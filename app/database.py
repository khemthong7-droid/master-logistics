import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base # ใช้ Relative Import เพื่อป้องกัน Error บน Render

# ดึงค่าจาก Environment หรือใช้ SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./master_logistic.db")

# แก้ไขหัวข้อสำหรับ PostgreSQL ของ Render
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# สร้าง Engine ให้รองรับทั้งสองระบบ
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()