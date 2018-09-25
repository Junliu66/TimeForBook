import uuid
from src.database import Database
from src.review import Review


class Book(object):
    def __init__(self, author, book_name, author_id, _id=None):
        self.author = author
        self.book_name = book_name
        self.author_id = author_id
        self._id = uuid.uuid4().hex if _id is None else _id

    def new_review(self, title, content):
        review = Review(book_id=self._id,
                        title=title,
                        content=content,
                        author=self.author)
        review.save_to_mongo()

    def get_reviews(self):
        return Review.from_book(self._id)

    def save_to_mongo(self):
        Database.insert(collection='books', data=self.json())

    def json(self):
        return {
            "author": self.author,
            "author_id": self.author_id,
            "book_name": self.book_name,
            "_id": self._id
        }

    @classmethod
    def from_mongo(cls, id):
        book_data = Database.find_one(collection='books', query={'_id': id})
        return cls(**book_data)

    @classmethod
    def find_by_author_id(cls, author_id):
        books = Database.find(collection='books', query={'author_id': author_id})
        return [cls(**book) for book in books]
