import os
import json
from flask import Flask, request
import requests

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data(as_text=True)
    events = json.loads(body)["events"]
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            reply_token = event["replyToken"]
            user_message = event["message"]["text"]
            reply_message(reply_token, f"受け取りました：{user_message}")
    return "OK"

def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        json=data
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
