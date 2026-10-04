from flask import Flask
import sqlite3
from flask import abort, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import reviews
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_items = reviews.get_items()
    return render_template("index.html", items = all_items)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user: 
        abort(404)
    reviews = users.get_reviews(user_id)
    return render_template("show_user.html", user=user, reviews=reviews)

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = reviews.find_items(query)
    else:    
        query = ""
        results = []
    return render_template("find_item.html", query=query, results = results)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = reviews.get_item(item_id)
    if not item: 
        abort(404)
    return render_template("show_item.html", item=item)

@app.route("/new_item")
def new_item():
    require_login()

    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    review = request.form["review"]
    if not review or len(review) > 1500:
        abort(403)
    user_id = session["user_id"]

    reviews.add_item(title, review, user_id)

    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()

    item = reviews.get_item(item_id)
    if not item: 
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    
    return render_template("edit_item.html", item=item)

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    require_login()

    item = reviews.get_item(item_id)
    if not item: 
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        item = reviews.get_item(item_id)
        return render_template("remove_item.html", item=item)
    if request.method == "POST":
        if "remove" in request.form:
            reviews.remove_item(item_id)
            return redirect("/")
        else: 
            return redirect("/item/" + str(item_id))

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
    item = reviews.get_item(item_id)
    if not item: 
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    review = request.form["review"]
    if not review or len(review) > 1500:
        abort(403)

    reviews.update_item(item_id, title, review)

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
    if "user_id" in session: 
        del session["username"]
        del session["user_id"]
    return redirect("/")