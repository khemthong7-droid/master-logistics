# Workflow: Personnel Onboarding
**Objective:** ลงทะเบียนผู้ใช้ใหม่และแจ้งเตือนเข้าศูนย์ควบคุม

## Steps:
1. รับข้อมูลจากฟอร์ม (Name, Phone, Role, Province)
2. บันทึกลงตาราง `users` ในฐานข้อมูล
3. เรียกใช้ `tools/line_tool.py` เพื่อแจ้งเตือน CEO
4. บันทึก Telemetry Event `user_registered`

## Edge Cases:
- ถ้าเบอร์โทรซ้ำ: แจ้งเตือนข้อผิดพลาด
- ถ้าส่ง LINE ไม่สำเร็จ: ให้บันทึก Log แต่ไม่ต้องหยุดการทำงาน