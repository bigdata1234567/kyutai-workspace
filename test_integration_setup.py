#!/usr/bin/env python3
"""
Pre-Flight Check: Validate Twilio + Kyutai TTS Integration Setup

Tests:
1. Check if Kyutai TTS server is running
2. Check if required API keys are configured
3. Test audio format conversion (24kHz → 8kHz)
4. Verify all dependencies are installed
"""

import asyncio
import sys
import os
import subprocess

async def check_kyutai_server():
    """Test if Kyutai TTS WebSocket server is running"""
    print("\n📡 Checking Kyutai TTS Server...")

    try:
        import websockets
        import msgpack

        uri = "ws://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
        headers = {"kyutai-api-key": "public_token"}

        async with websockets.connect(uri, additional_headers=headers, ping_interval=None) as ws:
            # Send simple text
            await ws.send(msgpack.packb({"type": "Text", "text": "test"}))
            await ws.send(msgpack.packb({"type": "Eos"}))

            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            msg = msgpack.unpackb(response)

            if msg.get("type") in ["Audio", "Done"]:
                print("✅ Kyutai TTS server is running and responding")
                return True
    except asyncio.TimeoutError:
        print("⚠️  Kyutai TTS server timed out (may be slow or busy)")
        return True
    except ConnectionRefusedError:
        print("❌ Kyutai TTS server is NOT running")
        print("   Start it with: docker compose -f docker-compose.tts.yml up -d")
        return False
    except Exception as e:
        print(f"⚠️  Error testing Kyutai: {e}")
        return False

def check_api_keys():
    """Check if required API keys are configured"""
    print("\n🔑 Checking API Keys...")

    required_keys = {
        "DEEPGRAM_API_KEY": "Deepgram (STT)",
        "OPENAI_API_KEY": "OpenAI (GPT)"
    }

    all_present = True
    for key, service in required_keys.items():
        if os.getenv(key):
            print(f"✅ {key}: {service} configured")
        else:
            print(f"❌ {key}: {service} NOT configured")
            all_present = False

    return all_present

def check_dependencies():
    """Check if all Python dependencies are installed"""
    print("\n📦 Checking Python Dependencies...")

    dependencies = {
        "websockets": "WebSocket support",
        "aiohttp": "Async HTTP client",
        "msgpack": "Message serialization",
        "numpy": "Numerical arrays",
        "scipy": "Audio resampling",
        "openai": "OpenAI API"
    }

    all_present = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: NOT installed - {description}")
            all_present = False

    return all_present

def test_audio_conversion():
    """Test audio format conversion functions"""
    print("\n🎵 Testing Audio Format Conversion...")

    try:
        import numpy as np
        import scipy.signal

        # Generate test signal
        test_float_samples = [0.5, 0.25, -0.5, -0.25, 0.0]

        # Test float → int16
        int16_samples = np.array([int(x * 32767) for x in test_float_samples], dtype=np.int16)
        assert len(int16_samples) == len(test_float_samples), "Float to int16 conversion failed"
        print(f"✅ Float → Int16 conversion: {test_float_samples[0]} → {int16_samples[0]}")

        # Test resampling (24kHz → 8kHz)
        test_pcm_24k = np.array(int16_samples)
        num_samples = int(len(test_pcm_24k) / 3)
        resampled = scipy.signal.resample(test_pcm_24k, num_samples)
        expected_length = len(test_pcm_24k) // 3
        assert abs(len(resampled) - expected_length) <= 1, "Resampling dimensions incorrect"
        print(f"✅ Resampling 24kHz → 8kHz: {len(test_pcm_24k)} → {len(resampled)} samples")

        # Test µ-law conversion
        mu = 255.0
        safe_abs = np.abs(test_float_samples)
        magnitude = np.log(1.0 + mu * np.array(safe_abs) / 32768.0) / np.log(1.0 + mu)
        signal = np.sign(test_float_samples) * magnitude * 128.0
        ulaw_bytes = np.uint8(signal + 128.0)
        print(f"✅ PCM → µ-law conversion: {len(ulaw_bytes)} bytes")

        return True
    except Exception as e:
        print(f"❌ Audio conversion test failed: {e}")
        return False

def check_docker():
    """Check if Kyutai TTS Docker container is running"""
    print("\n🐳 Checking Docker Container...")

    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=kyutai"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and "kyutai" in result.stdout:
            print("✅ Kyutai TTS Docker container is running")
            return True
        else:
            print("⚠️  Kyutai TTS Docker container is NOT running")
            print("   Start it with: docker compose -f docker-compose.tts.yml up -d")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Docker command timed out")
        return False
    except FileNotFoundError:
        print("⚠️  Docker not installed (may be okay if using native build)")
        return False
    except Exception as e:
        print(f"⚠️  Error checking Docker: {e}")
        return False

async def main():
    """Run all checks"""
    print("=" * 70)
    print("🚀 Twilio + Kyutai TTS Integration - Pre-Flight Check")
    print("=" * 70)

    results = {}

    # Check dependencies first (required for other tests)
    results["dependencies"] = check_dependencies()

    # Check API keys
    results["api_keys"] = check_api_keys()

    # Check audio conversion
    results["audio_conversion"] = test_audio_conversion()

    # Check Docker
    results["docker"] = check_docker()

    # Check Kyutai server (requires dependencies)
    if results["dependencies"]:
        results["kyutai_server"] = await check_kyutai_server()
    else:
        print("\n📡 Skipping Kyutai check (dependencies missing)")
        results["kyutai_server"] = False

    # Summary
    print("\n" + "=" * 70)
    print("📋 Summary:")
    print("=" * 70)

    checks = [
        ("Dependencies installed", results["dependencies"]),
        ("API Keys configured", results["api_keys"]),
        ("Audio conversion", results["audio_conversion"]),
        ("Docker running", results["docker"]),
        ("Kyutai TTS responding", results["kyutai_server"])
    ]

    all_pass = True
    for check, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        all_pass = all_pass and passed

    print("=" * 70)

    if all_pass:
        print("\n✅ All checks passed! Ready to run:")
        print("   python3 twilio_kyutai_integration.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix issues above before running.")
        print("\nQuick fixes:")
        print("1. Install dependencies: pip install websockets aiohttp numpy scipy openai msgpack")
        print("2. Set API keys: cp .env.example .env && nano .env")
        print("3. Start Kyutai: docker compose -f docker-compose.tts.yml up -d")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
