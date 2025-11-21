#!/usr/bin/env python3
"""Quick TTS speed test"""
import asyncio
import websockets
import msgpack
import time

async def test_tts_speed():
    """Test TTS latency and speed"""
    uri = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
    headers = {"kyutai-api-key": "public_token"}

    text = "Bonjour, ceci est un test de latence du serveur TTS Kyutai."

    try:
        async with websockets.connect(uri, additional_headers=headers) as ws:
            # Timing
            start = time.time()

            # Send text word by word (streaming like LLM)
            for word in text.split():
                await ws.send(msgpack.packb({"type": "Text", "text": word + " "}))

            # Signal end
            await ws.send(msgpack.packb({"type": "Eos"}))

            # Receive audio
            audio_chunks = []
            async for message_bytes in ws:
                msg = msgpack.unpackb(message_bytes)
                if msg["type"] == "Audio":
                    audio_chunks.append(msg["pcm"])

            elapsed = time.time() - start
            total_audio_samples = sum(len(chunk) for chunk in audio_chunks)
            audio_duration = total_audio_samples / 24000  # 24kHz sampling rate
            rtf = elapsed / audio_duration if audio_duration > 0 else 0

            print(f"✅ TTS Test Results:")
            print(f"   Text: '{text}'")
            print(f"   Total time: {elapsed:.3f}s")
            print(f"   Audio duration: {audio_duration:.3f}s")
            print(f"   RTF (Real-Time Factor): {rtf:.2f}x")
            print(f"   Audio chunks: {len(audio_chunks)}")
            print(f"   Total samples: {total_audio_samples}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tts_speed())
