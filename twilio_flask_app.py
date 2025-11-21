#!/usr/bin/env python3
"""
Flask server for Twilio TwiML endpoint
Handles incoming calls and initiates outgoing calls
"""

from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect

app = Flask(__name__)

# ✅ Twilio credentials (Load from .env - see .env.example)
import os
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER", "")
YOUR_NUMBER = os.getenv("YOUR_NUMBER", "")

if not all([ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER, YOUR_NUMBER]):
    raise ValueError("❌ Missing Twilio credentials in .env file. See .env.example")

# URLs (from Cloudflare tunnels)
WS_TUNNEL_URL = "wss://birds-colony-large-ms.trycloudflare.com/ws"
FLASK_TUNNEL_URL = "https://interstate-arrest-bronze-stuart.trycloudflare.com"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

@app.route("/twiml", methods=["POST"])
def twiml():
    """TwiML response to connect call to WebSocket"""
    print("✅ Twilio requested TwiML")
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=WS_TUNNEL_URL)
    response.append(connect)
    return Response(str(response), mimetype="text/xml")

@app.route("/call", methods=["GET"])
def call():
    """Initiate a new call"""
    print("☎️ Starting call...")
    try:
        call_obj = client.calls.create(
            to=YOUR_NUMBER,
            from_=TWILIO_NUMBER,
            url=f"{FLASK_TUNNEL_URL}/twiml"
        )
        return f"✅ Call initiated! SID: {call_obj.sid}\n"
    except Exception as e:
        return f"❌ Error: {e}\n", 500

@app.route("/status", methods=["GET"])
def status():
    """Health check"""
    return "🎧 Twilio + Kyutai TTS Flask server is running\n"

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌐 FLASK TWILIO SERVER")
    print("="*60)
    print(f"📱 Twilio number: {TWILIO_NUMBER}")
    print(f"📞 Your number: {YOUR_NUMBER}")
    print(f"🎙️ WebSocket tunnel: {WS_TUNNEL_URL}")
    print(f"🌐 Flask tunnel: {FLASK_TUNNEL_URL}")
    print("\nEndpoints:")
    print(f"  GET  http://localhost:5000/call     - Initiate a call")
    print(f"  POST http://localhost:5000/twiml    - TwiML callback")
    print(f"  GET  http://localhost:5000/status   - Health check")
    print("="*60 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False)
