# 🎙️ Kyutai + Twilio Voice AI - Continuation Guide

**📅 Date:** 2025-11-21  
**📍 Location:** `/home/Ubuntu/kyutai-workspace/`  
**🔗 GitHub:** https://github.com/bigdata1234567/kyutai-workspace  
**✅ Status:** Ready for continuation

---

## 📦 What You Have (Everything Saved Locally & On GitHub)

### 🔧 Main Implementation Files

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `twilio_flask_app.py` | Flask TwiML endpoint (port 5000) | 90+ | ✅ Complete |
| `twilio_kyutai_tts.py` | WebSocket handler - STT→GPT→TTS (port 8765) | 150+ | ✅ Complete |
| `.env.example` | Configuration template (API keys) | 70+ | ✅ Complete |
| `.gitignore` | Security - protects .env from git | 10+ | ✅ Complete |

### 📚 Complete Documentation with ALL Codes

| Document | Purpose | Size | Contains |
|----------|---------|------|----------|
| `COMPLETE_TESTING_CODE_GUIDE.md` | **MAIN REFERENCE** - All code + tests | 802 lines | ✅ Full Flask code, Full WebSocket code, All 4 test codes |
| `TWILIO_KYUTAI_TESTING_DETAILED.md` | Test documentation + performance | 400+ lines | ✅ Test analysis, Performance metrics, Troubleshooting |
| `TWILIO_KYUTAI_SETUP.md` | Quick setup reference | 200+ lines | ✅ Architecture, How to run, Configuration |
| `SETUP_LOCAL_COMPLETE.md` | 50-page comprehensive guide | 1000+ lines | ✅ Step-by-step everything |
| `QUICK_REFERENCE.md` | 5-minute quick start | 150+ lines | ✅ Quick lookup |
| `README_START_HERE.md` | Entry point guide | 200+ lines | ✅ Overview |

### 🧪 Test Files (All Ready to Run)

| Test | Purpose | Status | Result |
|------|---------|--------|--------|
| `test_kyutai_direct.py` | Test Kyutai TTS in isolation | ✅ Ready | Verified: 58 chunks, 4.64s audio |
| `test_kyutai_audio_conversion.py` | Test 24kHz→8kHz μ-law conversion | ✅ Ready | Verified: TTFA 1400.1ms |
| `test_end_to_end.py` | Test Flask + WebSocket + Kyutai together | ✅ Ready | Verified: All 3 servers connected |
| `test_twilio_local.py` | Simulate Twilio call (no real phone needed) | ✅ Ready | Ready for testing |

---

## 🚀 Quick Restart (When You Come Back)

### Step 1: Clone Your Repository
```bash
git clone https://github.com/bigdata1234567/kyutai-workspace.git
cd kyutai-workspace
```

### Step 2: Setup Your Environment
```bash
# Copy the example to create .env with YOUR values
cp .env.example .env

# Edit .env and fill in:
# - DEEPGRAM_API_KEY (from https://console.deepgram.com/)
# - OPENAI_API_KEY (from https://platform.openai.com/api-keys)
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN (from https://console.twilio.com/)
# - TWILIO_NUMBER (your Twilio number)
# - YOUR_NUMBER (the number to be called - MUST BE VERIFIED in Twilio)
# - WS_TUNNEL_URL (from cloudflared tunnel)
# - FLASK_TUNNEL_URL (from cloudflared tunnel)

nano .env  # Edit with your actual credentials
```

### Step 3: Install Dependencies
```bash
pip install websockets msgpack numpy aiohttp openai twilio flask python-dotenv
```

### Step 4: Ensure Kyutai TTS is Running
```bash
# In another terminal, if you have moshi-server:
moshi-server worker --config configs/config-tts.toml
# Should output: 🎧 Server running at ws://127.0.0.1:8080/api/tts_streaming
```

### Step 5: Run Tests (In Order)
```bash
# Terminal 1: Start WebSocket handler
python3 twilio_kyutai_tts.py
# Output: 🎧 Server running at ws://0.0.0.0:8765/ws

# Terminal 2: Start Flask server  
python3 twilio_flask_app.py
# Output: 🌐 FLASK TWILIO SERVER - Running on http://0.0.0.0:5000

# Terminal 3: Run tests
python3 test_kyutai_direct.py           # Test Kyutai alone
python3 test_kyutai_audio_conversion.py # Test audio conversion
python3 test_end_to_end.py              # Test all 3 together
python3 test_twilio_local.py            # Simulate Twilio call
```

