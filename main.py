import os
import json
from flask import Flask, request
import requests

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data(as_text=True)
    events = json.loads(body)["events"]
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            reply_token = event["replyToken"]
            user_message = event["message"]["text"]
            ai_response = ask_claude(user_message)
            reply_message(reply_token, ai_response)
    return "OK"

def ask_claude(text):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "system": "あなたは野菜の仕入れ代理店のアシスタントです。農家さんからの在庫確認や発注に丁寧な日本語で対応してください。",
        "messages": [{"role": "user", "content": text}]
    }
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    result = res.json()
    return result["content"][0]["text"]

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
