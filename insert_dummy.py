from app import db, app, User, Record
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

with app.app_context():
    db.drop_all()   # 既存テーブル削除（安全なら残してOK）
    db.create_all() # 新規作成

    # ユーザー作成
    admin = User(username="admin", password_hash=generate_password_hash("admin123"), role="admin")
    alice = User(username="alice", password_hash=generate_password_hash("test123"))
    bob = User(username="bob", password_hash=generate_password_hash("test123"))
    charlie = User(username="charlie", password_hash=generate_password_hash("test123"))

    db.session.add_all([admin, alice, bob, charlie])
    db.session.commit()

    # ダミー日誌内容
    notes = ["実験A", "解析B", "打ち合わせ", "資料作成", "装置メンテ", "論文執筆"]

    today = datetime.utcnow().date()
    users = [alice, bob, charlie]

    # 過去7日分のレコード生成
    for u in users:
        for i in range(7):
            date = today - timedelta(days=i)
            start_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=9, minutes=random.randint(-30, 30))
            duration = timedelta(hours=random.randint(6, 9))
            end_time = start_time + duration
            note = random.choice(notes)

            record = Record(
                user_id=u.id,
                clock_in=start_time,
                clock_out=end_time,
                note=note,
                client_ip="127.0.0.1"
            )
            db.session.add(record)

    db.session.commit()
    print("✅ ダミーデータ挿入完了！")
