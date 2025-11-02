#!/usr/bin/env python3
"""
Page Craft Bot - Webhook Mode (Like FrostByte)
A powerful Telegram bot for document processing with webhook support
"""

import os
import sys
import logging
import threading
import time
import queue
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application
from bot.bot_handlers import setup_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Thread-safe update queue
update_queue = queue.Queue()
_bot_thread = None
_initialized = False

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://page-craft-bot.onrender.com
WEBHOOK_PORT = int(os.getenv("PORT", "10000"))

# Global application instance
telegram_app = None

def ensure_bot_initialized():
    """Ensure the bot is initialized before processing requests"""
    global telegram_app, _initialized, _bot_thread
    if not _initialized:
        try:
            setup_telegram_app()
            _bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
            _bot_thread.start()
            _initialized = True
            logger.info("Bot initialization completed successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise

def setup_telegram_app():
    """Initialize the Telegram application with handlers"""
    global telegram_app
    
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    
    # Setup all handlers from bot module
    setup_handlers(telegram_app)
    
    logger.info("Telegram application initialized with all handlers")

def run_bot_thread():
    """Run the bot in a separate thread with its own event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process_updates():
        await telegram_app.initialize()
        while True:
            try:
                # Get update from queue with timeout
                update = update_queue.get(timeout=1)
                await telegram_app.process_update(update)
                update_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing update in bot thread: {e}")
    
    try:
        loop.run_until_complete(process_updates())
    except Exception as e:
        logger.error(f"Bot thread error: {e}")
    finally:
        loop.close()

# Flask routes
@app.route('/', methods=['GET'])
def home():
    """Home page with bot information"""
    return jsonify({
        'status': 'running',
        'bot_name': 'Page Craft Bot',
        'mode': 'webhook',
        'webhook_url': f"{WEBHOOK_URL}/webhook" if WEBHOOK_URL else None,
        'endpoints': {
            'webhook': '/webhook',
            'set_webhook': '/set_webhook',
            'delete_webhook': '/delete_webhook',
            'webhook_info': '/webhook_info',
            'health': '/health'
        }
    }), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    if request.method == 'POST':
        try:
            # Ensure bot is initialized
            ensure_bot_initialized()
            
            # Parse the incoming update
            update = Update.de_json(request.get_json(), telegram_app.bot)
            
            # Log the update details
            if update.message:
                message_type = "text" if update.message.text else "document" if update.message.document else "other"
                content = update.message.text[:50] if update.message.text else "N/A"
                logger.info(f"Received update: {update.update_id} - Type: {message_type} - Content: {content}")
            else:
                logger.info(f"Received update: {update.update_id} - Type: Unknown")
            
            # Add update to queue for processing by bot thread
            update_queue.put(update)
            logger.info(f"Successfully queued update: {update.update_id}")
            return jsonify({'status': 'ok'}), 200
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            logger.error(f"Update data: {request.get_json()}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    """Set the webhook URL with Telegram"""
    try:
        if not WEBHOOK_URL:
            return jsonify({'error': 'WEBHOOK_URL environment variable not set'}), 400
        
        webhook_url = f"{WEBHOOK_URL}/webhook"
        
        # Use requests to set webhook
        import requests
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        response = requests.post(url, json={'url': webhook_url})
        
        if response.status_code == 200:
            logger.info(f"Webhook set successfully to {webhook_url}")
            return jsonify({
                'status': 'success',
                'message': f'Webhook set to {webhook_url}',
                'webhook_url': webhook_url
            }), 200
        else:
            return jsonify({'error': 'Failed to set webhook', 'details': response.text}), 500
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_webhook', methods=['GET', 'POST'])
def delete_webhook():
    """Remove the webhook from Telegram"""
    try:
        # Ensure bot is initialized
        ensure_bot_initialized()
        
        result = asyncio.run(telegram_app.bot.delete_webhook())
        
        if result:
            logger.info("Webhook deleted successfully")
            return jsonify({
                'status': 'success',
                'message': 'Webhook deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to delete webhook'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    """Get current webhook information from Telegram"""
    try:
        # Use requests to get webhook info
        import requests
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'status': 'success',
                'webhook_info': data['result']
            }), 200
        else:
            return jsonify({'error': 'Failed to get webhook info'}), 500

    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring services"""
    try:
        return jsonify({
            'status': 'healthy',
            'bot_username': telegram_app.bot.username if telegram_app and telegram_app.bot else None,
            'webhook_url': f"{WEBHOOK_URL}/webhook" if WEBHOOK_URL else None,
            'mode': 'webhook'
        }), 200
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            'status': 'healthy',
            'bot_username': None,
            'webhook_url': f"{WEBHOOK_URL}/webhook" if WEBHOOK_URL else None,
            'mode': 'webhook'
        }), 200

def auto_wake():
    """Auto-wake function to prevent Render free tier from sleeping"""
    while True:
        try:
            time.sleep(840)  # 14 minutes
            if WEBHOOK_URL:
                import requests
                requests.get(f"{WEBHOOK_URL}/health", timeout=10)
                logger.info("Auto-wake ping sent")
        except Exception as e:
            logger.error(f"Auto-wake error: {e}")

def create_app():
    """Create and configure the Flask application"""
    # Validate environment variables
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    if not WEBHOOK_URL:
        logger.warning("WEBHOOK_URL environment variable not set - webhook mode may not work properly")
    
    # Setup Telegram application
    setup_telegram_app()
    
    # Start auto-wake system
    wake_thread = threading.Thread(target=auto_wake, daemon=True)
    wake_thread.start()
    logger.info("Auto-wake system started")
    
    logger.info(f"Telegram application initialized successfully")
    logger.info(f"Webhook URL will be: {WEBHOOK_URL}/webhook")
    
    return app

if __name__ == '__main__':
    # Create and configure the app
    app = create_app()
    
    logger.info(f"🚀 Starting Page Craft Bot in WEBHOOK mode on port {WEBHOOK_PORT}")
    logger.info(f"🌐 Webhook URL: {WEBHOOK_URL}/webhook")
    logger.info(f"💡 After deployment, visit {WEBHOOK_URL}/set_webhook to activate webhook")
    
    # Run Flask app
    port = int(os.environ.get('PORT', WEBHOOK_PORT))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
