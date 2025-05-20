import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    published_at TEXT
                )
            """)
            conn.commit()

    def article_exists(self, url):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
            return cursor.fetchone() is not None

    def save_article(self, url, title, source, published_at):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO articles (url, title, source, published_at) VALUES (?, ?, ?, ?)",
                (url, title, source, published_at)
            )
            conn.commit()