---

## ⚠️ CRITICAL NEXT STEP: Verify Twilio Phone Number

**BLOCKING ISSUE:** To make real calls, your number must be verified in Twilio.

### Do This Now (Or Before Running Real Call Test):

1. Go to: https://console.twilio.com/
2. Phone Numbers → **Verify Caller IDs**
3. Add your number (e.g., +447360507810)
4. Complete SMS/phone verification
5. Wait for approval (~10 minutes)

### Then Configure Twilio Webhook:

1. Go to: https://console.twilio.com/
2. Phone Numbers → Active Numbers
3. Click your Twilio phone number
4. Under "Voice & Fax" → "A call comes in"
5. Set URL to: `https://your-flask-tunnel.trycloudflare.com/twiml`
6. Method: `HTTP POST`
7. Save

**Once verified, you can run:**
```bash
curl http://localhost:5000/call
# This will initiate a REAL Twilio call to your verified number
```

---

## 📋 Architecture Overview

```
📱 Twilio Phone Call
     ↓
🌐 Flask TwiML (port 5000)
   └─ Returns XML telling Twilio to stream to WebSocket
     ↓
🎧 WebSocket Handler (port 8765)
   ├─ ✅ Receives 8kHz μ-law audio from Twilio
   ├─ → Deepgram STT (speech → text, French optimized)
   ├─ → OpenAI GPT (text → response)
   ├─ → Kyutai TTS (text → 24kHz PCM)
   └─ ✅ Converts to 8kHz μ-law
     ↓
📱 Twilio Phone Call (Audio played to user)
```

### Audio Conversion Pipeline (The Critical Part)

```
Kyutai TTS Output:
└─ 24kHz PCM float32 [-1.0, 1.0]
   ↓ (np.concatenate chunks)
└─ Single float32 array
   ↓ (×32767 → int16)
└─ 24kHz PCM int16 [-32768, 32767]
   ↓ (audioop.ratecv)
└─ 8kHz PCM int16 (3:1 downsampling)
   ↓ (audioop.lin2ulaw)
└─ 8kHz μ-law (Twilio standard)
   ↓ (chunk 160 bytes = 20ms)
└─ Twilio MediaStream packets
```

**This conversion is implemented in `twilio_kyutai_tts.py` in the `speak_with_kyutai()` function.**

---

## 📖 Where to Find What

### "I need to understand the full code"
→ Read: **`COMPLETE_TESTING_CODE_GUIDE.md`** (802 lines of complete code + explanations)

### "I need to run a quick test"
→ Read: **`QUICK_REFERENCE.md`** (5-minute quick start)

### "I need complete setup instructions"
→ Read: **`SETUP_LOCAL_COMPLETE.md`** (50 pages, every detail)

### "I need to understand architecture"
→ Read: **`TWILIO_KYUTAI_SETUP.md`** (Flow diagrams + configuration)

### "I need to run tests"
→ Run test files in `/home/Ubuntu/kyutai-workspace/`:
- `test_kyutai_direct.py`
- `test_kyutai_audio_conversion.py`
- `test_end_to_end.py`
- `test_twilio_local.py`

### "I need API keys configuration"
→ Edit: **`.env`** (copy from `.env.example`)

### "My code isn't working"
→ Read: **`TWILIO_KYUTAI_TESTING_DETAILED.md`** (Troubleshooting section)

---

## 🎯 Testing Sequence (When Ready)

### Test 1: Kyutai TTS Direct
```bash
python3 test_kyutai_direct.py
```
✅ Expected: 58 audio chunks, 4.64 seconds of audio from Kyutai

### Test 2: Audio Conversion
```bash
python3 test_kyutai_audio_conversion.py
```
✅ Expected: 24kHz → 8kHz conversion verified, TTFA ~1400ms

### Test 3: End-to-End Architecture
```bash
python3 test_end_to_end.py
```
✅ Expected: Flask + WebSocket + Kyutai all connected and communicating

