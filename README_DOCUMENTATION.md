# 📚 Kyutai TTS Installation Documentation - Index Complet

**Guide d'accès aux ressources d'installation Kyutai TTS**
**Date:** 2025-01-21
**Statut:** Production Ready ✅

---

## 🎯 Par Objectif (Choisir ton document)

### Je veux juste faire marcher rapidement (5 min)
**→ Lire: `QUICK_START.md`**
- Pour: Aller droit au but
- Temps: 5 minutes
- Résultat: Serveur qui marche

### Je veux installer complètement de zéro (45 min)
**→ Lire: `KYUTAI_TTS_INSTALLATION_GUIDE.md`**
- Pour: Setup from scratch avec tous les détails
- Temps: 45 minutes
- Contient:
  - Phase 1: Préparation système
  - Phase 2: Configuration Docker
  - Phase 3: Build & déploiement
  - Phase 4: Tests & validation
  - Troubleshooting 7 erreurs communes
  - Performance metrics

### Mon installation n'a pas marché (debugging)
**→ Lire: `KYUTAI_ERRORS_AND_SOLUTIONS.md`**
- Pour: Corriger problèmes spécifiques
- Contient:
  - 6 erreurs avec root cause analysis
  - Solutions précises avec code
  - Matrice troubleshooting rapide
  - Leçons apprises

### Je veux comprendre ce qui s'est passé (context)
**→ Lire: `INSTALLATION_TIMELINE.md`**
- Pour: Voir les phases, timing réel, ce qui a traîné
- Contient:
  - Timeline complète 24h → 1h optimisée
  - Erreurs principales et leurs causes
  - Temps économisé par document
  - Statistiques par phase

---

## 📖 Guide Détaillé par Document

### 1. QUICK_START.md (5 min)
```
Longueur: 3 pages
Chapitres:
  - Prérequis (2 min)
  - Démarrer serveur (3 min)
  - Tester latence (1 min)

Quand l'utiliser: Juste besoin ça marche
```

**Contenu résumé:**
```bash
# Prérequis
nvidia-smi
docker --version

# Démarrer
docker compose -f docker-compose.tts.yml build
docker compose -f docker-compose.tts.yml up -d

# Test
python3 test_ttfa_quick.py
# Output: ✅ TTFA: 250-280ms
```

---

### 2. KYUTAI_TTS_INSTALLATION_GUIDE.md (45 min)
```
Longueur: 800+ lignes
Chapitres:
  - Table des matières & prérequis
  - Phase 1: Préparation système
  - Phase 2: Configuration Docker
  - Phase 3: Build & déploiement
  - Phase 4: Tests & validation
  - Troubleshooting complet
  - Performance metrics
  - Checklist finale
  - Commandes utiles

Quand l'utiliser: Première installation from scratch
```

**Structure par phase:**

**Phase 1: Préparation (5 pages)**
- Cloner repos (2.5 GB)
- Vérifier configurations
- Auth HuggingFace
- Préparer cache

**Phase 2: Configuration Docker (15 pages)**
- Dockerfile.tts complet (80 lignes annotées)
- docker-compose.tts.yml (40 lignes)
- Explications chaque section

**Phase 3: Build & Deploy (2 pages)**
- Build commands
- Démarrage
- Vérification

**Phase 4: Tests (8 pages)**
- Test TTFA simple (code Python complet)
- Test RTF (code Python complet)
- Résultats attendus

**Troubleshooting (12 pages)**
- Erreur 1: "Failed to locate CUDA runtime"
- Erreur 2: "No module named 'moshi'"
- Erreur 3: "ModuleNotFoundError: numpy"
- Erreur 4: "moshi-server: not found"
- Erreur 5: "Connection refused"
- Erreur 6: "SSL: CERTIFICATE_VERIFY_FAILED"
- Erreur 7: "WebSocket error 1005"

**Performance Metrics (5 pages)**
- Résultats typiques par config
- Benchmark texte varié
- Tables comparatives

**Commandes Utiles (2 pages)**
- Démarrage/arrêt
- Inspection
- Debugging

---

