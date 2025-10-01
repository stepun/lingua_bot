#!/bin/bash

# Start Admin Panel for LinguaBot
# Usage: ./start_admin.sh

echo "🚀 Starting LinguaBot Admin Panel..."

# Change to lingua_bot directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "new_venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv new_venv"
    exit 1
fi

# Activate virtual environment
source new_venv/bin/activate

# Install requirements if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing FastAPI dependencies..."
    pip install fastapi uvicorn
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start admin panel
echo "✅ Admin panel starting on http://localhost:8081"
echo "📝 Press Ctrl+C to stop"
echo ""

cd lingua_bot
python -m uvicorn admin_app.app:app --host 0.0.0.0 --port 8081 --reload
