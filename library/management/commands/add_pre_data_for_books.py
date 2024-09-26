from django.core.management.base import BaseCommand
from ...models import Author, Book
import json
import datetime

class Command(BaseCommand):
    help = 'Adds pre-defined data to YourModel'

    def handle(self, *args, **kwargs):
        count = 0
        with open("books.json", 'r') as file:
            for line in file:
                if count == 1000:
                    break
                data = json.loads(line)
                author = Author.objects.filter(name=data.get("author_name"))
                if author:
                    Book.objects.create(
                        title=data.get("title"), 
                        author=author[0], 
                        description=data.get("description"), 
                        published_date=datetime.datetime.now()
                    )
                    count += 1

        self.stdout.write(self.style.SUCCESS('Pre-data added successfully'))