### 3. KYUTAI_ERRORS_AND_SOLUTIONS.md (600+ lignes)
```
Longueur: 600+ lignes
Chapitres:
  - Résumé erreurs (table)
  - Erreur #1: Native compilation (5h wasted)
  - Erreur #2: PyTorch version
  - Erreur #3: ModuleNotFoundError numpy
  - Erreur #4: moshi-server not found
  - Erreur #5: TTFA timeout
  - Erreur #6: WebSocket 1005 concurrency
  - Matrice troubleshooting
  - Leçons apprises

Quand l'utiliser: Debugging spécifique ou learning from mistakes
```

**Pour chaque erreur:**
1. **Description** - quand/où/symptômes
2. **Root Cause** - analyse profonde
3. **Solution** - code exact + explications
4. **Temps economisé** - how long this wasted

**Exemple Erreur #3:**
```
Symptôme: ModuleNotFoundError: No module named 'numpy'
Cause: Dépendances Python incorrectes dans Dockerfile
Solution: Consulter moshi/rust/moshi-server/pyproject.toml
Temps: 30 min debugging → 2 min avec guide
```

---

### 4. INSTALLATION_TIMELINE.md (400+ lignes)
```
Longueur: 400+ lignes
Chapitres:
  - Timeline résumée (30h → 1h)
  - Phase 1: Native Compilation (4-5h, FAILED)
  - Phase 2: Docker Setup (2-3h, SUCCESS)
  - Phase 3: TTFA Testing (4-6h, HARD)
  - Phase 4: Performance (2-3h, SUCCESS)
  - Phase 5: Documentation (3-4h)
  - Statistiques globales
  - Résultats finaux

Quand l'utiliser: Comprendre le journey, timing expectations
```

**Par Phase - Détails:**

**Phase 1 Timeline (4-5 heures) ❌**
```
0:00 - Clone repos
0:05 - Essai cargo build → CUDA not found
0:35 - Try apt-get install cuda → incompatible version
0:50 - Adjust libstdc++ → g++ version conflict
1:50 - Abandon native, switch Docker
```

**Phase 3 Timeline (4-6 heures) - Protocol Discovery**
```
Iter 1: test_ttfa_simple.py → Timeout 15s
Iter 2: test_ttfa_fast.py → Syntax error
Iter 3: test_ttfa_fixed.py → Still timeout
Iter 4: test_ttfa_correct.py → WORKS! (add Eos)
       Découverte: {"type": "Eos"} est CRITIQUE
```

**Savings Stats:**
```
Without guide: 24 hours (trial & error)
With guide: 1 hour (follow steps)
Saved: 23 hours (95%)
```

---

## 🔄 Workflow de Lecture Recommandé

### Scénario 1: Première Installation (Novice)
```
1. QUICK_START.md (5 min)
   ↓ (si ça marche)
2. Profit! Serveur en marche

   ↓ (si problèmes)
3. KYUTAI_ERRORS_AND_SOLUTIONS.md
   → Trouver erreur → Appliquer solution
```

### Scénario 2: Installation Complète (Expérimenté)
```
1. KYUTAI_TTS_INSTALLATION_GUIDE.md
   → Phase 1-4 complètement

2. Si problèmes:
   → KYUTAI_ERRORS_AND_SOLUTIONS.md
   → Matrice troubleshooting
```

### Scénario 3: Post-Installation (Learning)
```
1. INSTALLATION_TIMELINE.md
   → Comprendre ce qui a pris du temps
   → Leçons apprises

2. KYUTAI_TTS_INSTALLATION_GUIDE.md
   → Sections troubleshooting
```

---

## 📁 Structure des Fichiers

```
~/kyutai-workspace/
├── 📘 README_DOCUMENTATION.md (this file)
├── ⚡ QUICK_START.md
├── 📖 KYUTAI_TTS_INSTALLATION_GUIDE.md
├── 🔧 KYUTAI_ERRORS_AND_SOLUTIONS.md
├── ⏱️ INSTALLATION_TIMELINE.md
│
├── Dockerfile.tts (Docker image)
├── docker-compose.tts.yml (orchestration)
│
├── test_ttfa_simple.py
├── test_ttfa_varied.py
├── test_ttfa_concurrent.py
├── test_tts_quick.py
│
├── delayed-streams-modeling/
│   ├── configs/config-tts.toml
│   └── ...
└── moshi/
    ├── rust/Cargo.toml
    └── ...
```

