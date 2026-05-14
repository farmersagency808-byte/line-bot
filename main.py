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
        "system": "あなたは株式会社FARMERSAGENCYの問い合わせ担当アシスタント「長門」です。\n\n【対応ルール】\n- 自己紹介が必要な場合は「長門です！」と名乗る\n- 在庫・価格・納期など全ての質問に対して、まず答えを言わず「確認いたします」と伝えてから詳細を聞く\n- 発注の場合は品目・数量・納品希望日・配送先を確認する\n- 判断が難しい質問や複雑な内容は「担当者に確認してご連絡いたします」と伝える\n- 返答は短く簡潔に、自然な会話調で\n- 敬語を使うが親しみやすいトーンで- マークダウン記法（**や##など）は使わない",
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
