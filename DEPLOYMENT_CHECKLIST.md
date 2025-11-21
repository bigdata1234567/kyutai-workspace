# ✅ Deployment Checklist

Use this checklist to ensure everything is ready before going live.

---

## 📦 Phase 1: Code & Files

- [ ] Download `kyutai-workspace` to local machine
- [ ] Create virtual environment: `python3 -m venv venv`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Install dependencies: `pip install websockets msgpack numpy aiohttp openai flask twilio python-dotenv`
- [ ] Copy test files to local:
  - [ ] `test_kyutai_direct.py`
  - [ ] `test_kyutai_audio_conversion.py`
  - [ ] `test_twilio_local.py`
  - [ ] `test_end_to_end.py`
- [ ] Copy main scripts:
  - [ ] `twilio_kyutai_tts.py`
  - [ ] `twilio_flask_app.py`
  - [ ] `launch_twilio_server.sh`

---

## 🔑 Phase 2: API Keys & Credentials

Create `.env` file with:

- [ ] `DEEPGRAM_API_KEY` (from https://console.deepgram.com/)
  - Verify it works: `curl -H "Authorization: Token YOUR_KEY" https://api.deepgram.com/v1/status`

- [ ] `OPENAI_API_KEY` (from https://platform.openai.com/api-keys)
  - Verify it works: Test in Python with `OpenAI(api_key=...)`

- [ ] `TWILIO_ACCOUNT_SID` (from https://console.twilio.com/)
- [ ] `TWILIO_AUTH_TOKEN` (from https://console.twilio.com/)
- [ ] `TWILIO_NUMBER` (your purchased/verified UK number)
- [ ] `YOUR_NUMBER` (number to be called)

- [ ] Verify YOUR_NUMBER:
  - [ ] Go to https://console.twilio.com/
  - [ ] **Account** → **Phone Numbers** → **Verified Caller IDs**
  - [ ] Add YOUR_NUMBER if not listed
  - [ ] Complete SMS/call verification

- [ ] Verify TWILIO_NUMBER:
  - [ ] Go to https://console.twilio.com/
  - [ ] **Phone Numbers** → **Active Numbers**
  - [ ] Set "Friendly Name" (any name is fine)
  - [ ] Under **Voice & Fax** → **A call comes in**: Select "Webhook"

---

## 🌐 Phase 3: Cloudflare Tunnels

- [ ] Install cloudflared:
  ```bash
  curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.tgz | tar xz
  ```

- [ ] Create Flask tunnel (port 5000):
  ```bash
  ./cloudflared tunnel --url http://localhost:5000
  # Note the URL: wss://xxxxx.trycloudflare.com
  ```

- [ ] Create WebSocket tunnel (port 8765):
  ```bash
  ./cloudflared tunnel --url ws://localhost:8765
  # Note the URL: wss://xxxxx.trycloudflare.com
  ```

- [ ] Add URLs to `.env`:
  ```
  WS_TUNNEL_URL=wss://your-ws-tunnel.trycloudflare.com/ws
  FLASK_TUNNEL_URL=https://your-flask-tunnel.trycloudflare.com
  ```

---

## 🎙️ Phase 4: Kyutai TTS Configuration

- [ ] Kyutai TTS server accessible:
  - [ ] SSH to cloud machine (if remote)
  - [ ] Ensure `moshi-server worker --config...` is running
  - [ ] Test: `python3 test_kyutai_direct.py` returns ✅

- [ ] Update `.env`:
  ```
  KYUTAI_TTS_URL=ws://127.0.0.1:8080/api/tts_streaming
  KYUTAI_API_KEY=public_token
  KYUTAI_VOICE=cml-tts/fr/2465_1943_000152-0002.wav
  KYUTAI_FORMAT=PcmMessagePack
  ```

---

## 📱 Phase 5: Twilio Configuration

- [ ] Update voice URL in Twilio Console:
  1. Go to https://console.twilio.com/
  2. **Phone Numbers** → **Active Numbers**
  3. Click your number
  4. Under **Voice & Fax**:
     - [ ] **A call comes in:** `Webhook` (dropdown)
     - [ ] **URL:** `https://your-flask-tunnel.trycloudflare.com/twiml`
     - [ ] **Method:** `HTTP POST`
  5. Click **Save**

- [ ] Test TwiML endpoint:
  ```bash
  curl -X POST https://your-flask-tunnel.trycloudflare.com/twiml
  # Should return valid XML with <Connect><Stream>...</Stream></Connect>
  ```

---

## 🧪 Phase 6: Testing

### Local Tests (No Phone Needed)

```bash
# Test 1: Kyutai TTS Direct
python3 test_kyutai_direct.py
# Expected: ✅ Everything working!

# Test 2: Audio Conversion
python3 test_kyutai_audio_conversion.py
# Expected: ✅ All conversions successful!

# Test 3: Full Architecture
python3 test_end_to_end.py
# Expected: ✅ Ready for Twilio: ✅
```

Checklist:
- [ ] Test 1 passes
- [ ] Test 2 passes
- [ ] Test 3 passes

### End-to-End Test (With Real Call)

1. **Start all servers:**
   ```bash
   # Terminal 1: Kyutai TTS (on cloud machine)
   moshi-server worker --config configs/config-tts.toml

   # Terminal 2: WebSocket handler
   python3 twilio_kyutai_tts.py

   # Terminal 3: Flask server
   python3 twilio_flask_app.py
   ```

2. **Make a test call:**
   ```bash
   curl http://localhost:5000/call
   # Your phone will ring in 5-10 seconds
   ```

3. **Test the conversation:**
   - [ ] Phone rings
   - [ ] You can hear dialing tone
   - [ ] You can speak
   - [ ] AI responds with audio
   - [ ] Audio is clear (not distorted)

4. **Monitor conversation:**
   ```bash
   tail -f transcript.txt
   # Should show your speech + AI response
   ```

---

## 🚀 Phase 7: Production Setup

- [ ] Update API keys to use environment variables (not hardcoded)
- [ ] Add error handling & logging
- [ ] Set up monitoring (e.g., CloudWatch, Datadog)
- [ ] Add conversation database storage
- [ ] Implement rate limiting
- [ ] Set up HTTPS certificates (not just Cloudflare tunnel)
- [ ] Add call recording
- [ ] Implement user authentication

---

## 📊 Phase 8: Monitoring & Costs

### Daily Checks
- [ ] Check transcript.txt for conversation quality
- [ ] Monitor error logs
- [ ] Check API usage (OpenAI, Deepgram)
- [ ] Test a manual call

### Cost Tracking
- [ ] Twilio: https://console.twilio.com/ → Billing
- [ ] Deepgram: https://console.deepgram.com/ → Usage
- [ ] OpenAI: https://platform.openai.com/ → Usage → API Keys

Estimated monthly cost (1000 minutes/month):
- Twilio: ~$15
- Deepgram: ~$0.30
- OpenAI: ~$15
- **Total: ~$30/month**

---

## 🐛 Phase 9: Troubleshooting

Before production, test these failure scenarios:

- [ ] **Deepgram API fails:**
  - Connection timeout → Fallback to default response
  - Invalid API key → Alert and log

- [ ] **OpenAI API fails:**
  - Rate limit hit → Queue request
  - Invalid API key → Alert and log

- [ ] **Kyutai TTS fails:**
  - WebSocket disconnects → Retry
  - No audio received → Fallback text-only response

- [ ] **Twilio connection drops:**
  - Graceful cleanup of resources
  - Error logging

- [ ] **Audio quality issues:**
  - Test with different microphones
  - Test with different networks
  - Monitor silence/noise levels

---

## ✅ Final Checklist

- [ ] All code files downloaded locally
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] `.env` file created with all keys
- [ ] Twilio number verified
- [ ] Twilio voice URL configured correctly
- [ ] Cloudflare tunnels active
- [ ] All 3 local tests pass
- [ ] End-to-end call test successful
- [ ] Conversation saved to transcript.txt
- [ ] Audio quality is acceptable
- [ ] Response latency is acceptable (~3-5 seconds)
- [ ] Cost estimates reviewed
- [ ] Error handling tested
- [ ] Monitoring set up
- [ ] Team trained on deployment
- [ ] Backup plan for failures documented

---

## 🎉 Ready to Deploy!

Once all checkboxes are ✅, your system is ready for:
- Production calls
- High volume
- 24/7 operation
- Multiple concurrent calls

---

## 📞 Support

If something fails:

1. **Check `.env` variables:** `cat .env | grep KEY_NAME`
2. **Test individual components:** `python3 test_kyutai_direct.py`
3. **Check logs:** `tail -f transcript.txt`
4. **Verify APIs:** `curl` endpoints
5. **Restart servers:** `pkill -f python3`

See **SETUP_LOCAL_COMPLETE.md** → **Troubleshooting** for detailed solutions.
