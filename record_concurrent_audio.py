#!/usr/bin/env python3
"""
Simple script to record audio from concurrent TTS clients
Just focuses on getting WAV files, no complex handling
"""
import asyncio
import websockets
import msgpack
import time
import os
import wave
import struct

# Configuration
OUTPUT_DIR = "audio_quality_tests"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LONG_TEXT = """Bonjour à vous tous. Je suis ravi de vous présenter ce serveur de synthèse vocale ultra-rapide.
Cet système utilise l'intelligence artificielle pour convertir du texte en parole naturelle et fluide.
La qualité audio est excellente et la latence est minimale pour une expérience utilisateur optimale."""

URI = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
HEADERS = {"kyutai-api-key": "public_token"}
SAMPLE_RATE = 24000

async def get_audio_simple(client_id: int, text: str) -> bytes:
    """Simple audio retrieval - just concatenate whatever we get"""
    audio_chunks = []

    try:
        async with websockets.connect(URI, additional_headers=HEADERS, ping_interval=None) as ws:
            # Send text
            await ws.send(msgpack.packb({"type": "Text", "text": text}))
            await ws.send(msgpack.packb({"type": "Eos"}))

            # Collect audio chunks
            while True:
                try:
                    msg_bytes = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    msg = msgpack.unpackb(msg_bytes)

                    if msg.get("type") == "Audio":
                        pcm = msg.get("pcm", b"")
                        if pcm:
                            # PCM is list of floats (0.0-1.0 range) - convert to int16
                            if isinstance(pcm, list):
                                # Convert float [-1.0, 1.0] to int16 [-32768, 32767]
                                int16_data = [int(x * 32767) for x in pcm]
                                pcm = struct.pack('<' + 'h' * len(int16_data), *int16_data)
                            audio_chunks.append(pcm)
                    elif msg.get("type") == "Done":
                        break
                except asyncio.TimeoutError:
                    break
                except Exception as e:
                    print(f"  Error in audio loop: {e}")
                    break

    except Exception as e:
        print(f"❌ Client {client_id}: {e}")
        return b""

    # Concatenate all chunks
    result = b"".join(audio_chunks)
    print(f"✅ Client {client_id}: Got {len(result)} bytes of audio")
    return result

def write_wav(filename: str, audio_data: bytes, sample_rate: int = SAMPLE_RATE) -> bool:
    """Write audio data to WAV file"""
    if not audio_data:
        print(f"  ⚠️  No audio for {filename}")
        return False

    try:
        filepath = os.path.join(OUTPUT_DIR, filename)
        with wave.open(filepath, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(audio_data)

        size_kb = os.path.getsize(filepath) / 1024
        duration_sec = len(audio_data) / (sample_rate * 2)
        print(f"  📝 {filename}: {size_kb:.1f} KB ({duration_sec:.1f}s)")
        return True
    except Exception as e:
        print(f"  ❌ Error writing {filename}: {e}")
        return False

async def test_concurrent(num_clients: int):
    """Test with N concurrent clients"""
    print(f"\n{'='*70}")
    print(f"Testing {num_clients} Concurrent Clients")
    print(f"{'='*70}")

    start = time.time()

    # Launch all clients
    tasks = [get_audio_simple(i, LONG_TEXT) for i in range(num_clients)]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    print(f"Total time: {elapsed:.1f}s\n")

    # Save each audio
    for i, audio_data in enumerate(results):
        filename = f"{num_clients:02d}client_{i+1:02d}.wav"
        write_wav(filename, audio_data)

async def main():
    print("\n" + "="*70)
    print("Audio Quality Testing - Concurrent Clients")
    print("="*70)
    print(f"Output: {OUTPUT_DIR}/")
    print(f"Voice: French (Voice 14 - optimal)")
    print(f"Text: 3 phrases ({len(LONG_TEXT)} chars)")

    # Test 1 client (baseline)
    await test_concurrent(1)

    # Test 5 clients
    await test_concurrent(5)

    # Test 7 clients
    await test_concurrent(7)

    print("\n" + "="*70)
    print("✅ Audio files generated!")
    print("="*70)
    print(f"\nListen to files in: {OUTPUT_DIR}/")
    print("Compare quality between 01client_*.wav, 05client_*.wav, 07client_*.wav")

if __name__ == "__main__":
    asyncio.run(main())
