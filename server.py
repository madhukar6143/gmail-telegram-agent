from flask import Flask, request
import requests
import os
import base64
import time

app = Flask(__name__)

ROUTINE_TOKEN = os.environ.get("ROUTINE_TOKEN")
ROUTINE_ID = os.environ.get("ROUTINE_ID")

# Cooldown tracker
last_triggered = 0
COOLDOWN_SECONDS = 300  # 5 minutes

@app.route("/", methods=["GET"])
def home():
    return "Gmail Webhook Server is running!", 200

@app.route("/gmail-webhook", methods=["POST"])
def gmail_webhook():
    global last_triggered
    try:
        envelope = request.get_json()
        if not envelope:
            return "No data received", 400

        pubsub_message = envelope.get("message", {})
        data = pubsub_message.get("data", "")
        
        if data:
            decoded = base64.b64decode(data).decode("utf-8")
            print(f"New email notification: {decoded}")

        # Check cooldown
        now = time.time()
        if now - last_triggered < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - (now - last_triggered))
            print(f"Cooldown active — skipping trigger ({remaining}s remaining)")
            return "OK", 200

        # Trigger Claude
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
        
        if response.status_code == 200:
            last_triggered = now
            print(f"Claude triggered successfully: {response.status_code}")
        else:
            print(f"Claude trigger failed: {response.status_code}")
            
        return "OK", 200

    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
