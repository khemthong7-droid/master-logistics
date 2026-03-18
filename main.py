import sys
import os

# บังคับให้ Python มองเห็นโฟลเดอร์ปัจจุบันเป็น Root
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from fastapi import FastAPI, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# ตอนนี้ Python จะมองเห็น app และ tools แล้ว
from app import database, models
from tools import notifier, analyzer 
from dotenv import load_dotenv
import json

# ... (โค้ดส่วนที่เหลือ) ...

# เริ่มต้นระบบ
load_dotenv()
database.init_db()
app = FastAPI(title="MASGISTICS - WAT Framework")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- ROUTES ต่อจากนี้เหมือนเดิม ---
@app.get("/")
def root(): return RedirectResponse(url="/profile")

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(database.get_db)):
    if request.cookies.get("mas_session") != "authenticated": return RedirectResponse(url="/login")
    stats = analyzer.get_business_stats(db)
    users = db.query(models.User).all()
    open_jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    matched_jobs = db.query(models.Job).filter(models.Job.status == "Matched").all()
    return templates.TemplateResponse("admin.html", {
        "request": request, "users": users, "jobs": open_jobs, "matched_jobs": matched_jobs,
        "jobs_count": stats["jobs_count"], "total_value": stats["total_value"], 
        "potential_revenue": stats["revenue"], "total_telemetry": stats["telemetry_count"],
        "verified_carriers": [u for u in users if u.is_verified]
    })

# ... (Route อื่นๆ ตามโค้ดล่าสุดของคุณ) ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)