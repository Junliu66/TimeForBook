import uuid
from src.database import Database


class Review(object):

    def __init__(self, book_id, title, content, author, _id=None):
        self.book_id = book_id
        self.title = title
        self.content = content
        self.author = author
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='reviews', data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'book_id': self.book_id,
            'author': self.author,
            'content': self.content,
            'title': self.title,
        }

    @classmethod
    def from_mongo(cls, id):
        review_data = Database.find_one(collection='reviews', query={'_id': id})
        return cls(**review_data)

    @staticmethod
    def from_book(id):
        return [review for review in Database.find('reviews', query={'book_id': id})]