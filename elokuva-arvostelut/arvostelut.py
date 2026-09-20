import db

def add_item(title, review, user_id):
    sql = """INSERT INTO reviews (title, review, user_id) VALUES (?, ?, ?)"""
    db.execute(sql, [title, review, user_id])

def get_items():
    sql = "SELECT id, title FROM reviews ORDER BY id DESC"
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT reviews.title, reviews.review, reviews.user_id, users.username
            FROM reviews, users
            WHERE reviews.user_id = users.id AND reviews.id = ?"""

    return db.query(sql, [item_id])[0]
    