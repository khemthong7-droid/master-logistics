from datetime import datetime, timedelta, timezone

def check_pilot_fatigue(start_time_utc: datetime):
    """
    วิศวกรรมความปลอดภัย: 
    - ขับต่อเนื่องเกิน 4 ชม. ต้องพัก 30 นาที
    - ขับรวมเกิน 8 ชม. ต่อวัน ต้องหยุดพักยาว
    """
    now = datetime.now(timezone.utc)
    driving_duration = now - start_time_utc
    
    hours_driven = driving_duration.total_seconds() / 3600
    
    if hours_driven >= 4:
        return {"status": "REST_REQUIRED", "message": "🚨 ถึงเวลาพักผ่อน! กรุณาหยุดรถในจุดพักถัดไป 30 นาที"}
    elif hours_driven >= 3.5:
        return {"status": "CAUTION", "message": "⚠️ อีก 30 นาที จะถึงเวลาพักตามระเบียบความปลอดภัย"}
    else:
        return {"status": "NOMINAL", "message": "🟢 สภาพร่างกายพร้อมปฏิบัติหน้าที่"}