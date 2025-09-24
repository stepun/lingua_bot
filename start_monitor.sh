#!/bin/bash

echo "🚀 Starting PolyglotAI44 Bot Monitor..."

# Kill any existing monitors
pkill -f "python.*bot_monitor.py" 2>/dev/null || true

# Kill any existing bots
pkill -f "python.*main.py" 2>/dev/null || true

# Wait a bit for cleanup
sleep 2

# Start monitor in background
nohup python3 bot_monitor.py > monitor_startup.log 2>&1 &

echo "✅ Bot Monitor started in background"
echo "📝 Check logs: monitor.log (monitor) and bot.log (bot)"
echo "🔍 Monitor processes: ps aux | grep -E '(bot_monitor|main.py)'"
echo "🛑 Stop monitor: pkill -f 'python.*bot_monitor.py'"