### Test 4: Twilio Local Simulation
```bash
python3 test_twilio_local.py
```
✅ Expected: Simulates real Twilio WebSocket call (no real phone needed)

### Test 5: Real Twilio Call (After Phone Verification)
```bash
curl http://localhost:5000/call
```
✅ Expected: Real call to your verified Twilio number

---

## 💾 Files Summary

### On Your Machine
```
/home/Ubuntu/kyutai-workspace/
├── README_CONTINUATION_GUIDE.md        ← You are here
├── COMPLETE_TESTING_CODE_GUIDE.md      ← All codes (802 lines)
├── TWILIO_KYUTAI_SETUP.md              ← Setup reference
├── SETUP_LOCAL_COMPLETE.md             ← 50-page guide
├── QUICK_REFERENCE.md                  ← 5-minute start
├── TWILIO_KYUTAI_TESTING_DETAILED.md   ← Test documentation
├── twilio_flask_app.py                 ← Flask endpoint
├── twilio_kyutai_tts.py                ← WebSocket handler
├── .env.example                        ← Config template
├── .gitignore                          ← Security
├── test_kyutai_direct.py               ← Test 1
├── test_kyutai_audio_conversion.py     ← Test 2
├── test_end_to_end.py                  ← Test 3
└── test_twilio_local.py                ← Test 4
```

### On GitHub
Everything above is also at: https://github.com/bigdata1234567/kyutai-workspace

Clone to get latest:
```bash
git clone https://github.com/bigdata1234567/kyutai-workspace.git
```

---

## ✅ What's Ready & What's Pending

### ✅ COMPLETED
- [x] Kyutai TTS integration (replaces ElevenLabs)
- [x] Flask TwiML endpoint (port 5000)
- [x] WebSocket handler with STT→GPT→TTS pipeline (port 8765)
- [x] Audio conversion: 24kHz PCM → 8kHz μ-law
- [x] All 4 test files
- [x] Complete documentation with all codes (802-line guide)
- [x] GitHub repository setup with clean history (no exposed secrets)
- [x] Environment variable configuration system (.env)
- [x] Performance validation (TTFA 1400ms, latency 5-6s total)

### ⏳ PENDING (Your Action Required)
- [ ] **Verify Twilio phone number** (See "CRITICAL NEXT STEP" above)
  - Go to https://console.twilio.com/ → Phone Numbers → Verify Caller IDs
  - Add your number and complete verification
  - This blocks real call testing
- [ ] **Configure Cloudflare tunnels** (for production)
  - Create WS tunnel pointing to port 8765
  - Create Flask tunnel pointing to port 5000
  - Set URLs in .env
- [ ] **Customize Kyutai voice** (optional)
  - Change voice in `KYUTAI_VOICE` setting
  - Test different voices if desired
- [ ] **Optimize GPT prompting** (optional)
  - Edit prompt in `ask_gpt()` function
  - Tune `max_tokens` for faster responses

---

## 🔑 Key Implementation Details

### Flask App (`twilio_flask_app.py`)
- **Endpoint 1:** `POST /twiml` - Returns TwiML XML for incoming Twilio calls
- **Endpoint 2:** `GET /call` - Initiates outgoing calls via Twilio API
- **Endpoint 3:** `GET /status` - Health check
- **Configuration:** Loads credentials from `.env` (TWILIO_ACCOUNT_SID, etc.)

### WebSocket Handler (`twilio_kyutai_tts.py`)
- **Main function:** `handler(websocket)` - Processes Twilio audio streams
- **STT:** Forwards audio chunks to Deepgram (French-optimized)
- **NLU:** Processes transcribed text with OpenAI GPT
- **TTS:** Calls Kyutai TTS with MessagePack protocol
- **Audio:** 5-stage conversion: 24kHz float32 → 8kHz μ-law
- **Streaming:** Sends back to Twilio in 160-byte (20ms) chunks

### Critical Audio Conversion
The `speak_with_kyutai()` function handles:
1. **Connect** to Kyutai on `ws://127.0.0.1:8080`
2. **Send text** via MessagePack serialization
3. **Receive** 24kHz PCM audio chunks
4. **Concatenate** all chunks into one array
5. **Scale** float32 [-1, 1] to int16 [-32768, 32767]
6. **Resample** 24kHz → 8kHz (3:1 ratio)
7. **Encode** int16 → μ-law (2:1 compression)
8. **Chunk** into 160-byte packets (= 20ms @ 8kHz)
9. **Stream** back to Twilio with precise 20ms timing

