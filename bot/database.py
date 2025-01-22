import sqlite3


class Database:
    DB_NAME = 'requests.db'

    @staticmethod
    def connect():
        return sqlite3.connect(Database.DB_NAME, check_same_thread=False)

    @staticmethod
    def initialize():
        conn = Database.connect()
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS deliveries")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT, -- 'передать' или 'отвезти'
            item TEXT,
            city_from TEXT,
            city_to TEXT,
            user_id INTEGER,
            username TEXT,
            is_notified INTEGER DEFAULT 0 -- 0 означает, что уведомление не отправлено
        )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def insert_delivery(action, item, city_from, city_to, user_id, username):
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO deliveries (action, item, city_from, city_to, user_id, username)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (action, item, city_from, city_to, user_id, username))
        conn.commit()
        conn.close()

    @staticmethod
    def fetch_all_deliveries():
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT item, city_from, city_to, username FROM deliveries")
        results = cursor.fetchall()
        conn.close()
        return results

    @staticmethod
    def clear_deliveries():
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM deliveries")
        conn.commit()
        conn.close()


Database.initialize()
