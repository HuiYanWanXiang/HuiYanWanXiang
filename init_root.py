from database import SessionLocal
from models import User
from auth import hash_password

db = SessionLocal()

username = "root"
password = "12345678"

user = db.query(User).filter(User.username == username).first()
if not user:
    user = User(
        username=username,
        password_hash=hash_password(password),
        is_root=True,
        is_active=True,
        used_count=0,
        free_quota=999999999
    )
    db.add(user)
    db.commit()
    print("root 用户创建成功")
else:
    print("root 用户已存在")

db.close()