#!/usr/bin/env python3
"""Measure TTFA - Time To First Audio"""
import asyncio
import websockets
import msgpack
import time

async def measure_ttfa():
    uri = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
    headers = {"kyutai-api-key": "public_token"}

    try:
        async with websockets.connect(uri, additional_headers=headers, ping_interval=None, close_timeout=1) as ws:
            send_time = time.time()
            print(f"Sending 'Bonjour'...", flush=True)

            # Send text immediately
            await ws.send(msgpack.packb({"type": "Text", "text": "Bonjour"}))

            # Wait for first audio chunk with timeout
            try:
                msg_data = await asyncio.wait_for(ws.recv(), timeout=10.0)
                msg = msgpack.unpackb(msg_data)
                recv_time = time.time()

                if msg.get("type") == "Audio":
                    ttfa_ms = (recv_time - send_time) * 1000
                    print(f"✅ First audio received")
                    print(f"   TTFA: {ttfa_ms:.1f}ms")
                    return ttfa_ms
                else:
                    print(f"Got {msg.get('type')} message first, waiting for Audio...")
                    # Keep waiting
                    msg_data = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    msg = msgpack.unpackb(msg_data)
                    recv_time = time.time()
                    if msg.get("type") == "Audio":
                        ttfa_ms = (recv_time - send_time) * 1000
                        print(f"✅ First audio received")
                        print(f"   TTFA: {ttfa_ms:.1f}ms")
                        return ttfa_ms

            except asyncio.TimeoutError:
                print("❌ Timeout waiting for audio (>10s)")
                return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    result = asyncio.run(measure_ttfa())
