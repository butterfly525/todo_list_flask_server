from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id} - {self.username}>"
    
    # Метод для конвертации задачи в словарь (для API)
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "text": self.text,
            "completed": self.completed,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password