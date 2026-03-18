from sqlalchemy.orm import Session
from app import models

def calculate_business_metrics(db: Session):
    jobs = db.query(models.Job).all()
    open_jobs = [j for j in jobs if j.status == "Open"]
    matched_jobs = [j for j in jobs if j.status == "Matched"]
    
    total_value = sum(j.price for j in open_jobs) if open_jobs else 0
    actual_revenue = len(matched_jobs) * 50
    
    return {
        "total_value": total_value,
        "revenue": actual_revenue,
        "open_count": len(open_jobs)
    }