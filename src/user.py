from flask import session
from src.database import Database
from src.book import Book
import uuid


class User(object):
    def __init__(self, name, email, password, _id=None):
        self.name = name
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_name(cls, email):
        user = User.get_by_email(email)
        if user is not None:
            return user.name

    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        return False

    @classmethod
    def register(cls, name, email, password):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(name, email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def get_books(self):
        return Book.find_by_author_id(self._id)

    def new_book(self, book_name):
        book = Book(author=self.email,
                    book_name=book_name,
                    author_id=self._id)
        book.save_to_mongo()

    @staticmethod
    def new_review(book_id, title, content):
        book = Book.from_mongo(book_id)
        book.new_review(title=title,
                        content=content)

    def json(self):
        return {
            "name": self.name,
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
