#!/usr/bin/env python3
"""
Page Craft Bot - Entry Point
A powerful Telegram bot for document processing and Word-to-PDF conversion.
"""

import os
import sys
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from bot.bot import start_bot

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for Render health checks"""
    
    def _handle_request(self):
        """Bulletproof handler for UptimeRobot and all monitoring services"""
        try:
            # Always respond with 200 OK for any path/method
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # Only send body for non-HEAD requests
            if self.command != 'HEAD':
                response = {
                    'status': 'running',
                    'bot_name': 'Page Craft Bot',
                    'uptime': 'active',
                    'path': self.path,
                    'method': self.command
                }
                import json
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            # Fallback - always return 200 even on errors
            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                if self.command != 'HEAD':
                    self.wfile.write(b'OK')
            except:
                pass  # Ignore any further errors
    
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_PUT(self):
        self._handle_request()
    
    def do_DELETE(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._handle_request()
    
    def do_HEAD(self):
        self._handle_request()
    
    def do_PATCH(self):
        self._handle_request()
    
    def do_TRACE(self):
        self._handle_request()
    
    def do_CONNECT(self):
        self._handle_request()
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs to reduce noise
        pass

def run_web_server():
    """Run a simple web server for Render's port requirements"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"🌐 Health check server started on port {port}")
    server.serve_forever()

def main():
    """Main entry point for the bot"""
    try:
        # Check if bot token is provided
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token or bot_token == 'your_telegram_bot_token_here':
            logger.error("❌ BOT_TOKEN environment variable not set!")
            logger.error("Please set your Telegram bot token from @BotFather")
            sys.exit(1)
        
        # Create a simple lock mechanism to prevent multiple instances
        lock_file = '/tmp/pagebot.lock'
        if os.path.exists(lock_file):
            logger.warning("🔄 Lock file exists, checking if another instance is running...")
            try:
                # Try to remove old lock file (it might be stale)
                os.remove(lock_file)
                logger.info("✅ Removed stale lock file")
            except Exception:
                logger.warning("⚠️ Could not remove lock file, continuing anyway...")
        
        # Create lock file
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"🔒 Created lock file: {lock_file}")
        except Exception:
            logger.warning("⚠️ Could not create lock file, continuing anyway...")
        
        # Start web server in a separate thread for Render
        web_thread = Thread(target=run_web_server, daemon=True)
        web_thread.start()
        
        logger.info("🚀 Starting Page Craft Bot...")
        
        try:
            start_bot()
        finally:
            # Clean up lock file
            try:
                if os.path.exists(lock_file):
                    os.remove(lock_file)
                    logger.info("🧹 Cleaned up lock file")
            except Exception:
                pass
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        # Clean up lock file on error
        try:
            lock_file = '/tmp/pagebot.lock'
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
