import os
import requests
from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# log on page without posting
@app.route("/")
def index():
    message=None
    return render_template("index.html", message=message)

# registration page without posting
@app.route("/register/")
def register():
    message=None
    return render_template("register.html", message=message)

# registration action of posting
@app.route("/successregister/", methods=["POST"])
def successregister():
    nickname = request.form.get("user")
    password = request.form.get("password")
    name = request.form.get("name")
    password2 = request.form.get("password2")
    message = None
    if password!=password2:
        message = "Passwords do not match"
        return render_template("register.html", message=message)
    login = db.execute("SELECT username FROM users WHERE username = :nickname", {"nickname": nickname}).fetchone()
    if not login is None:
        message="User already registered"
        return render_template("register.html", message=message)
    db.execute("INSERT INTO users (username, password, name) VALUES (:nickname, :password, :name)", {"nickname": nickname, "password": password, "name": name})
    db.commit()
    return render_template("index.html", message=message)

#index page after hiting the log in button
@app.route("/successlogin/", methods=["POST"])
def success():
    login=request.form.get("user")
    message=None
    temp= db.execute("SELECT * FROM users WHERE username = :login", {"login": login}).fetchone()
    if temp is None:
        message="User not registered"
        return render_template("index.html", message=message)
    if temp.password != request.form.get("password"):
        message="Wrong Password"
        return render_template("index.html", message=message)
    session["user"]=temp.name
    session["id"]=temp.id
    return render_template("welcome.html", nome=session.get("user"))

#logout action - exiting the current session
@app.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("id", None)
    message=None
    return render_template("index.html", message=message)

#First page after logon with a search field
@app.route("/welcome/")
def welcome():
    return render_template("welcome.html", nome=str(session.get("user")))

#Results of search made on the Welcome page
@app.route("/results/", methods=["POST"])
def results():
    teste = request.form.get("search")
    book_id=teste.lower()
    fake = (f"%{book_id}%")
    books = db.execute("SELECT * FROM books WHERE lower(author) LIKE :book_id",
                            {"book_id":fake}).fetchall()
    books += db.execute("SELECT * FROM books WHERE lower(title) LIKE :book_id",
                            {"book_id":fake}).fetchall()
    books += db.execute("SELECT * FROM books WHERE lower(isbn) LIKE :book_id",
                            {"book_id":fake}).fetchall()
    books += db.execute("SELECT * FROM books WHERE CAST(id AS TEXT) LIKE :book_id",
                            {"book_id":fake}).fetchall()
    return render_template("results.html", books=books, nome=str(session.get("user")))

#this is a mokup if there is no book search made
@app.route("/details/")
def details():
    return render_template("welcome.html")

#this is the detail page of a given book
@app.route("/details/<int:book_id>")
def detail(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    result = db.execute("SELECT CAST(AVG(rating) AS DECIMAL(10,1)) FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    for i in result:
        avrating= i[0]
    reviews = db.execute ("SELECT * FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    participant=int(session.get("id"))
    already = None
    already = db.execute("SELECT user_id FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id AND user_id = :user_id", {"book_id": book_id, "user_id" : participant}).fetchone()
    message = "Thank you for reviewing this book!"
    isbn = book.isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jLA4R2uohX8mDRCj7lKg", "isbns": isbn})
    data = res.json()
    for b in data['books']:
        rgoodreads=b['average_rating']
        ngoodreads=b['work_ratings_count']
    return render_template("details.html", book=book, rating=avrating, reviews = reviews, message=message, rgoodreads=rgoodreads, ngoodreads=ngoodreads, already=already, nome=str(session.get("user")))

#this is the action of posting a review for a book
@app.route("/details/<int:book_id>/review", methods=["POST"])
def review(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    text = request.form.get("text")
    nota = request.form.get("nota")
    id = session.get("id")
    db.execute("INSERT INTO reviews (rating, moment, comment, book_id, user_id) VALUES (:rating, (SELECT CURRENT_TIMESTAMP), :comment, :book_id, :user_id)",
            {"rating": nota, "comment": text, "book_id": book_id, "user_id":id})
    db.commit()
    result = db.execute("SELECT CAST(AVG(rating) AS DECIMAL(10,1)) FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    for i in result:
        avrating= i[0]
    reviews = db.execute ("SELECT * FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    participant=int(session.get("id"))
    already = None
    already = db.execute("SELECT user_id FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id AND user_id = :user_id", {"book_id": book_id, "user_id" : participant}).fetchone()
    message = "Thank you for reviewing this book!"
    isbn = book.isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jLA4R2uohX8mDRCj7lKg", "isbns": isbn})
    data = res.json()
    for b in data['books']:
        rgoodreads=b['average_rating']
        ngoodreads=b['work_ratings_count']
    return render_template("details.html", book=book, rating=avrating, reviews = reviews, rgoodreads=rgoodreads, ngoodreads=ngoodreads, already = already, message = message, nome=str(session.get("user")))

#this is the api made to display information of a given book after called by it's isbn
@app.route("/api/<isbn>")
def api(isbn):
    #make sure book exists
    finder = db.execute("SELECT isbn FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    if finder is None:
        return jsonify({"error": "Book was not found in Bookfinder"}), 422
    #get book and reviews details
    apidetails = db.execute("SELECT * FROM books LEFT JOIN reviews ON books.id=reviews.book_id WHERE books.isbn = :isbn", {"isbn" :isbn}).fetchone()
    title = apidetails.title
    author = apidetails.author
    year = apidetails.year
    books = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
    book = books.id
    score = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :book_id", {"book_id" :book}).fetchall()
    for i in score:
        scoring= str(i[0])
    count = db.execute("SELECT COUNT(rating) FROM reviews WHERE book_id = :book_id", {"book_id":book}).fetchall()
    for i in count:
        counting= str(i[0])
    return jsonify({
        "title": title,
        "author": author,
        "year": year,
        "isbn": isbn,
        "review_count": counting,
        "average_score": scoring
        })
