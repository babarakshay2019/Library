from rest_framework import serializers
from .models import Book, Author, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
    
    #save password in hashed format
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class FavoriteBooksSerializer(serializers.Serializer):
    book_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        user = validated_data['user']
        book_ids = validated_data['book_ids']
        books = Book.objects.filter(id__in=book_ids)

        if not books:
            raise serializers.ValidationError("No valid books found.")

        user.favorite_books.add(*books)
        return user