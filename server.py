from flask import Flask, request
import requests
import os
import base64

app = Flask(__name__)

ROUTINE_TOKEN = os.environ.get("ROUTINE_TOKEN")
ROUTINE_ID = os.environ.get("ROUTINE_ID")

@app.route("/", methods=["GET"])
def home():
    return "Gmail Webhook Server is running!", 200

@app.route("/gmail-webhook", methods=["POST"])
def gmail_webhook():
    try:
        envelope = request.get_json()
        if not envelope:
            return "No data received", 400

        pubsub_message = envelope.get("message", {})
        data = pubsub_message.get("data", "")
        
        if data:
            decoded = base64.b64decode(data).decode("utf-8")
            print(f"New email notification: {decoded}")

        response = requests.post(
            f"https://api.anthropic.com/v1/claude_code/routines/{ROUTINE_ID}/fire",
            headers={
                "Authorization": f"Bearer {ROUTINE_TOKEN}",
                "anthropic-beta": "experimental-cc-routine-2026-04-01",
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={"text": "New email arrived in Gmail inbox"}
        )
        
        print(f"Claude triggered: {response.status_code}")
        return "OK", 200

    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    a
