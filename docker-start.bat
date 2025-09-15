@echo off
REM LinguaBot Docker Management Script for Windows

echo 🐳 LinguaBot Docker Manager
echo.

:menu
echo ================================
echo   Docker Management Menu
echo ================================
echo 1. Build and Start Bot
echo 2. Start Bot (existing image)
echo 3. Stop Bot
echo 4. View Logs
echo 5. Bot Status
echo 6. Cleanup (remove containers)
echo 7. Full Rebuild
echo 8. Shell into Container
echo 9. Exit
echo ================================
set /p choice="Choose option (1-9): "

if "%choice%"=="1" goto build_start
if "%choice%"=="2" goto start
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto status
if "%choice%"=="6" goto cleanup
if "%choice%"=="7" goto rebuild
if "%choice%"=="8" goto shell
if "%choice%"=="9" goto exit
goto menu

:build_start
echo 🔨 Building and starting LinguaBot...
docker-compose up --build -d
echo ✅ Bot started! Check logs with option 4
pause
goto menu

:start
echo 🚀 Starting LinguaBot...
docker-compose up -d
echo ✅ Bot started!
pause
goto menu

:stop
echo 🛑 Stopping LinguaBot...
docker-compose down
echo ✅ Bot stopped!
pause
goto menu

:logs
echo 📝 Showing bot logs (Press Ctrl+C to exit logs)...
docker-compose logs -f linguabot
pause
goto menu

:status
echo 📊 Bot Status:
docker-compose ps
echo.
echo 🏥 Health Status:
docker inspect linguabot --format="{{.State.Health.Status}}" 2>nul || echo "Health check not available"
pause
goto menu

:cleanup
echo 🧹 Cleaning up containers and images...
docker-compose down -v
docker system prune -f
echo ✅ Cleanup complete!
pause
goto menu

:rebuild
echo 🔄 Full rebuild (this may take a few minutes)...
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
echo ✅ Rebuild complete!
pause
goto menu

:shell
echo 🐚 Opening shell in bot container...
docker exec -it linguabot /bin/bash
pause
goto menu

:exit
echo 👋 Goodbye!
exit