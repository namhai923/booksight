import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
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
app.config["JSON_SORT_KEYS"] = False
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/login", methods=["POST","GET"])
def login():
    login_failed = False
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE username=:username AND password=:password", 
                    {"username":username, "password":password}).rowcount == 0:
            login_failed = True
        else:
            session["user"] = db.execute("SELECT * FROM users WHERE username=:username AND password=:password", 
                                {"username":username, "password":password}).fetchone()
            return redirect(url_for("main_page"))
    return render_template("login.html", login_failed=login_failed)

@app.route("/register", methods=["GET","POST"])
def register():
    valid_email = True
    valid_username = True
    register_success = False
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        if db.execute("SELECT * FROM users WHERE username=:username",
                        {"username":username}).rowcount != 0:
            valid_username = False
        if db.execute("SELECT * FROM users WHERE email=:email",
                        {"email":email}).rowcount != 0:
            valid_email = False
        if valid_username and valid_email:
            db.execute("INSERT INTO users(username, password, email) VALUES (:username, :password, :email)",
                        {"username":username, "password":password, "email":email})
            register_success = True
            db.commit()
    return render_template("register.html", valid_email=valid_email, valid_username=valid_username, 
                            register_success=register_success)

@app.route("/", methods=["POST", "GET"])
def main_page():
    if "user" in session:
        if request.method == "POST":
            search_content = request.form.get("search_content")
            result = db.execute("SELECT * FROM books WHERE UPPER(isbn) LIKE (:search) OR UPPER(title) LIKE (:search) OR UPPER(author) LIKE (:search)",
                                    {"search":"%"+search_content.upper()+"%"}).fetchall()
            if not result:
                return render_template("home.html", username=session["user"].username, result="failed")
            else:
                return render_template("home.html", username=session["user"].username, result=result)
        else:
            return render_template("home.html", username=session["user"].username, result=[])
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/<int:book_id>", methods=["GET","POST"])
def content(book_id):
    book_content = db.execute("SELECT * FROM books WHERE id=:id", {"id":book_id}).fetchone()
    book_reviews = db.execute("SELECT * FROM reviews JOIN users ON reviews.user_id=users.id WHERE book_id=:book_id", 
                                {"book_id":book_id}).fetchall()
    if request.method == "POST":
        if db.execute("SELECT * FROM reviews WHERE user_id=:user_id AND book_id=:book_id", 
                    {"user_id":session["user"].id, "book_id":book_id}).rowcount ==0:
            review = request.form.get("review")
            score = request.form.get("score")
            if score == None:
                score = 0
            else:
                score = int(score)
            if review == "":
                review = "No review"
            db.execute("INSERT INTO reviews(user_id, score, review, book_id) VALUES (:user_id, :score, :review, :book_id)", 
                        {"user_id":session["user"].id, "score":score, "review":review, "book_id":book_id})
            db.commit()
    return render_template("book_content.html", book_content=book_content, book_reviews=book_reviews)

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    if db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).rowcount == 0:
        return jsonify({"error": "invalid isbn"}), 404
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "fqWrv7MdZM611uha59Ovlg", "isbns": isbn})
    data = res.json()
    book_info = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
    return jsonify({
        "title": book_info.title,
        "author": book_info.author,
        "year": book_info.year,
        "isbn": book_info.isbn,
        "review_count": data['books'][0]['reviews_count'],
        "average_score": data['books'][0]['average_rating']
    })