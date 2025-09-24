#!/bin/bash

echo "Starting PolyglotAI44 in webhook mode..."

# Copy webhook config if exists
if [ -f ".env.webhook" ]; then
    echo "Using webhook configuration..."
    cp .env.webhook .env
fi

# Start the bot
python3 -u main.py