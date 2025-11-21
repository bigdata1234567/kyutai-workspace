# ⚡ Kyutai TTS - Quick Start (5 min)

**Pour faire marcher le serveur rapidement**

---

## 1️⃣ Prérequis (2 min)

```bash
# Vérifier GPU
nvidia-smi
# Output: NVIDIA-SMI, GPU list

# Vérifier Docker
docker --version
docker compose version

# Aller au répertoire
cd ~/kyutai-workspace
```

---

## 2️⃣ Démarrer le Serveur (3 min)

```bash
# Build l'image Docker (première fois = 20-40 min, après = rapide)
docker compose -f docker-compose.tts.yml build

# Démarrer le serveur
docker compose -f docker-compose.tts.yml up -d

# Attendre 10-15 secondes et vérifier
docker logs kyutai-tts-server | tail -5
# Devrait afficher: "Server ready on 0.0.0.0:8080"

# Test rapide
curl -k https://127.0.0.1:8080/health \
  -H "kyutai-api-key: public_token"
# Output: OK
```

---

## 3️⃣ Tester Latence (1 min)

```bash
# Install dependences
pip install websockets msgpack

# Créer test_ttfa_quick.py:
cat > test_ttfa_quick.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import websockets
import msgpack
import time

async def test():
    uri = "wss://127.0.0.1:8080/api/tts_streaming?voice=cml-tts/fr/2465_1943_000152-0002.wav&format=PcmMessagePack"
    headers = {"kyutai-api-key": "public_token"}

    async with websockets.connect(uri, additional_headers=headers, ssl=False) as ws:
        start = time.time()
        await ws.send(msgpack.packb({"type": "Text", "text": "Bonjour"}))
        await ws.send(msgpack.packb({"type": "Eos"}))

        async for msg_bytes in ws:
            msg = msgpack.unpackb(msg_bytes)
            if msg["type"] == "Audio":
                ttfa = (time.time() - start) * 1000
                print(f"✅ TTFA: {ttfa:.1f}ms")
                break

asyncio.run(test())
EOF

# Exécuter
python3 test_ttfa_quick.py
# Output: ✅ TTFA: 250-280ms
```

---

## ✅ C'est tout!

Le serveur est prêt pour production.

**Performance résumé:**
- TTFA: 250-280ms (latence utilisateur)
- RTF: 0.44x (2.26x temps réel = ultra rapide)
- Concurrency: 5-10 clients stables

---

## 📚 Documentation Complète

Pour détails complets, consulter:
- `KYUTAI_TTS_INSTALLATION_GUIDE.md` (setup complet)
- `KYUTAI_ERRORS_AND_SOLUTIONS.md` (troubleshooting)

---

## 🛑 Arrêter le Serveur

```bash
docker compose -f docker-compose.tts.yml down
```

---

## 🔧 Commandes Utiles

```bash
# Voir logs en direct
docker logs -f kyutai-tts-server

# Voir utilisation GPU
docker exec kyutai-tts-server nvidia-smi

# Redémarrer
docker compose -f docker-compose.tts.yml restart

# Status
docker ps | grep kyutai
```

---

**Durée totale:** ~45 min (première fois, surtout download + build)
**Durée redémarrage:** ~15 secondes
**Status:** Production Ready ✅
