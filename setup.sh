#!/bin/bash
# Getting Started Script for nagatha_core
# This script helps set up the development environment

set -e

echo "🚀 nagatha_core - Getting Started Setup"
echo "========================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
else
    echo "✓ Virtual environment already exists"
    source venv/bin/activate
fi

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --quiet --upgrade pip

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -e ".[dev]"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Start RabbitMQ and Redis (Docker):"
echo "   docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management"
echo "   docker run -d -p 6379:6379 redis:latest"
echo ""
echo "2. In Terminal 1 - Start the API server:"
echo "   python -m uvicorn nagatha_core.main:app --reload"
echo ""
echo "3. In Terminal 2 - Start the Celery worker:"
echo "   celery -A nagatha_core.broker.celery_app worker --loglevel=info"
echo ""
echo "4. In Terminal 3 - Use the CLI:"
echo "   nagatha list modules"
echo "   nagatha run echo_bot.echo -k message='Hello, World!'"
echo "   nagatha status --task-id <task-id>"
echo ""
echo "📚 Documentation:"
echo "   Read docs/index.md for comprehensive guide"
echo ""
echo "🧪 Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "Happy coding! 🎉"
