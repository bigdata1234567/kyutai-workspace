#!/bin/bash

# ✅ Launch both servers
# Terminal 1: Flask (port 5000)
# Terminal 2: WebSocket (port 8765)

echo "🚀 Starting Twilio + Kyutai TTS servers..."
echo ""

# Check if Kyutai TTS is running
echo "Checking Kyutai TTS..."
if ps aux | grep -i "moshi-server" | grep -v grep > /dev/null; then
    echo "✅ Kyutai TTS is running"
else
    echo "❌ Kyutai TTS is NOT running. Please start it first."
    echo "   Start in another terminal: moshi-server worker --config configs/config-tts.toml"
    exit 1
fi

echo ""
echo "Starting servers..."
echo ""

# Start Flask in background
echo "🌐 Starting Flask server (port 5000)..."
python3 twilio_flask_app.py &
FLASK_PID=$!
sleep 2

# Start WebSocket server in foreground
echo "🎧 Starting WebSocket server (port 8765)..."
python3 twilio_kyutai_tts.py

# Cleanup on exit
trap "kill $FLASK_PID 2>/dev/null" EXIT
