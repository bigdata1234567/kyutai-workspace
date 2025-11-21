#!/usr/bin/env python3
"""TTS Time-To-First-Audio (TTFA) latency test"""
import asyncio
import websockets
import msgpack
import time
import statistics

async def measure_ttfa(text: str) -> float:
    """
    Measure Time-To-First-Audio: time from sending first text chunk
    to receiving first audio chunk
    """
    uri = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
    headers = {"kyutai-api-key": "public_token"}

    try:
        async with websockets.connect(uri, additional_headers=headers) as ws:
            # Send first word
            send_time = time.time()
            await ws.send(msgpack.packb({"type": "Text", "text": text.split()[0] + " "}))

            # Wait for first audio chunk
            first_audio_time = None
            async for message_bytes in ws:
                msg = msgpack.unpackb(message_bytes)
                if msg["type"] == "Audio":
                    first_audio_time = time.time()
                    break

            if first_audio_time is None:
                return None

            ttfa = (first_audio_time - send_time) * 1000  # Convert to ms
            return ttfa
    except Exception as e:
        print(f"Error: {e}")
        return None

async def run_ttfa_tests():
    """Run multiple TTFA measurements"""
    texts = [
        "Bonjour",
        "Comment allez vous?",
        "Ceci est un test de latence.",
        "Le serveur TTS est très rapide.",
        "Je mesure le temps pour la première audio.",
    ]

    ttfa_results = []

    print("Measuring Time-To-First-Audio (TTFA) latency...\n")
    print("TTFA = time from sending first text to receiving first audio chunk\n")

    for i, text in enumerate(texts, 1):
        ttfa = await measure_ttfa(text)
        if ttfa is not None:
            ttfa_results.append(ttfa)
            print(f"Test {i}: '{text}'")
            print(f"  TTFA: {ttfa:.1f}ms")
        else:
            print(f"Test {i}: Failed")
        await asyncio.sleep(0.5)

    if ttfa_results:
        print("\n" + "="*50)
        print("TTFA Statistics:")
        print(f"  Min:     {min(ttfa_results):.1f}ms")
        print(f"  Max:     {max(ttfa_results):.1f}ms")
        print(f"  Mean:    {statistics.mean(ttfa_results):.1f}ms")
        print(f"  Median:  {statistics.median(ttfa_results):.1f}ms")
        if len(ttfa_results) > 1:
            print(f"  StdDev:  {statistics.stdev(ttfa_results):.1f}ms")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(run_ttfa_tests())
