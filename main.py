import sys, os, json, uvicorn, requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# --- 🛰️ STEP 1: INFRASTRUCTURE ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import database, models
from tools import notifier, analyzer, safety_tool, profit_calc

load_dotenv()
database.init_db()

app = FastAPI(title="MASHUB")

if not os.path.exists("static"): os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

def is_authenticated(request: Request):
    return request.cookies.get("mas_session") == "authenticated"

# --- 🛸 STEP 2: ROUTES (Updated for Python 3.14 Compatibility) ---

@app.get("/")
def root(): return RedirectResponse(url="/profile")

@app.get("/profile", response_class=HTMLResponse)
def company_profile(request: Request):
    # ปรับ Syntax: ใช้ request=request, name="..."
    return templates.TemplateResponse(request=request, name="profile.html")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return HTMLResponse(content="""
        <html><body style='background:#050505;color:white;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;text-align:center;'>
            <form action='/login' method='post' style='background:rgba(255,255,255,0.05);padding:40px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);'>
                <h1 style='letter-spacing:5px;font-style:italic;'>MASHUB ACCESS</h1>
                <input type='password' name='password' placeholder='Authorization Code' style='padding:10px;width:100%;margin-top:20px;background:black;color:white;border:1px solid white;' required>
                <button type='submit' style='margin-top:20px;width:100%;padding:10px;background:white;color:black;font-weight:bold;'>INITIATE ACCESS</button>
            </form>
        </body></html>
    """)

@app.post("/login")
def process_login(response: Response, password: str = Form(...)):
    if password == os.getenv("ADMIN_PASSWORD", "masgistics2024"):
        res = RedirectResponse(url="/admin", status_code=303)
        res.set_cookie(key="mas_session", value="authenticated", httponly=True)
        return res
    return HTMLResponse("<h1 style='color:red;text-align:center;'>ACCESS DENIED</h1>")

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request): return RedirectResponse(url="/login")
    
    stats = analyzer.get_business_stats(db)
    users = db.query(models.User).all()
    open_jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    matched_jobs = db.query(models.Job).filter(models.Job.status == "Matched").all()
    view_events = db.query(models.SystemEvent).filter(models.SystemEvent.event_type == "view_payloads").count()

    # ปรับ Syntax: แยก context ออกมาส่งแบบ Keyword
    return templates.TemplateResponse(
        request=request, 
        name="admin.html", 
        context={
            "users": users, "jobs": open_jobs, "matched_jobs": matched_jobs,
            "jobs_count": stats["jobs_count"], "total_value": stats["total_value"], 
            "potential_revenue": stats["revenue"], "total_telemetry": stats["telemetry_count"],
            "verified_carriers": [u for u in users if u.is_verified], "view_count": view_events
        }
    )

@app.get("/payloads", response_class=HTMLResponse)
def public_jobs(request: Request, db: Session = Depends(get_db)):
    jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    for job in jobs:
        try: job.estimated_profit = profit_calc.estimate_profit(job.price)
        except: job.estimated_profit = 0
        
    return templates.TemplateResponse(
        request=request, 
        name="payloads.html", 
        context={"jobs": jobs, "line_link": "https://line.me/ti/p/@839wctaq"}
    )

@app.get("/join", response_class=HTMLResponse)
def join_page(request: Request): 
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/initiate-onboarding")
def initiate_onboarding(name: str = Form(...), phone: str = Form(...), user_role: str = Form(...), province: str = Form(...), db: Session = Depends(get_db)):
    new_user = models.User(full_name=name, phone=phone, role=user_role)
    db.add(new_user); db.commit()
    notifier.send_line(f"🆕 NEW PERSONNEL!\n👤 {name}\n🏷️ {user_role}\n📍 {province}")
    return HTMLResponse(content="<html><body style='background:#050505;color:#00ff41;display:flex;justify-content:center;align-items:center;height:100vh;text-align:center;'><div><h1>TRANSMISSION RECEIVED</h1><a href='/join' style='color:white;'>RETURN</a></div></body></html>")

@app.post("/admin/assign-job")
def assign_job(job_id: int = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    user, job = db.query(models.User).get(user_id), db.query(models.Job).get(job_id)
    if user and user.wallet_balance >= 50:
        user.wallet_balance -= 50; job.status = "Matched"
        db.add(models.Transaction(user_id=user.id, amount=-50, type="Job-Deduction")); db.commit()
        return RedirectResponse(url=f"/mission/{job_id}", status_code=303)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/topup/{user_id}")
def topup_wallet(user_id: int, amount: float = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user:
        user.wallet_balance += amount
        db.add(models.Transaction(user_id=user.id, amount=amount, type="Top-up")); db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/verify/{user_id}")
def verify_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user: user.is_verified = True; db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/add-job")
def add_job(title: str = Form(...), origin: str = Form(...), destination: str = Form(...), price: float = Form(...), truck_type: str = Form(...), db: Session = Depends(get_db)):
    db.add(models.Job(title=title, origin=origin, destination=destination, price=price, truck_type_required=truck_type, status="Open"))
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
