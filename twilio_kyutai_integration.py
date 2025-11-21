import asyncio
import websockets
import base64
import json
import aiohttp
import datetime
import struct
import msgpack
import os
from openai import OpenAI
import scipy.signal
import numpy as np

# ✅ Configuration from environment variables
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
KYUTAI_TTS_URI = os.getenv("KYUTAI_TTS_URI", "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack")
KYUTAI_API_KEY = os.getenv("KYUTAI_API_KEY", "public_token")
TWILIO_SERVER_HOST = os.getenv("TWILIO_SERVER_HOST", "0.0.0.0")
TWILIO_SERVER_PORT = int(os.getenv("TWILIO_SERVER_PORT", "8765"))
TRANSCRIPT_FILE = os.getenv("TRANSCRIPT_FILE", "transcript.txt")

# ✅ Validate required API keys
if not DEEPGRAM_API_KEY or not OPENAI_API_KEY:
    raise ValueError("❌ Missing required environment variables: DEEPGRAM_API_KEY and OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Convert float PCM to int16
def float_to_int16(float_samples):
    """Convert float [-1.0, 1.0] to int16 [-32768, 32767]"""
    return np.array([int(x * 32767) for x in float_samples], dtype=np.int16)

# ✅ Convert int16 PCM to µ-law (8-bit)
def pcm_to_ulaw(pcm_data):
    """Convert 16-bit PCM to 8-bit µ-law"""
    # Use librosa/scipy compatible approach
    mu = 255.0
    safe_abs_value = np.abs(pcm_data)
    magnitude = np.log(1.0 + mu * safe_abs_value / 32768.0) / np.log(1.0 + mu)
    signal = np.sign(pcm_data) * magnitude * 128.0
    return np.uint8(signal + 128.0)

# ✅ Resample 24kHz → 8kHz
def resample_24k_to_8k(pcm_int16):
    """Resample PCM from 24kHz to 8kHz"""
    # Simple approach: every 3rd sample (24000/8000 = 3)
    # Better approach: use scipy.signal.resample
    num_samples = int(len(pcm_int16) / 3)
    resampled = scipy.signal.resample(pcm_int16, num_samples)
    return np.int16(resampled)

# ✅ WebSocket Handler
async def handler(websocket):
    print("✅ Twilio connected!")

    async with aiohttp.ClientSession() as session:
        deepgram_url = (
            "wss://api.deepgram.com/v1/listen?"
            "model=nova-2&encoding=mulaw&sample_rate=8000&channels=1&language=fr"
            "&smart_format=true&interim_results=true&endpointing=500"
        )
        dg_ws = await session.ws_connect(deepgram_url, headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"})
        print("🧬 Connected to Deepgram")

        # Reset transcript
        open(TRANSCRIPT_FILE, "w").close()

        stream_sid = None

        async def twilio_to_deepgram():
            nonlocal stream_sid
            try:
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("event") == "media":
                        audio = base64.b64decode(data["media"]["payload"])
                        await dg_ws.send_bytes(audio)
                    elif data.get("event") == "start":
                        stream_sid = data["start"]["streamSid"]
                        print(f"📡 Stream SID: {stream_sid}")
            except websockets.exceptions.ConnectionClosedError as e:
                print("🔌 Twilio closed:", e)

        async def deepgram_to_actions():
            try:
                async for msg in dg_ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        dg_data = json.loads(msg.data)
                        transcript = dg_data.get("channel", {}).get("alternatives", [{}])[0].get("transcript")
                        if transcript:
                            is_final = dg_data.get("is_final", False)
                            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                            print(f"🗣️ [{timestamp}] {'(FINAL)' if is_final else '(INTERIM)'} {transcript}")

                            if is_final:
                                with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as f:
                                    f.write(transcript + "\n")
                                gpt_reply = await ask_gpt(transcript)
                                print(f"🤖 GPT: {gpt_reply}")
                                await speak_with_kyutai(gpt_reply, websocket, stream_sid)
            except Exception as e:
                print("❌ Deepgram error:", e)

        await asyncio.gather(twilio_to_deepgram(), deepgram_to_actions())

# ✅ GPT Response
async def ask_gpt(text):
    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un assistant vocal amical. Réponds de manière concise en français (max 2-3 phrases)."},
                    {"role": "user", "content": text}
                ],
                max_tokens=100
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur GPT: {e}"

# ✅ Kyutai TTS → µ-law 8kHz → Send to Twilio
async def speak_with_kyutai(text, websocket, stream_sid):
    try:
        print(f"🎙️ Kyutai TTS: Converting '{text}' to speech...")

        # Connect to Kyutai TTS
        async with websockets.connect(KYUTAI_TTS_URI, additional_headers={"kyutai-api-key": KYUTAI_API_KEY}, ping_interval=None) as tts_ws:
            # Send text (using msgpack directly)
            await tts_ws.send(msgpack.packb({"type": "Text", "text": text}))
            # Signal end of stream
            await tts_ws.send(msgpack.packb({"type": "Eos"}))

            # Collect all PCM chunks
            pcm_float_list = []
            try:
                async with asyncio.timeout(10.0):
                    async for msg_bytes in tts_ws:
                        msg = msgpack.unpackb(msg_bytes)

                        if msg.get("type") == "Audio":
                            pcm = msg.get("pcm", [])
                            if isinstance(pcm, list):
                                pcm_float_list.extend(pcm)
                        elif msg.get("type") == "Done":
                            break
            except asyncio.TimeoutError:
                print("⚠️  Timeout waiting for Kyutai audio")
                pass

            if not pcm_float_list:
                print("❌ No audio from Kyutai")
                return

            # Convert float → int16
            pcm_int16 = float_to_int16(pcm_float_list)
            print(f"✅ Got {len(pcm_int16)} PCM samples @ 24kHz")

            # Resample 24kHz → 8kHz
            pcm_8k = resample_24k_to_8k(pcm_int16)
            print(f"📊 Resampled to {len(pcm_8k)} samples @ 8kHz")

            # Convert PCM → µ-law
            ulaw_data = pcm_to_ulaw(pcm_8k)
            print(f"🔉 Converted to µ-law: {len(ulaw_data)} bytes")

            # Chunk and send to Twilio (20ms per packet → 160 bytes µ-law @ 8kHz)
            chunk_size = 160
            for i in range(0, len(ulaw_data), chunk_size):
                chunk = ulaw_data[i:i+chunk_size]
                audio_base64 = base64.b64encode(chunk).decode("utf-8")
                await websocket.send(json.dumps({
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {"payload": audio_base64}
                }))
                await asyncio.sleep(0.02)  # ~20ms

            print(f"✅ Audio sent to Twilio ({len(ulaw_data)} bytes total)")

    except Exception as e:
        print(f"❌ Kyutai TTS error: {e}")
        import traceback
        traceback.print_exc()

# ✅ Run server
async def main():
    print(f"🎧 Kyutai TTS + Twilio Server running at ws://{TWILIO_SERVER_HOST}:{TWILIO_SERVER_PORT}/ws")
    print(f"📡 Kyutai TTS endpoint: {KYUTAI_TTS_URI}")
    async with websockets.serve(handler, TWILIO_SERVER_HOST, TWILIO_SERVER_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
