# Workflow: Deploy New Payload
1. รับข้อมูล Title, Origin, Destination, Price, TruckType จาก Admin
2. บันทึกข้อมูลลง Database (Job status = 'Open')
3. เรียกใช้ Tool: `tools/notifier.py` เพื่อแจ้งเตือน CEO ทาง LINE
4. บันทึก Telemetry: 'payload_deployed'