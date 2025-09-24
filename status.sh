#!/bin/bash

echo "📊 PolyglotAI44 Bot Status Report"
echo "=================================="

# Check monitor process
echo "🔍 Monitor Status:"
if pgrep -f "python.*bot_monitor.py" > /dev/null; then
    MONITOR_PID=$(pgrep -f "python.*bot_monitor.py")
    echo "  ✅ Monitor running (PID: $MONITOR_PID)"
else
    echo "  ❌ Monitor not running"
fi

# Check bot process
echo ""
echo "🤖 Bot Status:"
if pgrep -f "python.*main.py" > /dev/null; then
    BOT_PID=$(pgrep -f "python.*main.py")
    echo "  ✅ Bot running (PID: $BOT_PID)"
else
    echo "  ❌ Bot not running"
fi

# Check logs
echo ""
echo "📝 Recent Log Activity:"
if [ -f "bot.log" ]; then
    LAST_LOG_TIME=$(stat -c %Y bot.log 2>/dev/null || stat -f %m bot.log 2>/dev/null)
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - LAST_LOG_TIME))

    if [ $TIME_DIFF -lt 60 ]; then
        echo "  ✅ Bot log updated ${TIME_DIFF}s ago"
    elif [ $TIME_DIFF -lt 300 ]; then
        echo "  ⚠️ Bot log updated ${TIME_DIFF}s ago (may be idle)"
    else
        echo "  ❌ Bot log updated ${TIME_DIFF}s ago (likely stuck)"
    fi

    echo "  📄 Last 3 log lines:"
    tail -3 bot.log | sed 's/^/    /'
else
    echo "  ❌ No bot.log found"
fi

echo ""
echo "💾 Monitor Log:"
if [ -f "monitor.log" ]; then
    echo "  📄 Last 3 monitor log lines:"
    tail -3 monitor.log | sed 's/^/    /'
else
    echo "  ❌ No monitor.log found"
fi

echo ""
echo "🔧 Quick Commands:"
echo "  Start: ./start_monitor.sh"
echo "  Stop:  ./stop_bot.sh"
echo "  Logs:  tail -f monitor.log (or bot.log)"