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

def get_classes(review_id):
    sql = "SELECT title, value FROM reviews_classes WHERE review_id = ?"
    return db.query(sql, [review_id])

def get_items():
    sql = "SELECT id, title FROM reviews ORDER BY id DESC"
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

