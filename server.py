from flask import Flask, request
import requests
import os
import json
import base64

app = Flask(__name__)

# Your Claude Code Routine API details
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
ROUTINE_ID = os.environ.get("ROUTINE_ID")

@app.route("/", methods=["GET"])
def home():
    return "Gmail Webhook Server is running!", 200

@app.route("/gmail-webhook", methods=["POST"])
def gmail_webhook():
    try:
        # Google sends base64 encoded data
        envelope = request.get_json()
        if not envelope:
            return "No data received", 400

        # Decode the Pub/Sub message
        pubsub_message = envelope.get("message", {})
        data = pubsub_message.get("data", "")
        
        if data:
            decoded = base64.b64decode(data).decode("utf-8")
            print(f"New email notification: {decoded}")

        # Trigger Claude Code Routine
        # response = requests.post(
        #     f"https://api.claude.ai/api/coding_assistants/routines/{ROUTINE_ID}/trigger",
        #     headers={
        #         "Authorization": f"Bearer {CLAUDE_API_KEY}",
        #         "Content-Type": "application/json"
        #     },
        #     json={"source": "gmail_webhook"}
        # )

        response = requests.post(
    f"https://api.anthropic.com/v1/routines/{ROUTINE_ID}/trigger",
    headers={
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    },
    json={"source": "gmail_webhook"}
)
        
        print(f"Claude triggered: {response.status_code}")
        return "OK", 200

    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
