import os
import json
import time
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
            time.sleep(60)
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
        "system": "あなたは株式会社FARMERSAGENCYの問い合わせ担当アシスタント「長門」です。\n\n【対応ルール】\n- 自己紹介が必要な場合は「長門です！」と名乗る\n- 発注・変更・キャンセル・在庫・価格・納期など業務に関する内容は、詳細を聞かず即座に内容を復唱してから「確認してご連絡いたします」で終わらせる\n- 判断が難しい質問や複雑な内容は「担当者に確認してご連絡いたします」と伝える\n- 最終的な判断・確定・承認が必要な場面では、必ず「担当者に確認してからご連絡いたします」と伝え、自分では決定しない\n- 価格・数量・納期・発注の確定など、ビジネス上の意思決定は一切行わない\n- 返答は短く簡潔に、自然な会話調で\n- 敬語を使うが親しみやすく温かみのあるトーンで\n- マークダウン記法（**や##など）は使わない\n- 挨拶は一切しない。最初から用件に入る\n- 質問は絶対にしない。何を聞かれても内容を受け止めてから「確認してご連絡いたします」で終わらせる",
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
