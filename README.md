# Spotter.AI - Book Recommendation System

Spotter.AI is a book recommendation system API developed using Django REST Framework (DRF) with a cosine similarity algorithm. This project allows users to register, log in, create authors and books, update them, and receive book recommendations based on their favorite books.

## Features

- **User Authentication:** Register and log in with token-based authentication.
- **Author and Book Management:** Create, update, and retrieve authors and books.
- **Book Search:** Search for books by title.
- **Favorite Books:** Add and retrieve favorite books.
- **Book Recommendations:** Get recommended books based on your favorite books using cosine similarity.

## API Endpoints

Here are the available API routes:

### User Authentication

1. **User Registration**
   - Method: `POST`
   - URL: `/api/register/`
   - Description: Registers a new user.
   - Example: 
     ```bash
     curl -X POST http://127.0.0.1:8000/api/register/ -F 'username=test1234' -F 'password=Test@123'
     ```

2. **Login to Get Tokens**
   - Method: `POST`
   - URL: `/api/token/`
   - Description: Logs in a user and returns a token.
   - Example:
     ```bash
     curl -X POST http://127.0.0.1:8000/api/token/ -F 'username=test1234' -F 'password=Test@123'
     ```

### Author Management

1. **Create Author**
   - Method: `POST`
   - URL: `/api/authors/`
   - Description: Creates a new author.
   - Example:
     ```bash
     curl -X POST http://127.0.0.1:8000/api/authors/ -H 'Authorization: Bearer <your_token>' -F 'name=J K Rowling'
     ```

2. **Get Authors**
   - Method: `GET`
   - URL: `/api/authors/`
   - Description: Retrieves the list of all authors.
   - Example:
     ```bash
     curl -X GET http://127.0.0.1:8000/api/authors/
     ```

3. **Partially Update Author**
   - Method: `PATCH`
   - URL: `/api/authors/{id}/`
   - Description: Updates specific fields of an author.
   - Example:
     ```bash
     curl -X PATCH http://127.0.0.1:8000/api/authors/1/ -H 'Authorization: Bearer <your_token>' -F 'name=Ms.JK.Rowling'
     ```

### Book Management

1. **Create Book**
   - Method: `POST`
   - URL: `/api/books/`
   - Description: Creates a new book.
   - Example:
     ```bash
     curl -X POST http://127.0.0.1:8000/api/books/ -H 'Authorization: Bearer <your_token>' -F 'title=Harry potter 1' -F 'author=1' -F 'description=wizards book' -F 'published_date=2020-09-12'
     ```

2. **Get Books**
   - Method: `GET`
   - URL: `/api/books/`
   - Description: Retrieves the list of all books.
   - Example:
     ```bash
     curl -X GET http://127.0.0.1:8000/api/books/
     ```

3. **Get Single Book by ID**
   - Method: `GET`
   - URL: `/api/books/{id}/`
   - Description: Retrieves a book by its ID.
   - Example:
     ```bash
     curl -X GET http://127.0.0.1:8000/api/books/1/
     ```

4. **Partially Update Book**
   - Method: `PATCH`
   - URL: `/api/books/{id}/`
   - Description: Updates specific fields of a book.
   - Example:
     ```bash
     curl -X PATCH http://127.0.0.1:8000/api/books/1/ -H 'Authorization: Bearer <your_token>' -F 'description=wizards book reloaded'
     ```

### Book Search and Recommendations

1. **Search Books**
   - Method: `GET`
   - URL: `/api/books/?search={query}`
   - Description: Searches for books by title.
   - Example:
     ```bash
     curl -X GET http://127.0.0.1:8000/api/books/?search=harry
     ```

2. **Add Favorite Book**
   - Method: `POST`
   - URL: `/api/favorites/`
   - Description: Adds a book to the user's favorite list.
   - Example:
     ```bash
     curl -X POST http://127.0.0.1:8000/api/favorites/ -H 'Authorization: Bearer <your_token>' -F 'book_id=1'
     ```

3. **Get Recommended Books**
   - Method: `GET`
   - URL: `/api/recommendations/`
   - Description: Retrieves recommended books based on the user's favorite books.
   - Example:
     ```bash
     curl -X GET http://127.0.0.1:8000/api/recommendations/ -H 'Authorization: Bearer <your_token>'
     ```

## Project Setup

Follow these steps to set up the project locally:

### Prerequisites

- Python 3.x
- Django
- Django REST Framework
- PostgreSQL or SQLite (as per your configuration)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/spotter-ai.git
   cd spotter-ai

2. Create and Activate a Virtual Environment

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. Install the Required Packages:

    ```
    pip install -r requirements.txt
4. Apply migrations:

   ```bash
   python manage.py migrate
6. Run the Server

    Start the Django development server:
    ```bash
    python manage.py runserver
The server will be run at http://127.0.0.1:8000/.

### Command for creating model
This Command will create .h5 file for model which can be used for books recommendations:

```bash
python manage.py create_model
