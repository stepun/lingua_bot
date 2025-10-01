#!/bin/bash

while true; do
    if ! pgrep -f 'python.*main.py' > /dev/null; then
        echo "Wed Sep 24 15:17:27 +03 2025: Starting bot..."
        nohup python3 -u main.py > bot.log 2>&1 &
        sleep 10
    fi
    sleep 30
done
