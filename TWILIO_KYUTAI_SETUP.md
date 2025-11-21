# 🎙️ Twilio + Kyutai TTS Integration Setup

## ✅ What's Ready

Your Twilio voice AI system with **Kyutai TTS** is now set up:

- **Deepgram STT** - Speech-to-text transcription (French optimized)
- **OpenAI GPT** - Dialogue responses
- **Kyutai TTS** - Ultra-low latency text-to-speech (replaces ElevenLabs)
- **Twilio** - Real-time phone integration

## 📁 Files Created

```
twilio_kyutai_tts.py         ← WebSocket handler (Deepgram + GPT + Kyutai TTS)
twilio_flask_app.py          ← Flask app (TwiML + initiate calls)
launch_twilio_server.sh      ← Launch script for both servers
test_kyutai_audio_conversion.py ← Audio pipeline test
```

## 🚀 How to Run

### Prerequisites
- Kyutai TTS running: `moshi-server worker --config configs/config-tts.toml`
- Cloudflare tunnels active and URLs configured
- Python dependencies: `pip install msgpack numpy websockets aiohttp openai twilio flask`

### Option 1: Launch Both Servers (Recommended)

```bash
chmod +x launch_twilio_server.sh
./launch_twilio_server.sh
```

### Option 2: Manual (2 Terminals)

**Terminal 1 - WebSocket Server:**
```bash
python3 twilio_kyutai_tts.py
# Output: 🎧 Server running at ws://0.0.0.0:8765/ws
```

**Terminal 2 - Flask Server:**
```bash
python3 twilio_flask_app.py
# Output: 🌐 FLASK TWILIO SERVER
#         Running on http://0.0.0.0:5000
```

## 📞 Testing

### Initiate a Call
```bash
# Via HTTP
curl http://localhost:5000/call

# Or in browser
open http://localhost:5000/call
```

### Check Status
```bash
curl http://localhost:5000/status
```

### View Transcripts
```bash
tail -f transcript.txt
```

## 🔄 Architecture

```
📱 Twilio Phone Call
     ↓
🌐 Flask TwiML (port 5000)
     ↓
🎧 WebSocket Server (port 8765)
     ↓ (8kHz μ-law audio)
🧬 Deepgram STT (speech → text, French)
     ↓
🤖 OpenAI GPT (text → response)
     ↓
🎙️ Kyutai TTS (text → 24kHz PCM)
     ↓ (convert to 8kHz μ-law)
📱 Twilio Phone Call
```

## ⚡ Performance

- **TTFA (Time-To-First-Audio):** ~1400ms
- **RTF (Real-Time Factor):** ~0.33x (3x faster than real-time)
- **Audio Quality:** 24kHz → 8kHz μ-law (Twilio standard)
- **Latency:** Deepgram ~500ms + GPT ~1000ms + Kyutai ~1400ms = ~3s total

## 📊 Audio Conversion Pipeline

```
Kyutai TTS (24kHz PCM float32)
    ↓ (np.concatenate chunks)
PCM 24kHz float32 [-1, 1]
    ↓ (×32767 → int16)
PCM 24kHz int16 [-32768, 32767]
    ↓ (audioop.ratecv: 24000→8000 Hz)
PCM 8kHz int16
    ↓ (audioop.lin2ulaw)
μ-law 8kHz (Twilio format)
    ↓ (160 bytes = 20ms packets)
Twilio MediaStream
```

## 🔧 Configuration

### Twilio Credentials (Set in .env file)
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_NUMBER=+441686805585
YOUR_NUMBER=+447360507810
```

See `.env.example` for configuration template.

### Kyutai TTS Config (twilio_kyutai_tts.py)
```python
KYUTAI_TTS_URL = "ws://127.0.0.1:8080/api/tts_streaming"
KYUTAI_VOICE = "cml-tts/fr/2465_1943_000152-0002.wav"
KYUTAI_FORMAT = "PcmMessagePack"
```

## 🐛 Troubleshooting

### WebSocket connection fails
- Check Kyutai TTS is running: `ps aux | grep moshi-server`
- Verify port 8080 is open: `curl http://127.0.0.1:8080`

### Deepgram connection fails
- Verify API key: `echo $DEEPGRAM_API_KEY`
- Check internet connection

### Twilio call not connecting
- Verify tunnels are active in Cloudflare dashboard
- Check tunnel URLs match config
- Verify TwiML endpoint returns valid XML

### Audio is silent or corrupted
- Run: `python3 test_kyutai_audio_conversion.py`
- Check audio conversion is working
- Verify Kyutai TTS returns audio data

## 📝 API Keys (⚠️ SECURITY)

**IMPORTANT:** These keys are exposed in the code for testing only!
Before production:
1. Move keys to `.env` file
2. Load with `python-dotenv`
3. Never commit keys to git
4. Rotate all keys

```bash
# Create .env file
cat > .env << EOF
DEEPGRAM_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
EOF

# Load in Python
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("DEEPGRAM_API_KEY")
```

## ✨ Next Steps

1. **Test basic setup:**
   ```bash
   python3 test_kyutai_audio_conversion.py  # Verify audio pipeline
   ```

2. **Start servers:**
   ```bash
   ./launch_twilio_server.sh
   ```

3. **Initiate a call:**
   ```bash
   curl http://localhost:5000/call
   ```

4. **Monitor output:**
   ```bash
   tail -f transcript.txt
   ```

5. **Optimize:**
   - Adjust Kyutai voice if needed
   - Tune GPT prompt for better responses
   - Adjust latency thresholds

## 💡 Tips

- **Faster responses:** Reduce GPT `max_tokens` (currently 100)
- **Better voice quality:** Try different Kyutai voices
- **French optimization:** STT & GPT are already French-optimized
- **Debug audio:** Check `transcript.txt` for full conversation

---

**Version:** 1.0 (Kyutai TTS Integration)
**Last Updated:** 2024-11-21
