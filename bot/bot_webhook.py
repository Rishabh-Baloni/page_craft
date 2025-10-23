# Page Craft Bot - Webhook Mode (Prevents Sleeping on Render)
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Import all handlers from bot.py
from bot import (
    start, help_command, list_files_command, clear_files_command,
    handle_any_document, merge_command, split_command, to_images_command,
    merge_with_command, convert_image_command, combine_images_command,
    handle_filename_input, cancel_rename, WAITING_FOR_FILENAME
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_webhook_bot():
    """Start the bot in webhook mode for Render deployment"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL')
    PORT = int(os.getenv('PORT', 10000))
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    if not RENDER_EXTERNAL_URL:
        logger.error("❌ RENDER_EXTERNAL_URL not set! Required for webhook mode.")
        return
    
    # Build application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Create conversation handler
    command_filename_handler = ConversationHandler(
        entry_points=[
            CommandHandler("merge", merge_command),
            CommandHandler("split", split_command),
            CommandHandler("to_images", to_images_command),
            CommandHandler("merge_with", merge_with_command),
            CommandHandler("convert_image", convert_image_command),
            CommandHandler("combine_images", combine_images_command),
        ],
        states={
            WAITING_FOR_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filename_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel_rename)],
        per_message=False
    )
    
    # Add all handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_files_command))
    app.add_handler(CommandHandler("clear", clear_files_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_any_document))
    app.add_handler(command_filename_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filename_input))
    
    logger.info("🚀 Starting webhook mode...")
    logger.info(f"📍 Webhook URL: {RENDER_EXTERNAL_URL}/webhook")
    logger.info(f"🔌 Port: {PORT}")
    
    # Run webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{RENDER_EXTERNAL_URL}/webhook",
        drop_pending_updates=True
    )

if __name__ == "__main__":
    start_webhook_bot()
