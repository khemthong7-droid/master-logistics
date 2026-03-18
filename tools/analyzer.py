from sqlalchemy.orm import Session
from app import models

def get_business_stats(db: Session):
    open_jobs = db.query(models.Job).filter(models.Job.status == "Open").all()
    matched_tx = db.query(models.Transaction).filter(models.Transaction.type == "Job-Deduction").count()
    event_count = db.query(models.SystemEvent).count()
    
    return {
        "total_value": sum(j.price for j in open_jobs) if open_jobs else 0,
        "revenue": matched_tx * 50,
        "jobs_count": len(open_jobs),
        "telemetry_count": event_count
    }