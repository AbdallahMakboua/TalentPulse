#!/usr/bin/env bash
set -euo pipefail

echo "🚀 TalentPulse Bootstrap"
echo "========================"

# ── 1. Copy .env if missing ────────────────────────────────────────
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
fi

# ── 2. Check Ollama ────────────────────────────────────────────────
OLLAMA_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.1:8b}"

echo ""
echo "🔍 Checking Ollama at $OLLAMA_URL ..."

OLLAMA_AVAILABLE=false
if curl -s --connect-timeout 3 "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama is running"
    OLLAMA_AVAILABLE=true

    # Check if model exists
    if curl -s "$OLLAMA_URL/api/tags" | grep -q "$OLLAMA_MODEL"; then
        echo "✅ Model $OLLAMA_MODEL is available"
    else
        echo "📥 Pulling model $OLLAMA_MODEL (this may take a while)..."
        curl -s "$OLLAMA_URL/api/pull" -d "{\"name\": \"$OLLAMA_MODEL\"}" > /dev/null 2>&1 &
        echo "   Pull started in background. LLM features will be available once complete."
    fi
else
    echo "⚠️  Ollama not reachable at $OLLAMA_URL"
    echo "   → TalentPulse will run in TEMPLATE FALLBACK mode"
    echo "   → Install: brew install ollama && ollama serve"
    echo ""
fi

# ── 3. Bring up Docker Compose ─────────────────────────────────────
echo ""
echo "🐳 Starting Docker services..."
docker compose up -d --build

# ── 4. Wait for API ────────────────────────────────────────────────
echo ""
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy"
        break
    fi
    sleep 2
done

# ── 5. Seed demo data ──────────────────────────────────────────────
echo ""
echo "🌱 Seeding demo data..."
curl -s -X POST http://localhost:8000/sync/run | python3 -m json.tool 2>/dev/null || \
    curl -s -X POST http://localhost:8000/sync/run

echo ""
echo "════════════════════════════════════════════"
echo "🎉 TalentPulse is ready!"
echo ""
echo "   🖥  Dashboard:  http://localhost:3000"
echo "   📡 API docs:   http://localhost:8000/docs"
echo "   ❤️  Health:     http://localhost:8000/health"
echo ""
if [ "$OLLAMA_AVAILABLE" = true ]; then
    echo "   🤖 Ollama:     Connected (LLM features active)"
else
    echo "   🤖 Ollama:     Not connected (template fallback active)"
fi
echo "════════════════════════════════════════════"
