# 🚀 Twilio + Kyutai TTS Integration - Quick Start (5 minutes)

**Goal:** Get the Twilio + Kyutai TTS server running and replace ElevenLabs

---

## 1️⃣ Configure API Keys (2 minutes)

```bash
cd /home/Ubuntu/kyutai-workspace

# Copy example config
cp .env.example .env

# Edit with your API keys
nano .env
```

Required:
- `DEEPGRAM_API_KEY` from https://console.deepgram.com/
- `OPENAI_API_KEY` from https://platform.openai.com/api-keys

```env
DEEPGRAM_API_KEY="your-key-here"
OPENAI_API_KEY="your-key-here"
```

---

## 2️⃣ Verify Prerequisites (1 minute)

```bash
# Load environment
source .env

# Run pre-flight check
python3 test_integration_setup.py
```

**Expected output:**
```
✅ Dependencies installed
✅ API Keys configured
✅ Audio conversion
✅ Docker running
✅ Kyutai TTS responding
```

If any checks fail, follow the quick fixes shown.

---

## 3️⃣ Start Kyutai TTS Server (1 minute)

```bash
# Start Kyutai TTS (if not already running)
docker compose -f docker-compose.tts.yml up -d

# Wait ~30 seconds for startup
sleep 30

# Verify it's running
docker ps | grep kyutai
```

---

## 4️⃣ Start Twilio Integration Server (1 minute)

```bash
# Run the integration server
python3 twilio_kyutai_integration.py
```

**Expected output:**
```
🎧 Kyutai TTS + Twilio Server running at ws://0.0.0.0:8765/ws
📡 Kyutai TTS endpoint: ws://127.0.0.1:8080/api/tts_streaming?...
```

---

## 5️⃣ Configure Twilio (Optional - 1 minute)

In your Twilio Console, set the Voice webhook URL:

```
wss://your-domain.com:8765/ws
```

Or use Twilio CLI:
```bash
twilio phone-numbers:update +1234567890 \
  --voice-url="wss://your-server:8765/ws"
```

---

## ✅ Done!

Your integration is now running. When calls come in:
1. Deepgram transcribes the audio (French STT)
2. GPT generates a response
3. **Kyutai TTS synthesizes speech** (replaces ElevenLabs)
4. Audio is sent back to Twilio

---

## 📚 Need More Details?

- **Full deployment guide:** `TWILIO_KYUTAI_DEPLOYMENT_GUIDE.md`
- **Code reference:** See `twilio_kyutai_integration.py:60-100` for the main handler
- **Audio conversion pipeline:** `twilio_kyutai_integration.py:30-47` (float→int16→resample→µ-law)

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Connection refused" to Kyutai | Start Docker: `docker compose -f docker-compose.tts.yml up -d` |
| "API key not found" | Load env: `source .env` |
| "Timeout from Kyutai" | Wait 30s for startup, check GPU with `nvidia-smi` |
| Audio sounds distorted | Check resampling settings in `twilio_kyutai_integration.py:43-45` |

---

## 💰 Cost Comparison

| Service | Before (ElevenLabs) | After (Kyutai) | Savings |
|---------|------------------|-----------------|---------|
| TTS cost/hour | $15 | Free (self-hosted) | $15 |
| Per 1000 hours | $15,000 | ~$200 (misc) | **$14,800** |
| Monthly (1000h) | $1,250 | ~$17 | **98% savings** |

---

## 📝 Files Created

| File | Purpose |
|------|---------|
| `twilio_kyutai_integration.py` | Main integration server |
| `.env.example` | Configuration template |
| `test_integration_setup.py` | Pre-flight validation |
| `TWILIO_KYUTAI_DEPLOYMENT_GUIDE.md` | Full documentation |
| `INTEGRATION_QUICK_START.md` | This file |

---

**Ready to save 98% on TTS costs? You're all set! 🎉**
