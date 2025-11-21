# ⚡ Quick Start (5 Minutes)

## 🚀 For the Impatient

### **1. Get Files**
```bash
# Download kyutai-workspace from cloud
scp -r ubuntu@cloud-ip:~/kyutai-workspace ~/projects/
cd ~/projects/kyutai-workspace
```

### **2. Install**
```bash
python3 -m venv venv
source venv/bin/activate
pip install websockets msgpack numpy aiohttp openai flask twilio python-dotenv
```

### **3. Configure**
```bash
cat > .env << 'EOF'
DEEPGRAM_API_KEY=your_key
OPENAI_API_KEY=sk-proj-your_key
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=your_token
TWILIO_NUMBER=+441234567890
YOUR_NUMBER=+447360507810
WS_TUNNEL_URL=wss://your-tunnel.trycloudflare.com/ws
FLASK_TUNNEL_URL=https://your-tunnel.trycloudflare.com
EOF
```

### **4. Start Servers (3 terminals)**

**Terminal 1 - Kyutai TTS (on GPU machine):**
```bash
moshi-server worker --config delayed-streams-modeling/configs/config-tts.toml
```

**Terminal 2 - WebSocket:**
```bash
python3 twilio_kyutai_tts.py
```

**Terminal 3 - Flask:**
```bash
python3 twilio_flask_app.py
```

### **5. Test**
```bash
# Direct test (no phone needed)
python3 test_kyutai_direct.py

# Or make a call (after Twilio config)
curl http://localhost:5000/call
```

---

## 📋 Checklist Before Running

- [ ] `.env` file created with all API keys
- [ ] Kyutai TTS server running (`moshi-server worker...`)
- [ ] Python packages installed (`pip install...`)
- [ ] Twilio number verified (for outgoing calls)
- [ ] Twilio voice URL configured to `https://your-flask-tunnel/twiml`
- [ ] Cloudflare tunnels active (for public URLs)

---

## 🧪 Quick Tests

```bash
# Test 1: Kyutai TTS
python3 test_kyutai_direct.py
# Should output: ✅ Everything working!

# Test 2: Audio conversion
python3 test_kyutai_audio_conversion.py
# Should output: ✅ All conversions successful!

# Test 3: Architecture
python3 test_end_to_end.py
# Should output: ✅ Ready for Twilio: ✅
```

---

## 📞 Making a Call

```bash
# Option A: Outgoing call
curl http://localhost:5000/call
# Your phone will ring

# Option B: Incoming call
# Set up Twilio to call your number, it will connect to TwiML endpoint
```

---

## 🔍 Monitoring

```bash
# Watch conversation
tail -f transcript.txt

# Check servers running
ps aux | grep python3

# Check GPU usage (if local)
nvidia-smi -l 1
```

---

## 🚨 If Something Breaks

```bash
# Kill all Python servers
pkill -f python3

# Restart Kyutai TTS
moshi-server worker --config delayed-streams-modeling/configs/config-tts.toml

# Restart everything
python3 twilio_kyutai_tts.py &
python3 twilio_flask_app.py &

# Test
python3 test_kyutai_direct.py
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | API keys (NEVER commit!) |
| `twilio_kyutai_tts.py` | Main WebSocket handler |
| `twilio_flask_app.py` | TwiML endpoint |
| `transcript.txt` | Conversation log |
| `test_*.py` | Test scripts |

---

## 💰 Costs

Per minute of call:
- Twilio: $0.0075-0.02
- Deepgram: $0.0005
- OpenAI: $0.015-0.03
- Kyutai: $0 (self-hosted)
- **Total: ~$0.025/min = $1.50/hour**

---

## 🎯 What Happens When You Call

1. **Twilio receives your call** → Sends 8kHz μ-law audio
2. **WebSocket handler** → Routes to Deepgram + GPT + Kyutai
3. **Deepgram STT** → Converts speech to text (~500ms)
4. **GPT-4o** → Generates response (~1000ms)
5. **Kyutai TTS** → Synthesizes speech (~1400ms)
6. **Audio conversion** → 24kHz → 8kHz μ-law
7. **Twilio** → Streams back to your phone

**Total latency: 3-5 seconds** (acceptable for voice)

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" on 8765 | `python3 twilio_kyutai_tts.py` not running |
| Deepgram fails | Check `DEEPGRAM_API_KEY` in `.env` |
| OpenAI fails | Check `OPENAI_API_KEY` in `.env` |
| Kyutai TTS fails | Check moshi-server running on GPU |
| Audio is silent | Run `python3 test_kyutai_direct.py` to debug |
| Twilio won't call | Verify phone number in Twilio console |

---

## ✨ Pro Tips

- Add `DEBUG=1` to see detailed logs
- Use `gpt-4-turbo` instead of `gpt-4o` for faster/cheaper responses
- Reduce `max_tokens` from 100 to 50 for faster replies
- Test with `test_kyutai_direct.py` before making real calls
- Monitor `transcript.txt` to debug conversations

---

See **SETUP_LOCAL_COMPLETE.md** for full documentation.
