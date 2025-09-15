from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from models import db, Record

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab_daily.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        today = datetime.now().date()
        record = Record.query.filter_by(date=today).first()

        if not record:
            record = Record(date=today)
            db.session.add(record)

        if action == "clock_in":
            record.clock_in = datetime.now().strftime("%H:%M:%S")
        elif action == "clock_out":
            record.clock_out = datetime.now().strftime("%H:%M:%S")
        elif action == "save_note":
            record.note = request.form.get("note")

        db.session.commit()
        return redirect(url_for("index"))

    today = datetime.now().date()
    record = Record.query.filter_by(date=today).first()
    return render_template("index.html", record=record)


@app.route("/records")
def records():
    all_records = Record.query.order_by(Record.date.desc()).all()
    return render_template("records.html", records=all_records)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
