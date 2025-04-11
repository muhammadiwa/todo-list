import sqlite3
from datetime import datetime
import hashlib
import models
from typing import List, Optional

class Database:
    def __init__(self, db_name="todo.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create checklists table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create checklist_items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checklist_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            is_completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (checklist_id) REFERENCES checklists (id)
        )
        ''')
        
        self.conn.commit()

    # User methods
    def get_db(self):
        return self.conn

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, user: models.UserCreate):
        cursor = self.conn.cursor()
        hashed_password = self.hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (user.username, user.email, hashed_password)
        )
        self.conn.commit()
        user_id = cursor.lastrowid
        return self.get_user_by_id(user_id)

    def get_user_by_id(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return models.User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                created_at=datetime.fromisoformat(user_data["created_at"])
            )
        return None

    def get_user_by_username(self, username: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return models.User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                created_at=datetime.fromisoformat(user_data["created_at"])
            )
        return None

    def get_user_by_email(self, email: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        if user_data:
            return models.User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                created_at=datetime.fromisoformat(user_data["created_at"])
            )
        return None

    def authenticate_user(self, username: str, password: str):
        cursor = self.conn.cursor()
        hashed_password = self.hash_password(password)
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        user_data = cursor.fetchone()
        if user_data:
            return models.User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                created_at=datetime.fromisoformat(user_data["created_at"])
            )
        return None

    # Checklist methods
    def create_checklist(self, checklist: models.ChecklistCreate, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO checklists (name, user_id) VALUES (?, ?)",
            (checklist.name, user_id)
        )
        self.conn.commit()
        checklist_id = cursor.lastrowid
        return self.get_checklist(checklist_id)

    def get_checklist(self, checklist_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM checklists WHERE id = ?", (checklist_id,))
        checklist_data = cursor.fetchone()
        if checklist_data:
            return models.Checklist(
                id=checklist_data["id"],
                name=checklist_data["name"],
                user_id=checklist_data["user_id"],
                created_at=datetime.fromisoformat(checklist_data["created_at"])
            )
        return None

    def get_checklists(self, user_id: int) -> List[models.Checklist]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM checklists WHERE user_id = ?", (user_id,))
        checklists_data = cursor.fetchall()
        return [
            models.Checklist(
                id=checklist["id"],
                name=checklist["name"],
                user_id=checklist["user_id"],
                created_at=datetime.fromisoformat(checklist["created_at"])
            )
            for checklist in checklists_data
        ]

    def delete_checklist(self, checklist_id: int):
        cursor = self.conn.cursor()
        # First delete all items in the checklist
        cursor.execute("DELETE FROM checklist_items WHERE checklist_id = ?", (checklist_id,))
        # Then delete the checklist
        cursor.execute("DELETE FROM checklists WHERE id = ?", (checklist_id,))
        self.conn.commit()

    # Checklist Item methods
    def create_checklist_item(self, checklist_id: int, item: models.ChecklistItemCreate):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO checklist_items (checklist_id, item_name) VALUES (?, ?)",
            (checklist_id, item.itemName)
        )
        self.conn.commit()
        item_id = cursor.lastrowid
        return self.get_checklist_item(item_id)

    def get_checklist_item(self, item_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM checklist_items WHERE id = ?", (item_id,))
        item_data = cursor.fetchone()
        if item_data:
            return models.ChecklistItem(
                id=item_data["id"],
                checklist_id=item_data["checklist_id"],
                itemName=item_data["item_name"],
                is_completed=bool(item_data["is_completed"]),
                created_at=datetime.fromisoformat(item_data["created_at"])
            )
        return None

    def get_checklist_items(self, checklist_id: int) -> List[models.ChecklistItem]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM checklist_items WHERE checklist_id = ?", (checklist_id,))
        items_data = cursor.fetchall()
        return [
            models.ChecklistItem(
                id=item["id"],
                checklist_id=item["checklist_id"],
                itemName=item["item_name"],
                is_completed=bool(item["is_completed"]),
                created_at=datetime.fromisoformat(item["created_at"])
            )
            for item in items_data
        ]

    def toggle_checklist_item_status(self, item_id: int):
        cursor = self.conn.cursor()
        item = self.get_checklist_item(item_id)
        if item:
            new_status = not item.is_completed
            cursor.execute(
                "UPDATE checklist_items SET is_completed = ? WHERE id = ?",
                (new_status, item_id)
            )
            self.conn.commit()
            return self.get_checklist_item(item_id)
        return None

    def rename_checklist_item(self, item_id: int, new_name: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE checklist_items SET item_name = ? WHERE id = ?",
            (new_name, item_id)
        )
        self.conn.commit()
        return self.get_checklist_item(item_id)

    def delete_checklist_item(self, item_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM checklist_items WHERE id = ?", (item_id,))
        self.conn.commit()

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.conn.close()
