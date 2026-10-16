import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def add_item(title, review, user_id, classes):
    sql = """INSERT INTO reviews (title, review, user_id) VALUES (?, ?, ?)"""
    db.execute(sql, [title, review, user_id])

    review_id = db.last_insert_id()


    sql = "INSERT INTO reviews_classes (review_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [review_id, title, value])

def add_comment(review_id, user_id, comment):
    sql = """INSERT INTO comments (review_id, user_id, review_text)
             VALUES (?, ?, ?)"""
    db.execute(sql, [review_id, user_id, comment])


def get_images(review_id):
    sql = "SELECT id FROM images WHERE review_id = ?"
    return db.query(sql, [review_id])


def add_image(review_id, image):
    sql = """
        INSERT INTO images (review_id, image)
        VALUES (?, ?)
    """
    db.execute(sql, [review_id, image])

def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(review_id, image_id):
    sql = "DELETE FROM images WHERE id = ? AND review_id = ?"
    db.execute(sql, [image_id, review_id])


def get_comments(review_id):
    sql = """
        SELECT comments.review_text, comments.user_id, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.review_id = ?
        ORDER BY comments.id
    """
    result = db.query(sql, [review_id])
    return result


def get_classes(review_id):
    sql = "SELECT title, value FROM reviews_classes WHERE review_id = ?"
    return db.query(sql, [review_id])

def get_items():
    sql = """
        SELECT reviews.id, reviews.title, reviews.review,
               reviews.user_id, users.username, COUNT(comments.id) comments_count
        FROM reviews
        JOIN users ON reviews.user_id = users.id
        LEFT JOIN comments ON reviews.id = comments.review_id
        GROUP BY reviews.id
        ORDER BY reviews.id DESC
    """
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT reviews.id,
                    reviews.title,
                    reviews.review,
                    reviews.user_id,
                    users.id AS author_id,
                    users.username
             FROM reviews, users
             WHERE reviews.user_id = users.id
               AND reviews.id = ?"""

    result = db.query(sql, [item_id])
    return result[0] if result else None

def update_item(review_id, title, review, classes):
    sql = """UPDATE reviews
             SET title = ?, review = ?
             WHERE id = ?"""
    db.execute(sql, [title, review, review_id])

    sql = "DELETE FROM reviews_classes WHERE review_id = ?"
    db.execute(sql, [review_id])

    sql = "INSERT INTO reviews_classes (review_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [review_id, title, value])

def remove_item(item_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query): 
    sql = """SELECT id, title 
             FROM reviews 
             WHERE title LIKE ? OR review LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])

