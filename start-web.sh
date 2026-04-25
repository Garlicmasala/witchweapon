#!/bin/bash
# Quick start script for Witch's Weapon Web Edition

set -e

echo "🧙‍♀️ Witch's Weapon - Web Edition Launcher"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --quiet -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    echo "📋 Loading .env configuration..."
    export $(cat .env | grep -v '#' | xargs)
else
    echo "⚠️  No .env file found. Using defaults."
fi

# Get configuration
PORT=${PORT:-5000}
FLASK_ENV=${FLASK_ENV:-development}

# Clear old output
clear

echo ""
echo "🧙‍♀️ Starting Witch's Weapon Web Server"
echo "====================================="
echo ""
echo "📊 Configuration:"
echo "   ├─ Environment: $FLASK_ENV"
echo "   ├─ Port: $PORT"
echo "   ├─ URL: http://localhost:$PORT"
echo "   └─ API: http://localhost:$PORT/api/status"
echo ""
echo "✨ Features:"
echo "   ├─ Web Platform: Ready"
echo "   ├─ Portability: Integrated"
echo "   ├─ Daily Missions: Active"
echo "   └─ Cross-Platform: Enabled"
echo ""
echo "🌐 Browser Support:"
echo "   ├─ Chrome/Chromium: ✓"
echo "   ├─ Firefox: ✓"
echo "   ├─ Safari: ✓"
echo "   └─ Edge: ✓"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the web app
python web_app.py
