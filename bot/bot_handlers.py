"""
Bot Handlers Setup Module
Centralizes all bot command handlers for both webhook and polling modes
"""

from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters

# Import handlers from main bot module
from bot.bot import (
    start, 
    help_command, 
    list_files_command, 
    clear_files_command,
    handle_any_document, 
    merge_command, 
    split_command, 
    to_images_command,
    merge_with_command, 
    convert_image_command, 
    combine_images_command,
    handle_filename_input, 
    cancel_rename, 
    WAITING_FOR_FILENAME
)

def setup_handlers(application):
    """
    Setup all bot handlers for the application
    
    Args:
        application: Telegram Application instance
    """
    # Create conversation handler for filename input
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

    # Add basic command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_files_command))
    application.add_handler(CommandHandler("clear", clear_files_command))
    
    # Add document handler (must be before conversation handler)
    application.add_handler(MessageHandler(filters.Document.ALL, handle_any_document))
    
    # Add conversation handler
    application.add_handler(command_filename_handler)
    
    # Add global filename input handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filename_input))
    
    print("✅ All bot handlers registered successfully")
