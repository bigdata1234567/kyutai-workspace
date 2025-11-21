#!/usr/bin/env python3
"""Simple TTFA test - just measure first audio response"""
import asyncio
import websockets
import msgpack
import time

async def test_ttfa_simple():
    """Quick single test to measure TTFA"""
    uri = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
    headers = {"kyutai-api-key": "public_token"}
    text = "Bonjour"

    try:
        async with websockets.connect(uri, additional_headers=headers, ping_interval=None) as ws:
            # Record send time
            send_time = time.time()
            print(f"[{send_time:.3f}] Sending text: '{text}'")

            # Send text
            await ws.send(msgpack.packb({"type": "Text", "text": text}))

            # Wait for first audio response
            start_wait = time.time()
            async for message_bytes in ws:
                msg = msgpack.unpackb(message_bytes)
                recv_time = time.time()

                if msg["type"] == "Audio":
                    ttfa_ms = (recv_time - send_time) * 1000
                    print(f"[{recv_time:.3f}] Received first audio chunk")
                    print(f"\nTTFA (Time-To-First-Audio): {ttfa_ms:.1f}ms")
                    break

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ttfa_simple())
