import os

from flask import Flask, render_template, request, session, make_response, url_for

from src.database import Database
from src.book import Book
from src.user import User

app = Flask(__name__)
app.secret_key = "jose"


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/')
def home_template():
    return render_template('home.html')


@app.route('/login')
def login_template():
    return render_template('login.html')


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email, password):
        User.login(email)
    else:
        session['email'] = None
        return render_template('login.html')

    return render_template("profile.html", name=User.get_name(email), email=session['email'])


@app.route('/auth/register', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    User.register(name, email, password)

    return render_template("profile.html", name=name, email=session['email'])


@app.route('/books/<string:user_id>')
@app.route('/books')
def user_books(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])

    books = user.get_books()

    return render_template("user_books.html", books=books, email=user.email)


@app.route('/reviews/<string:book_id>')
def book_reviews(blog_id):
    book = Book.from_mongo(blog_id)
    reviews = book.get_reviews()

    return render_template('reviews.html', reviews=reviews, book_name=book.name, book_id=book._id)


@app.route('/books/new', methods=['POST', 'GET'])
def create_new_book():
    if request.method == 'GET':
        return render_template('new_book.html')
    else:
        book_name = request.form['book_name']
        user = User.get_by_email(session['email'])

        new_book = Book(user.email, book_name, user._id)
        new_book.save_to_mongo()

        return make_response(user_books(user._id))


@app.route('/reviews/new/<string:book_id>', methods=['POST', 'GET'])
def create_new_review(book_id):
    if request.method == 'GET':
        return render_template('new_review.html')
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])

        new_review = Book(book_id, title, content, user.email)
        new_review.save_to_mongo()

        return make_response(book_reviews(book_id))


if __name__ == '__main__':
    app.run(port=4998, debug=True)