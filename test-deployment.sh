#!/bin/bash
# Test script for Witch's Weapon Web Deployment

echo "🧙‍♀️ Witch's Weapon - Web Deployment Test"
echo "==========================================="
echo ""

# Test 1: Check Python
echo "Test 1: Python Environment"
python3 --version && echo "✓ Python OK" || echo "✗ Python NOT FOUND"
echo ""

# Test 2: Check requirements
echo "Test 2: Dependencies"
if pip list | grep -q "Flask"; then
    echo "✓ Flask installed"
else
    echo "⚠️  Flask not installed. Installing..."
    pip install -r requirements.txt
fi
echo ""

# Test 3: Check Flask app imports
echo "Test 3: Flask App Import"
python3 -c "from flask import Flask; print('✓ Flask import OK')" || echo "✗ Flask import FAILED"
echo ""

# Test 4: Check game modules
echo "Test 4: Game Module Import"
python3 -c "import sys; sys.path.insert(0, 'src'); from PORTABILITY_GUIDE import initialize_game_for_platform; print('✓ Portability module OK')" || echo "✗ Portability module FAILED"
echo ""

# Test 5: Check Docker
echo "Test 5: Docker Availability"
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo "✓ Docker: $docker_version"
else
    echo "⚠️  Docker not installed (optional for containerized deployment)"
fi
echo ""

# Test 6: Check git
echo "Test 6: Git Repository"
if [ -d ".git" ]; then
    echo "✓ Git repository initialized"
else
    echo "⚠️  Git repository not found"
fi
echo ""

echo "==========================================="
echo "✨ Deployment readiness check complete!"
echo ""
echo "Next steps:"
echo "  1. Start web server: bash start-web.sh"
echo "  2. Visit: http://localhost:5000"
echo "  3. Deploy to cloud: See DEPLOYMENT_GUIDE.md"
echo ""
