import requests, json, os
from dotenv import load_dotenv

load_dotenv() # โหลดค่าจาก .env

def send_line(text: str):
    token = os.getenv("CHANNEL_ACCESS_TOKEN")
    uid = os.getenv("USER_ID")
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": uid, "messages": [{"type": "text", "text": f"🛰️ MASGISTICS REPORT:\n{text}"}]}
    try:
        requests.post(url, headers=headers, data=json.dumps(payload))
        return True
    except:
        return False