import db

def add_item(title, review, user_id):
    sql = """INSERT INTO reviews (title, review, user_id) VALUES (?, ?, ?)"""
    db.execute(sql, [title, review, user_id])

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

    return db.query(sql, [item_id])[0]

def update_item(item_id, title, review):
    sql = """UPDATE reviews
             SET title = ?, review = ?
             WHERE id = ?"""
    db.execute(sql, [title, review, item_id])

def remove_item(item_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [item_id])