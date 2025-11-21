#!/usr/bin/env python3
"""
Direct test of Kyutai TTS without needing Deepgram
Bypasses STT and goes directly to TTS
"""

import asyncio
import websockets
import json
import base64
import msgpack
import numpy as np
import audioop

KYUTAI_TTS_URL = "ws://127.0.0.1:8080/api/tts_streaming"
KYUTAI_API_KEY = "public_token"
KYUTAI_VOICE = "cml-tts/fr/2465_1943_000152-0002.wav"
KYUTAI_FORMAT = "PcmMessagePack"

async def test_kyutai_direct():
    """Test Kyutai TTS directly"""

    uri = f"{KYUTAI_TTS_URL}?voice={KYUTAI_VOICE}&format={KYUTAI_FORMAT}"
    headers = {"kyutai-api-key": KYUTAI_API_KEY}

    text = "Bonjour, ceci est un test de Kyutai TTS avec la nouvelle intégration Twilio."

    print(f"📝 Text: {text}")
    print(f"🎙️ Kyutai TTS URL: {uri}\n")

    try:
        async with websockets.connect(uri, additional_headers=headers) as ws:
            print("✅ Connected to Kyutai TTS\n")

            # Send text
            print("📤 Sending text...")
            for word in text.split():
                await ws.send(msgpack.packb({"type": "Text", "text": word + " "}))

            await ws.send(msgpack.packb({"type": "Eos"}))
            print("✅ Text sent\n")

            # Receive audio
            print("📥 Receiving audio...")
            audio_chunks = []
            chunk_count = 0

            async for message_bytes in ws:
                msg = msgpack.unpackb(message_bytes)

                if msg.get("type") == "Audio":
                    pcm_data = msg.get("pcm")
                    if pcm_data is not None:
                        audio_chunks.append(pcm_data)
                        chunk_count += 1
                        if chunk_count % 10 == 0:
                            print(f"  Received {chunk_count} chunks...")

            print(f"✅ Received {chunk_count} chunks\n")

            if not audio_chunks:
                print("❌ No audio received!")
                return

            # Convert to 8kHz μ-law
            print("🔄 Converting 24kHz PCM → 8kHz μ-law...")
            pcm_24k = np.concatenate(audio_chunks, axis=0)
            print(f"   Input: {len(pcm_24k)} samples @ 24kHz = {len(pcm_24k)/24000:.2f}s")

            pcm_int16 = (pcm_24k * 32767).astype(np.int16).tobytes()
            pcm_8k, _ = audioop.ratecv(pcm_int16, 2, 1, 24000, 8000, None)
            pcm_mulaw = audioop.lin2ulaw(pcm_8k, 2)

            print(f"   Output: {len(pcm_mulaw)} bytes @ 8kHz μ-law = {len(pcm_mulaw)/8000:.2f}s")

            # Simulate sending to Twilio
            chunk_size = 160  # 20ms
            num_chunks = len(pcm_mulaw) // chunk_size

            print(f"\n📦 Twilio chunks: {num_chunks} × {chunk_size} bytes (20ms each)")
            print(f"   Total duration: {num_chunks * 0.02:.2f}s")

            print("\n✅ Everything working!")
            print(f"\n📊 Summary:")
            print(f"   - Kyutai TTS: ✅")
            print(f"   - Audio conversion: ✅")
            print(f"   - Ready for Twilio: ✅")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️ KYUTAI TTS DIRECT TEST")
    print("="*60 + "\n")

    asyncio.run(test_kyutai_direct())
