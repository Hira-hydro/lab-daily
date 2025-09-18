from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Record, AccessLog
from datetime import datetime, date, timedelta

# Flaskアプリケーションの設定
app = Flask(__name__)
# 本番用
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab-diary.db"
# 開発用（コメントアウト解除して使用）
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab-diary-test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your-secret-key"  # 後で安全なキーに置き換える

db.init_app(app)

# Flask-Loginの設定
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# 管理者権限チェック用デコレーター
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#初期ページからログインページへリダイレクト
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))

# ログイン機能
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # アクセスログの記録
            ip = request.remote_addr
            log = AccessLog(user_id = user.id, ip_address=ip, action = "login")
            db.session.add(log)
            db.session.commit()

            flash("ログイン成功！", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("ユーザー名もしくはパスワードが間違っています", "danger")

    return render_template("login.html")

# ログアウト機能
@app.route("/logout")
@login_required
def logout():
    # アクセスログの記録
    ip = request.remote_addr
    log = AccessLog(user_id = current_user.id, ip_address=ip, action = "logout")
    db.session.add(log)
    db.session.commit()

    logout_user()
    flash("ログアウトしました","info")
    return redirect(url_for("login"))

# 出勤状況表示
@app.route("/attendance")
@login_required
def attendance():
    today =date.today()
    records = Record.query.filter(
        Record.clock_in != None,
        Record.clock_out == None
    ).all()

    return render_template("attendance.html",records=records)

# ダッシュボード
@app.route("/dashboard")
@login_required
def dashboard():
    # 今日の記録を取得
    today = datetime.utcnow().date()
    record = Record.query.filter_by(user_id=current_user.id, date=today).first()
    return render_template("dashboard.html", user=current_user, record=record)

# 出勤打刻
@app.route("/clock_in", methods=["POST"])
@login_required
def clock_in():
    today = datetime.utcnow().date()
    record = Record.query.filter_by(user_id=current_user.id, date=today).first()
    if not record:
        record =Record(user_id=current_user.id, date=today, clock_in=datetime.utcnow())
        db.session.add(record)
    else:
        record.clock_in = datetime.utcnow()
    db.session.commit()
    flash("出勤打刻を記録しました","success")
    return redirect(url_for("dashboard"))

# 退勤打刻
@app.route("/clock_out", methods=["POST"])
@login_required
def clock_out():
    today = datetime.utcnow().date()
    record = Record.query.filter_by(user_id=current_user.id, date=today).first()
    if record:
        record.clock_out = datetime.utcnow()
        db.session.commit()
        flash("退勤時刻を記録しました", "success")
    else:
        flash("出勤打刻がありません", "danger")
    return redirect(url_for("dashboard"))

# 日誌保存
@app.route("/save_note", methods=["POST"])
@login_required
def save_note():
    today = datetime.utcnow().date()
    note_text = request.form["note"]

    # 今日の記録を取得または新規作成
    record = Record.query.filter_by(user_id=current_user.id, date=today).first()
    if not record:
        record = Record(user_id=current_user.id, date=today, note=note_text)
        db.session.add(record)
    else:
        record.note = note_text
    db.session.commit()

    flash("日誌を保存しました","success")
    return redirect(url_for("dashboard"))

# 記録閲覧
@app.route("/records")
@login_required
def records():
    if current_user.role == "admin":
        all_records = Record.query.order_by(Record.date.desc()).all()
        return render_template("records.html", records=all_records, user=current_user, is_admin=True)
    else:
        user_records = Record.query.filter_by(user_id=current_user.id).order_by(Record.date.desc()).all()
        return render_template("records.html", records=user_records, user=current_user, is_admin=False)

# 記録編集（管理者のみ）
@app.route("/admin/edit_record/<int:record_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_record(record_id):
    record = Record.query.get_or_404(record_id)

    if request.method == "POST":
        clock_in = request.form.get("clock_in")
        clock_out = request.form.get("clock_out")
        note = request.form.get("note")

        if clock_in:
            record.clock_in = datetime.fromisoformat(clock_in)
        else:
            record.clock_in = None

        if clock_out:
            record.clock_out = datetime.fromisoformat(clock_out)
        else:
            record.clock_out = None

        record.note = note
        db.session.commit()
        flash("記録を更新しました", "success")
        return redirect(url_for("records"))
    return render_template("edit_record.html", record=record)

# 記録削除（管理者のみ）
@app.route("/records/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(record_id):
    if current_user.role != "admin":
        abort(403)

    record =Record.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash("記録を削除しました","info")
    return redirect(url_for("records"))

# 労働時間統計
@app.route("/weekly_stats")
@login_required
def weekly_stats():
    week_offset = int(request.args.get("week_offset", 0))
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
    start_of_week -= timedelta(days=7*week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    results = db.session.query(
        User.username,
        db.func.strftime("%w", Record.clock_in),
        db.func.sum(db.func.julianday(Record.clock_out) - db.func.julianday(Record.clock_in)) * 24
    ).join(Record).filter(
        Record.clock_in >= start_of_week,
        Record.clock_in <= end_of_week,
        Record.clock_out.isnot(None)
    ).group_by(User.username, db.func.strftime("%w", Record.clock_in)).all()

    users = {u.username: [0]*7 for u in User.query.all()}
    for username, weekday, hours in results:
        users[username][int(weekday)] = round(hours or 0, 2)

    return render_template("weekly_stats.html", users=users, start=start_of_week, end=end_of_week, week_offset=week_offset)

# ユーザー管理（管理者のみ）
@app.route("/admin/users", methods=["GET", "POST"])
@login_required
@admin_required
def manage_users():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form.get("role", "user")

        if User.query.filter_by(username=username).first():
            flash("そのユーザー名は既に存在します", "danger")
        else:
            new_user = User(username=username, password_hash=generate_password_hash(password), role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("ユーザーを追加しました", "success")
    users = User.query.all()
    return render_template("manage_users.html", users=users, user=current_user)

# ユーザー削除（管理者のみ）
@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("自分自身を削除することはできません", "danger")
        return redirect(url_for("manage_users"))
    
    db.session.delete(user)
    db.session.commit()
    flash(f"ユーザー {user.username} を削除しました", "info")
    return redirect(url_for("manage_users"))

# ユーザー権限変更（管理者のみ）
@app.route("/admin/toggle_role/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("自分自身の権限を変更することはできません", "danger")
        return redirect(url_for("manage_users"))
    
    user.role = "admin" if user.role == "user" else "user"
    db.session.commit()
    flash(f"ユーザー {user.username} の権限を {user.role} に変更しました", "info")
    return redirect(url_for("manage_users"))

# アクセスログ閲覧（管理者のみ）
@app.route("/admin/logs")
@login_required
@admin_required
def view_logs():
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(100).all()
    return render_template("logs.html", logs=logs)

# テーマ変更
@app.route("/settings/theme", methods=["GET","POST"])
@login_required
def change_theme():
    if request.method == "POST":
        theme = request.form["theme"]
        current_user.theme = theme
        db.session.commit()
        flash("テーマを変更しました", "success")
        return redirect(url_for("dashboard"))
    return render_template("change_theme.html", user=current_user)

# 管理者アカウント作成（初回のみ使用）
@app.route("/create_admin")
def create_admin():
    if User.query.filter_by(username="admin").first():
        return "すでに管理者がいます"
    admin = User(username="admin", password_hash=generate_password_hash("admin123"), role="admin")
    db.session.add(admin)
    db.session.commit()
    return "管理者アカウントが作成されました。ユーザ名: admin, パスワード: admin123"

with app.app_context():
    db.create_all()  # 初回だけテーブル作成

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
