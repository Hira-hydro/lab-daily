from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    clock_in = db.Column(db.String(20))
    clock_out = db.Column(db.String(20))
    note = db.Column(db.Text)
