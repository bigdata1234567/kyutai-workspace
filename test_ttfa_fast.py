#!/usr/bin/env python3
"""Fast TTFA measurement with timeout"""
import asyncio
import websockets
import msgpack
import time
import sys

async def measure_ttfa():
    uri = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
    headers = {"kyutai-api-key": "public_token"}

    try:
        async with websockets.connect(uri, additional_headers=headers, ping_interval=None, close_timeout=1) as ws:
            send_time = time.time()
            print(f"Sending 'Bonjour'", flush=True)

            # Send text
            await ws.send(msgpack.packb({"type": "Text", "text": "Bonjour"}))

            # Wait for first audio with timeout
            try:
                async for message_bytes in asyncio.wait_for(ws.__aiter__().__anext__(), timeout=5):
                    break
            except asyncio.TimeoutError:
                pass

            # Actually receive one message
            try:
                msg_data = await asyncio.wait_for(ws.recv(), timeout=10)
                msg = msgpack.unpackb(msg_data)
                recv_time = time.time()

                if msg["type"] == "Audio":
                    ttfa = (recv_time - send_time) * 1000
                    print(f"First audio received after: {ttfa:.1f}ms")
                    return ttfa

            except asyncio.TimeoutError:
                print("No audio received within 10s timeout")
                return None

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(measure_ttfa())
    if result:
        print(f"\n✅ TTFA: {result:.1f}ms")
    else:
        print("\n❌ Failed to measure TTFA")
