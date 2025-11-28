#!/bin/bash

# Run script for LLM Analysis Quiz Solver
# This script helps you quickly run and test the application

set -e

echo "=================================="
echo "LLM Analysis Quiz Solver"
echo "=================================="
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Install Playwright browsers if needed
if ! playwright --version &> /dev/null; then
    echo "🌐 Installing Playwright browsers..."
    playwright install chromium
else
    echo "✓ Playwright already installed"
fi

# Run tests first
echo
echo "🧪 Running tests..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo
    echo "=================================="
    echo "✅ All tests passed!"
    echo "=================================="
    echo
    echo "🚀 Starting server..."
    echo "   API will be available at: http://localhost:8000"
    echo "   Health check: http://localhost:8000/health"
    echo
    echo "Press Ctrl+C to stop the server"
    echo
    
    # Start the server
    python app.py
else
    echo
    echo "=================================="
    echo "❌ Tests failed!"
    echo "=================================="
    echo "Please fix the issues before running the server."
    exit 1
fi
