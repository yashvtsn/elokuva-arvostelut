from flask import Flask
import sqlite3
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import arvostelut

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_items = arvostelut.get_items()
    return render_template("index.html", items = all_items)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = arvostelut.get_item(item_id)
    return render_template("show_item.html", item=item)

@app.route("/new_item")
def new_item():
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    title = request.form["title"]
    review = request.form["review"]
    user_id = session["user_id"]

    arvostelut.add_item(title, review, user_id)

    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    item = arvostelut.get_item(item_id)
    return render_template("edit_item.html", item=item)

@app.route("/remove_item/<int:item_id>")
def remove_item(item_id):
    arvostelut.remove_item(item_id)
    return redirect("/")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/update_item", methods=["POST"])
def update_item():
    item_id = request.form["item_id"]
    title = request.form["title"]
    review = request.form["review"]

    arvostelut.update_item(item_id, title, review)

    return redirect("/item/" + item_id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
            
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]
        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")