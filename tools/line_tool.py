import requests, json, os

def send_push(text: str):
    token = os.getenv("CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("USER_ID")
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": f"🛰️ MASGISTICS:\n{text}"}]}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.status_code