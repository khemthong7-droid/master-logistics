import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# เปลี่ยนจุดนี้: ให้ Import ตรงๆ จาก models ภายในโฟลเดอร์เดียวกัน
try:
    from app.models import Base
except ImportError:
    from models import Base
# ... (โค้ดส่วนที่เหลือ) ...

# ดึงค่าจาก .env หรือใช้ SQLite เป็นพื้นฐาน
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./master_logistic.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# สร้างเครื่องยนต์ฐานข้อมูล
if "postgresql" in DATABASE_URL:
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()