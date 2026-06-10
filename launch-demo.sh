#!/bin/bash
# Days Legacy AI OS — Lanceur démo HTTPS
# Usage : ./launch-demo.sh
# Arrêt : Ctrl+C (termine backend + tunnel proprement)

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$DIR/backend"
PORT=8000

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Days Legacy AI OS — Lanceur Démo HTTPS                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Vérifie le venv
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "❌ Environnement Python non trouvé. Lance d'abord :"
    echo "   cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Vérifie .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "⚠️  Fichier .env manquant. Création d'un .env par défaut pour la démo..."
    cat > "$BACKEND_DIR/.env" << 'EOF'
DATABASE_URL=sqlite:///./dayslegacy_demo.db
ADMIN_PASSWORD=DL-Demo-2026!Secure
JWT_SECRET=ef8a9c2b1d4e5f60718293a4b5c6d7e8f901234567890abcdef1234567890abcd
OPENAI_API_KEY=sk-dummy-demo
BASE_URL=http://localhost:8000
EOF
    echo "✅ .env créé. Mot de passe admin : DL-Demo-2026!Secure"
fi

# Vérifie cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared non installé. Installe-le avec :"
    echo "   curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg"
    echo "   echo 'deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main' | sudo tee /etc/apt/sources.list.d/cloudflared.list"
    echo "   sudo apt update && sudo apt install cloudflared"
    exit 1
fi

echo "🚀 Démarrage du backend sur le port $PORT..."
cd "$BACKEND_DIR"
source venv/bin/activate

# Tue un ancien process sur le port si besoin
OLD_PID=$(lsof -t -i:$PORT 2>/dev/null || true)
if [ -n "$OLD_PID" ]; then
    echo "   🧹 Nettoyage ancien process (PID $OLD_PID)"
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
fi

# Lance le backend en background
uvicorn main:app --host 0.0.0.0 --port $PORT > /tmp/dayslegacy-backend.log 2>&1 &
BACK_PID=$!

# Attend que le backend réponde
echo "⏳ Attente du backend..."
for i in {1..30}; do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✅ Backend prêt (PID $BACK_PID)"
        break
    fi
    sleep 0.5
    if [ $i -eq 30 ]; then
        echo "❌ Le backend ne démarre pas. Logs :"
        tail -20 /tmp/dayslegacy-backend.log
        exit 1
    fi
done

echo ""
echo "🔒 Création du tunnel HTTPS (cloudflared)..."
echo "   Cela prend 5-10 secondes..."
echo ""

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt en cours..."
    kill $CF_PID 2>/dev/null || true
    kill $BACK_PID 2>/dev/null || true
    wait $BACK_PID 2>/dev/null || true
    echo "✅ Terminé."
    exit 0
}
trap cleanup INT TERM EXIT

# Lance cloudflared et capture l'URL
cloudflared tunnel --url "http://localhost:$PORT" 2>&1 | while IFS= read -r line; do
    echo "$line"
    if [[ "$line" == *"trycloudflare.com"* ]]; then
        URL=$(echo "$line" | grep -oP 'https://[^\s]+\.trycloudflare\.com')
        if [ -n "$URL" ]; then
            echo ""
            echo "═══════════════════════════════════════════════════════════════"
            echo "  🌐 DÉMO HTTPS PRÊTE"
            echo ""
            echo "  👉 Mode démo (sans mot de passe) :"
            echo "     $URL/dashboard?demo=1"
            echo ""
            echo "  👉 Mode production (login requis) :"
            echo "     $URL/dashboard"
            echo ""
            echo "  📱 Teste aussi sur ton téléphone avec cette même URL."
            echo "═══════════════════════════════════════════════════════════════"
            echo ""
            echo "🟢 Serveur actif. Appuie sur Ctrl+C pour arrêter."
        fi
    fi
done &
CF_PID=$!

# Attend indéfiniment
wait $CF_PID