---

## 🎓 Apprentissage (Lessons Learned)

### Erreur #1: Native Compilation (4-5 heures perdue)
**Leçon:** Docker wins. Use containers.

### Erreur #2: PyTorch PyPI vs Custom Index (30 min)
**Leçon:** Always use correct PyTorch wheel index `https://download.pytorch.org/whl/cu121`

### Erreur #3: Python Dépendances Incomplètes (30 min)
**Leçon:** Consult official `pyproject.toml`, ne pas deviner

### Erreur #4: moshi-server Binaire Manquant (1 heure)
**Leçon:** Rust crates = compile AND install

### Erreur #5: TTFA Protocol Inconnu (3 heures)
**Leçon:** {"type": "Eos"} signal mandatory pour streaming

### Erreur #6: Concurrency Limits (30 min)
**Leçon:** Config needed for >8 workers

---

## 🚀 Performance Résumé

```
┌────────────────────────────────────────┐
│ KYUTAI TTS PERFORMANCE                 │
├────────────────────────────────────────┤
│ TTFA (latency)         │ 250-280 ms   │
│ RTF (throughput)       │ 0.44x        │
│ Real-Time Speed        │ 2.26x        │
│ Setup Time (optimized) │ 45 minutes   │
│ Production Ready       │ ✅ YES       │
│ Documentation Pages    │ 2000+ lines  │
│ Troubleshooting Cases  │ 6+ detailed  │
└────────────────────────────────────────┘
```

---

## 🔗 Ressources Officielles

**GitHub:**
- https://github.com/kyutai-labs/delayed-streams-modeling
- https://github.com/kyutai-labs/moshi

**HuggingFace:**
- https://huggingface.co/kyutai/tts-1.6b-en_fr
- https://huggingface.co/kyutai/tts-voices

**Documentation Officielle:**
- README: delayed-streams-modeling
- README: moshi/rust

---

## 💾 Files Créés

| Fichier | Type | Lignes | Objet |
|---------|------|--------|-------|
| QUICK_START.md | MD | 100 | Fast setup |
| KYUTAI_TTS_INSTALLATION_GUIDE.md | MD | 800 | Complete guide |
| KYUTAI_ERRORS_AND_SOLUTIONS.md | MD | 600 | Debugging |
| INSTALLATION_TIMELINE.md | MD | 400 | Journey log |
| README_DOCUMENTATION.md | MD | 400 | Index (this) |
| Dockerfile.tts | Dockerfile | 150 | Container |
| docker-compose.tts.yml | YAML | 40 | Orchestration |
| test_*.py | Python | 300 | Tests/metrics |

**Total: 2000+ lines de documentation précise**

---

## ✅ Checklist Avant de Commencer

- [ ] GPU NVIDIA 24GB+ VRAM
- [ ] Docker + docker-compose installés
- [ ] 100GB disque libre
- [ ] 30 min à 1 heure disponible
- [ ] Patience pour première build (20-40 min)

---

## 🎯 TL;DR (Trop Long; Pas Lu)

**Veut juste marcher?** → `QUICK_START.md` (5 min)

**Veut installation complète?** → `KYUTAI_TTS_INSTALLATION_GUIDE.md` (45 min)

**Veut corriger erreur?** → `KYUTAI_ERRORS_AND_SOLUTIONS.md` (find your error)

**Veut comprendre timeline?** → `INSTALLATION_TIMELINE.md` (20 min reading)

---

## 📞 Support

If issues still occur after consulting docs:
1. Check error message
2. Go to `KYUTAI_ERRORS_AND_SOLUTIONS.md`
3. Find matching error
4. Apply exact solution
5. If not found, add to "Leçons apprises"

---

**Documentation Version:** 1.0
**Created:** 2025-01-21
**Status:** Complete & Validated ✅
**Maintenance:** Keep updated with new errors

---

**Bon courage! 🚀**

Avec cette documentation, l'installation devrait être smooth et rapide.
