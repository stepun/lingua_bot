#!/bin/bash

echo "🛑 Stopping PolyglotAI44 Bot and Monitor..."

# Stop monitor
echo "🔍 Stopping bot monitor..."
pkill -f "python.*bot_monitor.py" 2>/dev/null && echo "✅ Monitor stopped" || echo "ℹ️ No monitor running"

# Stop bot
echo "🤖 Stopping bot..."
pkill -f "python.*main.py" 2>/dev/null && echo "✅ Bot stopped" || echo "ℹ️ No bot running"

# Stop any auto-restart scripts
echo "🔄 Stopping auto-restart scripts..."
pkill -f "auto_restart.sh" 2>/dev/null && echo "✅ Auto-restart stopped" || echo "ℹ️ No auto-restart running"

echo "✅ All processes stopped"