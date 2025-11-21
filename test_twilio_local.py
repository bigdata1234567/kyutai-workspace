#!/usr/bin/env python3
"""
Local test of Twilio + Kyutai TTS integration
Simulates a Twilio WebSocket connection without needing a real phone call
"""

import asyncio
import websockets
import json
import base64
import random
import string

# Simulated audio chunks (8kHz μ-law, like Twilio sends)
# This is "Bonjour" in silence (8kHz μ-law encoding)
SILENT_AUDIO = b'\x7f' * 160  # Silence = 0xFF in μ-law

async def test_twilio_connection():
    """Simulate a Twilio WebSocket client"""

    uri = "ws://127.0.0.1:8765/ws"

    print(f"📞 Connecting to WebSocket at {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Generate stream SID (like Twilio does)
            stream_sid = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

            # Send Twilio START event
            start_event = {
                "event": "start",
                "start": {
                    "streamSid": stream_sid,
                    "accountSid": "ACxxxxxxxxxxxxxxxxxxxxxxxx",  # Your Account SID from .env
                    "callSid": "CA" + ''.join(random.choices(string.digits, k=32)),
                    "tracks": ["inbound"]
                }
            }

            await websocket.send(json.dumps(start_event))
            print(f"📡 START event sent (Stream SID: {stream_sid[:8]}...)")

            await asyncio.sleep(1)

            # Simulate user speaking "Bonjour"
            print("\n🗣️ Simulating user: 'Bonjour'")

            # Send audio chunks (simulated silence for now)
            audio_chunks = 40  # ~800ms at 20ms per chunk
            for i in range(audio_chunks):
                media_event = {
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {
                        "payload": base64.b64encode(SILENT_AUDIO).decode("utf-8")
                    }
                }
                await websocket.send(json.dumps(media_event))
                await asyncio.sleep(0.02)  # 20ms
                if (i + 1) % 10 == 0:
                    print(f"  Sent {i + 1} chunks...")

            print("\n⏳ Waiting for response from Deepgram + GPT + Kyutai...")
            print("   (This may take 3-5 seconds)")

            # Listen for media events coming back
            response_audio = []
            start_listen = asyncio.get_event_loop().time()
            max_wait = 15  # seconds

            while asyncio.get_event_loop().time() - start_listen < max_wait:
                try:
                    data = json.loads(await asyncio.wait_for(websocket.recv(), timeout=0.5))

                    if data.get("event") == "media":
                        response_audio.append(data["media"]["payload"])
                        print(f"  🔊 Received audio chunk {len(response_audio)}")

                except asyncio.TimeoutError:
                    # Still waiting for response
                    continue
                except Exception as e:
                    print(f"  ℹ️  {type(e).__name__}: {str(e)[:50]}")
                    break

            if response_audio:
                print(f"\n✅ Received {len(response_audio)} audio chunks from Kyutai TTS!")
                total_audio = sum(len(base64.b64decode(chunk)) for chunk in response_audio)
                print(f"   Total size: {total_audio} bytes = {total_audio/8000:.2f}s @ 8kHz")
            else:
                print("\n⏳ No audio response received (Deepgram may still be processing...)")

            # Send STOP event
            stop_event = {
                "event": "stop",
                "stop": {
                    "streamSid": stream_sid
                }
            }
            await websocket.send(json.dumps(stop_event))
            print("\n🛑 STOP event sent")

            await asyncio.sleep(1)
            print("\n✅ Test completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 LOCAL TWILIO TEST (No phone call needed)")
    print("="*60)
    print("\nThis simulates a Twilio WebSocket connection.")
    print("Make sure both servers are running:")
    print("  - python3 twilio_kyutai_tts.py (port 8765)")
    print("  - python3 twilio_flask_app.py (port 5000)")
    print("\n" + "="*60 + "\n")

    asyncio.run(test_twilio_connection())