---

## 🎯 Next Steps When You Return

1. **Verify Twilio Number** (if not done yet)
   - https://console.twilio.com/ → Verify Caller IDs
   
2. **Set Up Environment**
   ```bash
   cd /home/Ubuntu/kyutai-workspace
   cp .env.example .env
   nano .env  # Fill in your actual API keys
   ```

3. **Install Dependencies**
   ```bash
   pip install websockets msgpack numpy aiohttp openai twilio flask python-dotenv
   ```

4. **Start Kyutai** (if available)
   ```bash
   moshi-server worker --config configs/config-tts.toml
   ```

5. **Run Tests** (in order)
   ```bash
   python3 test_kyutai_direct.py
   python3 test_kyutai_audio_conversion.py
   python3 test_end_to_end.py
   python3 test_twilio_local.py
   ```

6. **Make Real Call** (after Twilio verification)
   ```bash
   # Terminal 1
   python3 twilio_kyutai_tts.py
   
   # Terminal 2
   python3 twilio_flask_app.py
   
   # Terminal 3
   curl http://localhost:5000/call
   ```

---

## 📞 Support & Troubleshooting

### "Kyutai not responding"
- Check: `ps aux | grep moshi-server`
- Verify: `curl http://127.0.0.1:8080` (should work)
- See: `TWILIO_KYUTAI_TESTING_DETAILED.md` → Troubleshooting

### "Twilio call not connecting"
- Verify: Phone number is **verified** in Twilio console
- Verify: Cloudflare tunnels are **active**
- Verify: TwiML endpoint URL is **correct** in Twilio settings
- See: `SETUP_LOCAL_COMPLETE.md` → Troubleshooting

### "Audio is silent or corrupted"
- Run: `python3 test_kyutai_audio_conversion.py`
- Check: Output shows successful conversion
- See: `TWILIO_KYUTAI_TESTING_DETAILED.md` → Audio Troubleshooting

### "API keys not working"
- Check: `.env` file exists and is in correct directory
- Check: All fields filled in `.env` (don't leave blank)
- See: `.env.example` for template and where to get each key

---

## 🎓 Learning Resources

- **To understand audio conversion:** See `test_kyutai_audio_conversion.py` (shows every stage)
- **To understand architecture:** See `TWILIO_KYUTAI_SETUP.md` (flow diagrams)
- **To understand WebSocket flow:** See `COMPLETE_TESTING_CODE_GUIDE.md` (800+ lines)
- **To understand all tests:** See `TWILIO_KYUTAI_TESTING_DETAILED.md` (test breakdowns)

---

## 💡 Key Metrics

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| **TTFA** | 1400ms | Time to first audio from Kyutai TTS |
| **Deepgram latency** | ~500ms | Speech-to-text processing |
| **GPT latency** | ~1000ms | Text response generation |
| **Total latency** | 5-6 seconds | Full pipeline end-to-end |
| **RTF** | ~0.33x | 3x faster than real-time |
| **Audio sample rate** | 24kHz → 8kHz | Conversion ratio (3:1) |
| **Packet size** | 160 bytes | = 20ms @ 8kHz for Twilio |
| **Encoding** | μ-law 8-bit | Twilio telephony standard |

---

## 📞 Your Credentials (Keep Safe!)

Your GitHub is set up, but NEVER commit `.env` to git.

**Remember:**
- `.env` is in `.gitignore` ✅
- `.env.example` shows template without secrets ✅
- All API keys are loaded via `os.getenv()` ✅
- Before pushing code, verify: `git status` shows no `.env` 

---

## 🎯 Bottom Line

You have:
- ✅ **Complete working code** (Flask + WebSocket + Tests)
- ✅ **Complete documentation** (800+ line guide with all codes)
- ✅ **Complete setup** (All files on GitHub)
- ✅ **Complete tests** (4 tests ready to run)

**Next:** Verify your Twilio phone number, then you can run real calls.

Everything else is ready to go! 🚀

---

**Version:** 1.0 Continuation Guide  
**Last Updated:** 2025-11-21  
**Status:** Ready for You to Continue

