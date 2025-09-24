#!/bin/bash

# Script to check if monitor is running and restart if needed
# Add to cron: */5 * * * * /home/v/vokhma1v/vokhma1v.beget.tech/lingua_bot/check_and_restart.sh

cd /home/v/vokhma1v/vokhma1v.beget.tech/lingua_bot

# Check if monitor is running
if ! pgrep -f "python.*bot_monitor.py" > /dev/null; then
    echo "$(date): Monitor not running, starting..." >> cron_check.log
    ./start_monitor.sh >> cron_check.log 2>&1
else
    # Monitor is running, check if bot is running
    if ! pgrep -f "python.*main.py" > /dev/null; then
        echo "$(date): Bot not running but monitor is up" >> cron_check.log
    fi
fi