#!/bin/bash
while true; do
    if ! pgrep -f 'python.*main.py' > /dev/null; then
        echo "$(date): Restarting bot..."
        nohup python3 -u main.py > bot.log 2>&1 &
        sleep 10
    fi
    sleep 20
done
