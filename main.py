#!/usr/bin/env python3
"""
Paper Craft Bot - Entry Point
A powerful Telegram bot for document processing and Word-to-PDF conversion.
"""

import os
import sys
import logging
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

def main():
    """Main entry point for the bot"""
    try:
        # Check if bot token is provided
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token or bot_token == 'your_telegram_bot_token_here':
            logger.error("❌ BOT_TOKEN environment variable not set!")
            logger.error("Please set your Telegram bot token from @BotFather")
            sys.exit(1)
        
        logger.info("🚀 Starting Paper Craft Bot...")
        start_bot()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
