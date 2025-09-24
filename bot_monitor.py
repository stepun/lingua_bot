#!/usr/bin/env python3
"""
Bot Monitor - Advanced monitoring and auto-recovery system for PolyglotAI44
Monitors bot health and automatically restarts if needed
"""

import subprocess
import time
import logging
import os
import signal
import sys
from datetime import datetime
from pathlib import Path

# Configuration
BOT_SCRIPT = "main.py"
BOT_LOG = "bot.log"
MONITOR_LOG = "monitor.log"
CHECK_INTERVAL = 30  # seconds
MAX_RESTART_ATTEMPTS = 5
RESTART_DELAY = 10  # seconds between restarts
HEALTH_CHECK_TIMEOUT = 60  # seconds without log activity = unhealthy

class BotMonitor:
    def __init__(self):
        self.bot_process = None
        self.restart_count = 0
        self.last_restart = None
        self.setup_logging()

    def setup_logging(self):
        """Setup monitoring logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(MONITOR_LOG),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def is_bot_running(self):
        """Check if bot process is running"""
        if not self.bot_process:
            return False

        # Check if process is still alive
        try:
            self.bot_process.poll()
            return self.bot_process.returncode is None
        except:
            return False

    def is_bot_healthy(self):
        """Check if bot is healthy (responding and logging)"""
        if not self.is_bot_running():
            return False

        try:
            # Check if bot log has recent activity
            if os.path.exists(BOT_LOG):
                log_stat = os.stat(BOT_LOG)
                last_modified = datetime.fromtimestamp(log_stat.st_mtime)
                now = datetime.now()
                time_since_log = (now - last_modified).seconds

                if time_since_log > HEALTH_CHECK_TIMEOUT:
                    self.logger.warning(f"Bot unhealthy: no log activity for {time_since_log}s")
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def start_bot(self):
        """Start the bot process"""
        try:
            self.logger.info("🚀 Starting bot...")

            # Kill any existing processes
            self.kill_existing_bots()

            # Start new bot process
            self.bot_process = subprocess.Popen([
                sys.executable, "-u", BOT_SCRIPT
            ], stdout=open(BOT_LOG, 'w'), stderr=subprocess.STDOUT)

            self.restart_count += 1
            self.last_restart = datetime.now()

            self.logger.info(f"✅ Bot started with PID {self.bot_process.pid}")
            time.sleep(RESTART_DELAY)  # Give bot time to initialize

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to start bot: {e}")
            return False

    def kill_existing_bots(self):
        """Kill any existing bot processes"""
        try:
            # Find and kill existing python processes running main.py
            result = subprocess.run([
                'pgrep', '-f', 'python.*main.py'
            ], capture_output=True, text=True)

            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid and pid.isdigit():
                        self.logger.info(f"🔄 Killing existing bot process PID {pid}")
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(2)

        except Exception as e:
            self.logger.error(f"Error killing existing processes: {e}")

    def restart_bot(self):
        """Restart the bot"""
        self.logger.warning("🔄 Restarting bot...")

        # Kill current process if exists
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
            except:
                try:
                    self.bot_process.kill()
                except:
                    pass

        return self.start_bot()

    def reset_restart_counter(self):
        """Reset restart counter if bot has been stable"""
        if (self.last_restart and
            (datetime.now() - self.last_restart).seconds > 300):  # 5 minutes stable
            if self.restart_count > 0:
                self.logger.info("🎯 Bot stable, resetting restart counter")
                self.restart_count = 0

    def run(self):
        """Main monitoring loop"""
        self.logger.info("🔍 Bot Monitor starting...")

        # Start bot initially
        if not self.start_bot():
            self.logger.error("💥 Failed to start bot initially, exiting")
            return

        try:
            while True:
                time.sleep(CHECK_INTERVAL)

                # Reset counter if bot has been stable
                self.reset_restart_counter()

                # Check bot health
                if not self.is_bot_healthy():
                    self.logger.warning("⚠️ Bot is not healthy")

                    # Check restart limits
                    if self.restart_count >= MAX_RESTART_ATTEMPTS:
                        self.logger.error(f"💥 Max restart attempts ({MAX_RESTART_ATTEMPTS}) reached, giving up")
                        break

                    # Attempt restart
                    if not self.restart_bot():
                        self.logger.error("💥 Failed to restart bot")
                        break

                else:
                    # Bot is healthy
                    if self.restart_count > 0:
                        self.logger.info(f"💚 Bot healthy (restarts: {self.restart_count})")

        except KeyboardInterrupt:
            self.logger.info("🛑 Monitor interrupted by user")
        except Exception as e:
            self.logger.error(f"💥 Monitor crashed: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup on exit"""
        self.logger.info("🧹 Cleaning up monitor...")

        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
            except:
                try:
                    self.bot_process.kill()
                except:
                    pass

        self.logger.info("👋 Monitor stopped")

def main():
    """Main entry point"""
    # Handle signals
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, stopping monitor...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Start monitor
    monitor = BotMonitor()
    monitor.run()

if __name__ == "__main__":
    main()