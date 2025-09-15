#!/bin/bash

# LinguaBot Linux/macOS Startup Script

echo "Starting LinguaBot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and fill in your API keys."
    exit 1
fi

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories if they don't exist
mkdir -p data logs exports

# Start the bot
echo "Starting LinguaBot..."
python main.py