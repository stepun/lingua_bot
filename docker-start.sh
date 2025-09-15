#!/bin/bash

# LinguaBot Docker Management Script for Linux/macOS

echo "🐳 LinguaBot Docker Manager"
echo

show_menu() {
    echo "================================"
    echo "   Docker Management Menu"
    echo "================================"
    echo "1. Build and Start Bot"
    echo "2. Start Bot (existing image)"
    echo "3. Stop Bot"
    echo "4. View Logs"
    echo "5. Bot Status"
    echo "6. Cleanup (remove containers)"
    echo "7. Full Rebuild"
    echo "8. Shell into Container"
    echo "9. Exit"
    echo "================================"
}

build_start() {
    echo "🔨 Building and starting LinguaBot..."
    docker-compose up --build -d
    echo "✅ Bot started! Check logs with option 4"
}

start_bot() {
    echo "🚀 Starting LinguaBot..."
    docker-compose up -d
    echo "✅ Bot started!"
}

stop_bot() {
    echo "🛑 Stopping LinguaBot..."
    docker-compose down
    echo "✅ Bot stopped!"
}

show_logs() {
    echo "📝 Showing bot logs (Press Ctrl+C to exit logs)..."
    docker-compose logs -f linguabot
}

show_status() {
    echo "📊 Bot Status:"
    docker-compose ps
    echo
    echo "🏥 Health Status:"
    docker inspect linguabot --format="{{.State.Health.Status}}" 2>/dev/null || echo "Health check not available"
}

cleanup() {
    echo "🧹 Cleaning up containers and images..."
    docker-compose down -v
    docker system prune -f
    echo "✅ Cleanup complete!"
}

rebuild() {
    echo "🔄 Full rebuild (this may take a few minutes)..."
    docker-compose down -v
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Rebuild complete!"
}

shell_access() {
    echo "🐚 Opening shell in bot container..."
    docker exec -it linguabot /bin/bash
}

# Main loop
while true; do
    show_menu
    read -p "Choose option (1-9): " choice
    echo

    case $choice in
        1)
            build_start
            ;;
        2)
            start_bot
            ;;
        3)
            stop_bot
            ;;
        4)
            show_logs
            ;;
        5)
            show_status
            ;;
        6)
            cleanup
            ;;
        7)
            rebuild
            ;;
        8)
            shell_access
            ;;
        9)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-9."
            ;;
    esac

    echo
    read -p "Press Enter to continue..."
    echo
done