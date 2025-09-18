from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ユーザー情報
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), default="user")  # "admin" or "user"
    theme = db.Column(db.String(20), default="light")

    records = db.relationship("Record", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

# 出退勤・日誌
class Record(db.Model):
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    clock_in = db.Column(db.DateTime, nullable=True)
    clock_out = db.Column(db.DateTime, nullable=True)
    note = db.Column(db.Text, nullable=True)
    client_ip = db.Column(db.String(45))  # IPv4/IPv6対応

    def __repr__(self):
        return f"<Record {self.user_id} {self.date}>"
    
# アクセスログ
class AccessLog(db.Model):
    __tablename__ = "access_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv4/IPv6対応
    action = db.Column(db.String(50))      # "login", "logout" など

    user = db.relationship("User", backref="logs")

