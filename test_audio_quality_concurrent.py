#!/usr/bin/env python3
"""
Test audio quality with concurrent clients
Generates WAV files to compare quality degradation under load
"""
import asyncio
import websockets
import msgpack
import time
import os
import wave
import struct

# Create output directory
OUTPUT_DIR = "audio_quality_tests"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Text to synthesize (3 phrases, fairly long)
LONG_TEXT = """Bonjour à vous tous. Je suis ravi de vous présenter ce serveur de synthèse vocale ultra-rapide.
Cet système utilise l'intelligence artificielle pour convertir du texte en parole naturelle et fluide.
La qualité audio est excellente et la latence est minimale pour une expérience utilisateur optimale."""

# Configuration
URI = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
HEADERS = {"kyutai-api-key": "public_token"}
SAMPLE_RATE = 24000  # 24 kHz

async def get_audio_from_server(client_id: int, text: str) -> bytes:
    """Get audio from TTS server and return raw PCM bytes"""
    audio_data = b""

    try:
        async with websockets.connect(URI, additional_headers=HEADERS,
                                     ping_interval=None) as ws:
            # Send text
            await ws.send(msgpack.packb({"type": "Text", "text": text}))

            # Signal end of stream
            await ws.send(msgpack.packb({"type": "Eos"}))

            # Collect all audio chunks
            async for message_bytes in ws:
                msg = msgpack.unpackb(message_bytes)

                if msg.get("type") == "Audio":
                    pcm_data = msg.get("pcm", b"")
                    # Handle both bytes and list types
                    if isinstance(pcm_data, list):
                        # Convert list of integers to bytes (signed 16-bit)
                        try:
                            pcm_data = struct.pack('<' + 'h' * len(pcm_data), *[int(x) for x in pcm_data])
                        except (struct.error, ValueError, TypeError):
                            # If conversion fails, skip this chunk
                            continue
                    elif isinstance(pcm_data, bytes):
                        pass  # Already in correct format
                    else:
                        continue
                    audio_data += pcm_data

    except Exception as e:
        print(f"❌ Client {client_id} error: {e}")
        return b""

    return audio_data

def save_wav(filename: str, audio_data: bytes, sample_rate: int = SAMPLE_RATE):
    """Save raw PCM audio to WAV file"""
    if not audio_data:
        print(f"⚠️  No audio data for {filename}")
        return False

    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        with wave.open(filepath, 'wb') as wav_file:
            # Audio format: 1 channel, 2 bytes per sample (16-bit), PCM
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)

        file_size_kb = os.path.getsize(filepath) / 1024
        duration = len(audio_data) / (sample_rate * 2)  # 2 bytes per sample

        print(f"✅ {filename}")
        print(f"   Size: {file_size_kb:.1f} KB, Duration: {duration:.1f}s")
        return True
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return False

async def test_single_client():
    """Test with 1 concurrent client (baseline)"""
    print("\n" + "="*70)
    print("TEST 1: Single Client (Baseline Quality)")
    print("="*70)

    start_time = time.time()
    print(f"Generating audio (this may take a minute)...")

    audio = await get_audio_from_server(1, LONG_TEXT)

    elapsed = time.time() - start_time

    filename = f"01_single_client_{elapsed:.1f}s.wav"
    success = save_wav(filename, audio)

    if success:
        print(f"⏱️  Time: {elapsed:.1f}s")

    return success

async def test_concurrent_clients(num_clients: int):
    """Test with N concurrent clients"""
    print("\n" + "="*70)
    print(f"TEST: {num_clients} Concurrent Clients")
    print("="*70)

    start_time = time.time()
    print(f"Generating {num_clients} audio streams simultaneously...")

    # Launch all clients at once
    tasks = [get_audio_from_server(i, LONG_TEXT) for i in range(num_clients)]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time

    # Save each audio
    successful = 0
    for i, audio in enumerate(results):
        filename = f"{num_clients:02d}_concurrent_client_{i+1:02d}_{elapsed:.1f}s.wav"
        if save_wav(filename, audio):
            successful += 1

    print(f"\n📊 Results: {successful}/{num_clients} successful")
    print(f"⏱️  Total time: {elapsed:.1f}s (all in parallel)")
    print(f"⏱️  Average per client: {elapsed:.1f}s")

    return successful == num_clients

async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  Audio Quality Testing - Concurrent Clients Analysis".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"📝 Text length: {len(LONG_TEXT)} characters")
    print(f"🎙️  Voice: French (Voice 14 - optimal)")
    print(f"📊 Sample rate: {SAMPLE_RATE} Hz")

    # Run tests
    await test_single_client()
    await test_concurrent_clients(5)
    await test_concurrent_clients(7)

    print("\n" + "="*70)
    print("✅ All tests complete!")
    print("="*70)
    print(f"\n📂 Audio files saved in: {OUTPUT_DIR}/")
    print("\n💡 How to compare quality:")
    print("   1. Listen to 01_single_client_*.wav (baseline - best quality)")
    print("   2. Listen to 05_concurrent_client_*.wav (5 clients - some degradation?)")
    print("   3. Listen to 07_concurrent_client_*.wav (7 clients - more degradation?)")
    print("\n📌 Look for:")
    print("   - Artifacts or distortion")
    print("   - Clarity of speech")
    print("   - Overall volume levels")
    print("   - Any differences in prosody or naturalness")
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(main())
