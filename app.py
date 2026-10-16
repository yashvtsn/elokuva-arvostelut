from flask import Flask
import sqlite3
from flask import abort, redirect, render_template, request, session, make_response
import config
import reviews
import users
import db

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



@app.route("/item/<int:review_id>")
def show_item(review_id):
    item = reviews.get_item(review_id)
    if not item:
        abort(404)

    classes = reviews.get_classes(review_id)
    comments = reviews.get_comments(review_id)
    images = reviews.get_images(review_id)

    return render_template(
        "show_item.html",
        item=item,
        classes=classes,
        comments=comments,
        images=images
    )

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = reviews.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/new_item")
def new_item():
    require_login()
    classes = reviews.get_all_classes()
    return render_template("new_item.html", classes = classes)

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

    all_classes = reviews.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        print("entry:", repr(entry))
        print("all_classes:", all_classes)

        if entry:
            class_title, class_value = entry.split(":", 1)
            class_title = class_title.strip()
            class_value = class_value.strip()

            if class_title not in all_classes:
                abort(403)

            if class_value not in all_classes[class_title]:
                abort(403)

            classes.append((class_title, class_value))

    reviews.add_item(title, review, user_id, classes)
    review_id = db.last_insert_id()

    return redirect("/item/" + str(review_id))


@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    comment = request.form["comment"].strip()
    if not comment or len(comment) > 1500:
        abort(403)

    review_id = request.form["review_id"]
    review = reviews.get_item(review_id)
    if not review:
        abort(403)
    user_id = session["user_id"]
    reviews.add_comment(review_id, user_id, comment)

    return redirect("/item/" + str(review_id))


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

    all_classes = reviews.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in reviews.get_classes(item_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_item.html", item=item, classes=classes, all_classes = all_classes)


@app.route("/images/<int:review_id>")
def edit_images(review_id):
    require_login()

    review = reviews.get_item(review_id)
    if not review:
        abort(404)

    if review["user_id"] != session["user_id"]:
        abort(403)

    images = reviews.get_images(review_id)

    return render_template(
        "images.html", review=review, images=images)


@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()

    review_id = request.form["review_id"]
    review = reviews.get_item(review_id)
    if not review: 
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith(".jpg"):
        return "VIRHE: väärä tiedostomuoto"

    image = file.read()
    if len(image) > 100 * 1024:
        return "VIRHE: liian suuri kuva"

    reviews.add_image(review_id, image)
    return redirect("/images/" + str(review_id))


@app.route("/remove_image", methods=["POST"])
def remove_image():
    require_login()

    review_id = request.form["review_id"]
    review = reviews.get_item(review_id)
    if not review: 
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
      reviews.remove_image(review_id, image_id)  

    return redirect("/images/" + str(review_id))

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

    classes = []
    all_classes = reviews.get_all_classes()
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes: 
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    reviews.update_item(item_id, title, review, classes)

    return redirect("/item/" + item_id)

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_id = users.check_login(username, password)
        if user_id:
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