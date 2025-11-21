#!/usr/bin/env python3
"""Measure TTFA with concurrent clients (batch mode)"""
import asyncio
import websockets
import msgpack
import time
from typing import List, Tuple

async def measure_ttfa_client(client_id: int, text: str) -> Tuple[int, float, str]:
    """Measure TTFA for a single client"""
    uri = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
    headers = {"kyutai-api-key": "public_token"}

    try:
        async with websockets.connect(uri, additional_headers=headers, ping_interval=None, close_timeout=1) as ws:
            send_time = time.time()

            # Send text
            await ws.send(msgpack.packb({"type": "Text", "text": text}))

            # Signal end of stream
            await ws.send(msgpack.packb({"type": "Eos"}))

            # Wait for first audio chunk
            try:
                while True:
                    msg_data = await asyncio.wait_for(ws.recv(), timeout=15.0)
                    msg = msgpack.unpackb(msg_data)

                    if msg.get("type") == "Audio":
                        recv_time = time.time()
                        ttfa_ms = (recv_time - send_time) * 1000
                        return (client_id, ttfa_ms, text[:30])

            except asyncio.TimeoutError:
                return (client_id, None, text[:30])

    except Exception as e:
        print(f"❌ Client {client_id} error: {e}")
        return (client_id, None, text[:30])


async def test_concurrent_clients(num_clients: int, text: str = "Bonjour"):
    """Test TTFA with multiple concurrent clients"""
    print(f"\n{'='*80}")
    print(f"Testing TTFA with {num_clients} concurrent clients")
    print(f"Text: '{text}'")
    print(f"{'='*80}\n")

    # Create concurrent tasks
    tasks = [measure_ttfa_client(i, text) for i in range(num_clients)]

    # Launch all simultaneously and measure total time
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    # Process results
    successful = [(cid, ttfa, txt) for cid, ttfa, txt in results if ttfa is not None]
    failed = [(cid, txt) for cid, ttfa, txt in results if ttfa is None]

    print(f"\n{'Client':<8} {'TTFA (ms)':<12} {'Text':<35}")
    print("-" * 55)
    for client_id, ttfa, text_preview in sorted(successful):
        print(f"{client_id:<8} {ttfa:<12.1f} {text_preview:<35}")

    if failed:
        print(f"\n⚠️  Failed clients: {[cid for cid, _ in failed]}")

    if successful:
        ttfas = [ttfa for _, ttfa, _ in successful]
        print(f"\n{'='*55}")
        print(f"Results ({len(successful)}/{num_clients} successful):")
        print(f"  Min TTFA:     {min(ttfas):.1f}ms")
        print(f"  Max TTFA:     {max(ttfas):.1f}ms")
        print(f"  Mean TTFA:    {sum(ttfas)/len(ttfas):.1f}ms")
        print(f"  Total time:   {total_time:.1f}s (all clients in parallel)")
        print(f"  Latency increase: {max(ttfas) - min(ttfas):.1f}ms")

        # Analysis
        if max(ttfas) - min(ttfas) < 50:
            verdict = "✅ Very stable - server handles concurrency well"
        elif max(ttfas) - min(ttfas) < 100:
            verdict = "⚠️  Moderate - slight latency increase with concurrency"
        else:
            verdict = "❌ Degraded - significant latency increase under load"

        print(f"\n{verdict}")


async def main():
    """Run concurrent tests with increasing client counts"""
    test_cases = [
        (1, "Bonjour"),
        (5, "Bonjour"),
        (10, "Bonjour"),
        (20, "Bonjour"),
    ]

    for num_clients, text in test_cases:
        await test_concurrent_clients(num_clients, text)
        await asyncio.sleep(2)  # Wait between test cases

    print(f"\n{'='*80}")
    print("Concurrent testing complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
