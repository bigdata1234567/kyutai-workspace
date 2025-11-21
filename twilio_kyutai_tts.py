import asyncio
import websockets
import base64
import json
import aiohttp
import datetime
import msgpack
import numpy as np
import audioop
from openai import OpenAI

# ✅ API Keys (Load from .env file - see .env.example)
import os
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not DEEPGRAM_API_KEY or not OPENAI_API_KEY:
    raise ValueError("❌ Missing API keys in .env file. See .env.example")

# ✅ Kyutai TTS Configuration
KYUTAI_TTS_URL = "ws://127.0.0.1:8080/api/tts_streaming"
KYUTAI_API_KEY = "public_token"
KYUTAI_VOICE = "cml-tts/fr/2465_1943_000152-0002.wav"
KYUTAI_FORMAT = "PcmMessagePack"

TRANSCRIPT_FILE = "transcript.txt"

client = OpenAI(api_key=OPENAI_API_KEY)

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
                    {"role": "system", "content": "Réponds de manière amicale et concise en français."},
                    {"role": "user", "content": text}
                ],
                max_tokens=100
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur GPT: {e}"

# ✅ Kyutai TTS → 24kHz PCM → 8kHz μ-law → Twilio
async def speak_with_kyutai(text, websocket, stream_sid):
    try:
        uri = f"{KYUTAI_TTS_URL}?voice={KYUTAI_VOICE}&format={KYUTAI_FORMAT}"
        headers = {"kyutai-api-key": KYUTAI_API_KEY}

        print(f"🎙️ Kyutai: {text[:60]}...")

        async with websockets.connect(uri, additional_headers=headers) as tts_ws:
            # Send text word by word
            for word in text.split():
                await tts_ws.send(msgpack.packb({"type": "Text", "text": word + " "}))
            await tts_ws.send(msgpack.packb({"type": "Eos"}))

            # Collect audio chunks
            audio_chunks = []
            async for message_bytes in tts_ws:
                msg = msgpack.unpackb(message_bytes)
                if msg.get("type") == "Audio":
                    pcm_data = msg.get("pcm")
                    if pcm_data is not None:
                        audio_chunks.append(pcm_data)

            if not audio_chunks:
                print("❌ No audio from Kyutai")
                return

            # Convert 24kHz PCM float → 8kHz μ-law
            pcm_24k = np.concatenate(audio_chunks, axis=0)
            pcm_int16 = (pcm_24k * 32767).astype(np.int16).tobytes()
            pcm_8k, _ = audioop.ratecv(pcm_int16, 2, 1, 24000, 8000, None)
            pcm_mulaw = audioop.lin2ulaw(pcm_8k, 2)

            print(f"🔉 {len(pcm_mulaw)} bytes to Twilio")

            # Stream to Twilio (160 bytes = 20ms)
            chunk_size = 160
            for i in range(0, len(pcm_mulaw), chunk_size):
                chunk = pcm_mulaw[i:i+chunk_size]
                audio_base64 = base64.b64encode(chunk).decode("utf-8")
                await websocket.send(json.dumps({
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {"payload": audio_base64}
                }))
                await asyncio.sleep(0.02)

            print("✅ Audio sent")

    except Exception as e:
        print(f"❌ Kyutai error: {e}")

# ✅ Run server
async def main():
    print("🎧 Server running at ws://0.0.0.0:8765/ws")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
