#!/usr/bin/env python3
"""Measure TTFA with varied text lengths"""
import asyncio
import websockets
import msgpack
import time

async def measure_ttfa(text: str) -> float:
    """Measure TTFA for a given text"""
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
                        return ttfa_ms

            except asyncio.TimeoutError:
                return None

    except Exception as e:
        print(f"Error with text '{text[:50]}...': {e}")
        return None

async def test_varied_texts():
    """Test TTFA with different text lengths"""
    texts = [
        # Short
        "Bonjour",
        "Hello world",
        "Coucou",
        # Medium
        "Bonjour, comment allez-vous aujourd'hui?",
        "Le serveur TTS fonctionne très bien avec une latence rapide.",
        "Je suis un assistant virtuel et je peux parler français et anglais.",
        # Long
        "Bonjour à vous. Je suis heureux de vous présenter ce serveur de synthèse vocale ultra-rapide qui utilise l'intelligence artificielle pour convertir du texte en parole.",
        "Le Kyutai TTS est un modèle de synthèse vocale très avancé qui peut générer de la parole naturelle et fluide en plusieurs langues avec une très basse latence.",
        "Voici un texte plus long pour tester comment la latence change en fonction de la longueur du texte d'entrée. Plus le texte est long, plus il faut de temps pour générer la parole.",
    ]

    print("Testing TTFA with varied text lengths:\n")
    print(f"{'Text':<70} {'Chars':<6} {'Words':<6} {'TTFA (ms)':<10}")
    print("=" * 95)

    results = []
    for text in texts:
        ttfa = await measure_ttfa(text)
        if ttfa is not None:
            results.append((text, ttfa))
            char_count = len(text)
            word_count = len(text.split())
            text_preview = (text[:65] + "...") if len(text) > 65 else text
            print(f"{text_preview:<70} {char_count:<6} {word_count:<6} {ttfa:.1f}       ")
        await asyncio.sleep(0.5)

    print("\n" + "=" * 95)
    if results:
        ttfas = [ttfa for _, ttfa in results]
        print(f"Min TTFA:  {min(ttfas):.1f}ms")
        print(f"Max TTFA:  {max(ttfas):.1f}ms")
        print(f"Mean TTFA: {sum(ttfas)/len(ttfas):.1f}ms")
        print(f"\n📊 Observation: TTFA is {'relatively stable' if (max(ttfas) - min(ttfas)) < 100 else 'variable'} across text lengths")

if __name__ == "__main__":
    asyncio.run(test_varied_texts())
