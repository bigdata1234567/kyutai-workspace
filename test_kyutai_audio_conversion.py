#!/usr/bin/env python3
"""
Test audio conversion: Kyutai 24kHz PCM → 8kHz μ-law
This mimics what happens in the TTS handler
"""
import asyncio
import websockets
import msgpack
import numpy as np
import audioop
import time

KYUTAI_TTS_URL = "ws://127.0.0.1:8080/api/tts_streaming"
KYUTAI_API_KEY = "public_token"
KYUTAI_VOICE = "cml-tts/fr/2465_1943_000152-0002.wav"
KYUTAI_FORMAT = "PcmMessagePack"

async def test_kyutai_tts_conversion():
    """Test full TTS pipeline: text → 24kHz PCM → 8kHz μ-law"""

    text = "Bonjour, ceci est un test de conversion audio."
    print(f"📝 Testing with text: '{text}'")

    try:
        uri = f"{KYUTAI_TTS_URL}?voice={KYUTAI_VOICE}&format={KYUTAI_FORMAT}"
        headers = {"kyutai-api-key": KYUTAI_API_KEY}

        async with websockets.connect(uri, additional_headers=headers) as ws:
            start_time = time.time()

            # Send text word by word
            print("📤 Sending text to Kyutai...")
            for word in text.split():
                await ws.send(msgpack.packb({"type": "Text", "text": word + " "}))

            # Signal end
            await ws.send(msgpack.packb({"type": "Eos"}))

            # Receive audio chunks
            print("📥 Receiving audio from Kyutai...")
            audio_chunks = []
            async for message_bytes in ws:
                msg = msgpack.unpackb(message_bytes)
                if msg.get("type") == "Audio":
                    pcm_data = msg.get("pcm")
                    if pcm_data is not None:
                        audio_chunks.append(pcm_data)

            ttfa = (time.time() - start_time) * 1000
            print(f"⏱️ TTFA: {ttfa:.1f}ms")
            print(f"📊 Received {len(audio_chunks)} chunks")

            if not audio_chunks:
                print("❌ No audio chunks received!")
                return

            # Concatenate chunks
            pcm_24k = np.concatenate(audio_chunks, axis=0)
            print(f"✅ Kyutai output: {len(pcm_24k)} samples @ 24kHz")
            print(f"   Duration: {len(pcm_24k)/24000:.3f}s")
            print(f"   Data type: {pcm_24k.dtype}, Min: {pcm_24k.min():.3f}, Max: {pcm_24k.max():.3f}")

            # Convert float32 [-1, 1] to int16
            print("\n🔄 Converting float32 → int16...")
            pcm_int16 = (pcm_24k * 32767).astype(np.int16)
            print(f"✅ int16: {len(pcm_int16)} samples, Min: {pcm_int16.min()}, Max: {pcm_int16.max()}")

            pcm_int16_bytes = pcm_int16.tobytes()
            print(f"   Bytes: {len(pcm_int16_bytes)}")

            # Resample 24kHz → 8kHz
            print("\n🔄 Resampling 24kHz → 8kHz...")
            pcm_8k, _ = audioop.ratecv(pcm_int16_bytes, 2, 1, 24000, 8000, None)
            print(f"✅ 8kHz: {len(pcm_8k)} bytes")
            print(f"   Expected: {len(pcm_24k)//3} bytes (24kHz/3)")
            print(f"   Samples @ 8kHz: {len(pcm_8k)//2}")
            print(f"   Duration @ 8kHz: {(len(pcm_8k)//2)/8000:.3f}s")

            # Convert to μ-law
            print("\n🔄 Converting to μ-law...")
            pcm_mulaw = audioop.lin2ulaw(pcm_8k, 2)
            print(f"✅ μ-law: {len(pcm_mulaw)} bytes")
            print(f"   Expected: {len(pcm_8k)//2} bytes (1 byte per sample)")

            # Chunk for Twilio
            chunk_size = 160  # 20ms @ 8kHz
            num_chunks = len(pcm_mulaw) // chunk_size
            print(f"\n📦 Chunking for Twilio...")
            print(f"✅ {num_chunks} chunks of {chunk_size} bytes (20ms each)")
            print(f"   Total duration: {num_chunks * 0.02:.3f}s")

            print("\n✅ All conversions successful!")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_kyutai_tts_conversion())
    exit(0 if result else 1)
