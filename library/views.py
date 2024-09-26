from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Book, Author, User
from .serializers import BookSerializer, AuthorSerializer, UserSerializer, FavoriteBooksSerializer
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

import h5py
import numpy as np

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author__name']

    def get_permissions(self):
        """
        Checks if the user is authenticated if the HTTP method is POST, PUT, or DELETE.
        """
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authors to be viewed or edited.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        """
        Checks if the user is authenticated if the HTTP method is POST, PUT, or DELETE.
        """
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        Creates a new Author object.
        """
        if IsAuthenticated.has_permission(self, request, view=self):
            # Create the Author object
            author = Author.objects.create(**request.data)
            # Return the newly created Author object
            return Response(status=status.HTTP_201_CREATED, data=AuthorSerializer(author).data)
        # Return a 403 Forbidden response if the user is not authenticated
        return Response(status=status.HTTP_403_FORBIDDEN, data={'message': 'Permission denied'})

    
class RegisterView(generics.CreateAPIView):
    """
    API endpoint that allows users to be created.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new User object.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate a refresh token
        refresh = RefreshToken.for_user(user)

        # Return the newly created User object and the refresh token
        return Response(status=status.HTTP_201_CREATED, data={
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })


class FavoriteBooksListCreateView(generics.ListCreateAPIView):
    """
    API endpoint that allows users to get or add books to their favorites.

    GET /favorite_books/ - Returns a list of the user's favorite books.
    POST /favorite_books/ - Adds the specified book to the user's favorites.
    """
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns the authenticated user's favorite books.
        """
        user = self.request.user
        return user.favorite_books.all()

    def create(self, request, *args, **kwargs):
        """
        Adds the specified book to the user's favorites and returns a list of suggested books.
        """
        serializer = FavoriteBooksSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Get suggested books
        suggested_books = self.get_suggested_books(request.data.get('book_ids'))

        return Response({
            "detail": "Favorite books added successfully.",
            "suggested_books": suggested_books
        }, status=status.HTTP_201_CREATED)

    def get_suggested_books(self, id):
        """
        Returns a list of suggested books based on the user's favorite books.
        """
        if id is None:
            return []

        # Load the book recommendation model
        def load_similarity_model():
            """
            Loads the book recommendation model from a .h5 file.
            """
            with h5py.File("book_recommendation_model.h5", "r") as hf:
                asin_i = hf["asin_i"][:].astype(str)
                asin_j = hf["asin_j"][:].astype(str)
                similarities = hf["similarity"][:]
            return asin_i, asin_j, similarities

        asin_i, asin_j, similarities = load_similarity_model()

        # Get recommendations
        def get_recommendations(id, n=5):
            """
            Returns a list of up to n books that are similar to the book with the specified ID.
            """
            similar_books_dict = []
            for i in range(len(asin_i)):
                if asin_i[i] == id:
                    similar_books_dict.append(str(asin_j[i]))
            return similar_books_dict

        return get_recommendations(id, 5)

    def delete(self, request, *args, **kwargs):
        """
        Removes the specified book from the user's favorites.
        """
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"detail": "Book ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        favorite_books = user.favorite_books.filter(id=book_id)

        if favorite_books.exists():
            user.favorite_books.remove(favorite_books.first())
            return Response({"detail": "Book removed from favorites."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Book not found in favorites."}, status=status.HTTP_404_NOT_FOUND)
