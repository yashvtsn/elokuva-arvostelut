from flask import Flask
import sqlite3
from flask import abort, redirect, render_template, request, session, make_response, flash
import config
import reviews
import users
import secrets
import markupsafe

app = Flask(__name__)
app.secret_key = config.secret_key
 
 
def require_login():
    if "user_id" not in session:
        abort(403)
 
 
def check_csrf():
    token = session.get("csrf_token")
    if not token or request.form.get("csrf_token") != token:
        abort(403)
 
 
def get_own_item(item_id):
    """Return the review if it exists and belongs to the logged-in user."""
    require_login()
    item = reviews.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)
    return item
 
 
def read_item_form():
    errors = []
    title = request.form.get("title", "").strip()
    review = request.form.get("review", "").strip()
    if not title:
        errors.append("VIRHE: otsikko puuttuu")
    elif len(title) > 50:
        errors.append("VIRHE: otsikko on liian pitkä")
    if not review:
        errors.append("VIRHE: arvostelu puuttuu")
    elif len(review) > 1500:
        errors.append("VIRHE: arvostelu on liian pitkä")
 
    all_classes = reviews.get_all_classes()
    classes = []
    for entry in request.form.getlist("classes"):
        if not entry:
            continue
        class_title, _, class_value = entry.partition(":")
        class_title = class_title.strip()
        class_value = class_value.strip()
        if (class_title not in all_classes
                or class_value not in all_classes[class_title]):
            errors.append("VIRHE: virheellinen luokittelu")
            break
        classes.append((class_title, class_value))
    return title, review, classes, errors
 
 
@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)
 
 
@app.route("/")
def index():
    all_items = reviews.get_items()
    return render_template("index.html", items=all_items)
 
 
@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_reviews = users.get_reviews(user_id)
    return render_template("show_user.html", user=user,
                           reviews=user_reviews)
 
 
@app.route("/find_item")
def find_item():
    query = request.args.get("query", "").strip()
    results = reviews.find_items(query) if query else []
    return render_template("find_item.html", query=query, results=results)
 
 
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
    return render_template("new_item.html", classes=classes)
 
 
@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    check_csrf()
    title, review, classes, errors = read_item_form()
    if errors:
        for error in errors:
            flash(error)
        return redirect("/new_item")
    review_id = reviews.add_item(title, review, session["user_id"], classes)
    return redirect(f"/item/{review_id}")
 
 
@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    comment = request.form.get("comment", "").strip()
    review_id = request.form.get("review_id", type=int)
    review = reviews.get_item(review_id)
    if not review:
        abort(404)
    if not comment:
        flash("VIRHE: kommentti puuttuu")
        return redirect(f"/item/{review_id}")
    if len(comment) > 1500:
        flash("VIRHE: kommentti on liian pitkä")
        return redirect(f"/item/{review_id}")

    reviews.add_comment(review_id, session["user_id"], comment)
    return redirect(f"/item/{review_id}")
 
 
@app.route("/register")
def register():
    return render_template("register.html")
 
 
@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    item = get_own_item(item_id)
 
    all_classes = reviews.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in reviews.get_classes(item_id):
        classes[entry["title"]] = entry["value"]
 
    return render_template("edit_item.html", item=item, classes=classes,
                           all_classes=all_classes)
 
 
@app.route("/images/<int:review_id>")
def edit_images(review_id):
    review = get_own_item(review_id)
    images = reviews.get_images(review_id)
    return render_template("images.html", review=review, images=images)
 
 
@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()
    review_id = request.form.get("review_id", type=int)
    get_own_item(review_id)
 
    file = request.files.get("image")
    if not file or not file.filename.lower().endswith(".jpg"):
        flash("VIRHE: väärä tiedostomuoto")
        return redirect(f"/images/{review_id}")
 
    image = file.read()
    if len(image) > 100 * 1024:
        flash("VIRHE: liian suuri kuva")
        return redirect(f"/images/{review_id}")
 
    reviews.add_image(review_id, image)
    return redirect(f"/images/{review_id}")
 
 
@app.route("/remove_image", methods=["POST"])
def remove_image():
    require_login()
    check_csrf()
    review_id = request.form.get("review_id", type=int)
    get_own_item(review_id)
 
    for image_id in request.form.getlist("image_id"):
        reviews.remove_image(review_id, image_id)
 
    return redirect(f"/images/{review_id}")
 
 
@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    item = get_own_item(item_id)
 
    if request.method == "GET":
        return render_template("remove_item.html", item=item)
 
    check_csrf()
    if "remove" in request.form:
        reviews.remove_item(item_id)
        return redirect("/")
    return redirect(f"/item/{item_id}")
 
 
@app.route("/update_item", methods=["POST"])
def update_item():
    require_login()
    check_csrf()
    item_id = request.form.get("item_id", type=int)
    get_own_item(item_id)
 
    title, review, classes, errors = read_item_form()
    if errors:
        for error in errors:
            flash(error)
        return redirect(f"/edit_item/{item_id}")
    reviews.update_item(item_id, title, review, classes)
    return redirect(f"/item/{item_id}")
 
 
@app.route("/create", methods=["POST"])
def create():
    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")
 
    errors = []
    if not 3 <= len(username) <= 20:
        errors.append("VIRHE: tunnuksen pituus on 3-20 merkkiä")
    if not 8 <= len(password1) <= 100:
        errors.append("VIRHE: salasanan pituus on 8-100 merkkiä")
    if password1 != password2:
        errors.append("VIRHE: salasanat eivät ole samat")
    if not errors:
        try:
            users.create_user(username, password1)
        except sqlite3.IntegrityError:
            errors.append("VIRHE: tunnus on jo varattu")
 
    if errors:
        for error in errors:
            flash(error)
        return redirect("/register")
    flash("Tunnus luotu, voit nyt kirjautua sisään")
    return redirect("/login")
 
 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
 
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    user_id = users.check_login(username, password)
    if not user_id:
        flash("VIRHE: väärä tunnus tai salasana")
        return redirect("/login")
 
    session.clear()
    session["user_id"] = user_id
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    return redirect("/")
 
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
 
 
@app.errorhandler(403)
def forbidden(error):
    return render_template("error.html", message="Ei oikeutta."), 403
 
 
@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Sivua ei löytynyt."), 404
