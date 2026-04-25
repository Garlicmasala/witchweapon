#!/usr/bin/env python3
"""
Quick web server launcher for Witch's Weapon.
Run this file directly to start the game on a web server.

Usage:
    python quick_web.py              # Start on http://localhost:5000
    PORT=8080 python quick_web.py    # Start on http://localhost:8080
"""

import os
import sys
import subprocess

def main():
    # Ensure dependencies
    print("🧙‍♀️ Witch's Weapon - Web Edition")
    print("=" * 50)
    
    try:
        import flask
        print("✓ Flask is installed")
    except ImportError:
        print("📦 Installing Flask...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "flask"], check=True)
        print("✓ Flask installed")
    
    # Get port
    port = os.environ.get('PORT', '5000')
    print(f"🌐 Starting web server on port {port}...")
    print(f"📖 Open http://localhost:{port} in your browser")
    print("=" * 50)
    
    # Import and run
    from web_app import app
    app.run(host='0.0.0.0', port=int(port), debug=False, threaded=True)

if __name__ == '__main__':
    main()
