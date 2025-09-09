#!/usr/bin/env python3
"""
Bot Conflict Resolver - Clears webhooks and ensures clean polling setup
"""

import os
import asyncio
import sys

async def clear_bot_webhook():
    """Clear any existing webhook to enable polling"""
    
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TOKEN')
    
    if BOT_TOKEN == 'YOUR_TOKEN':
        print("❌ BOT_TOKEN not set!")
        print("Please set your bot token:")
        print("$env:BOT_TOKEN='your_bot_token_here'  # Windows PowerShell")
        print("export BOT_TOKEN='your_bot_token_here'  # Linux/Mac")
        return False
    
    try:
        import telegram
        
        print("🔧 Connecting to Telegram bot...")
        bot = telegram.Bot(token=BOT_TOKEN)
        
        # Get current webhook info
        print("📡 Checking current webhook status...")
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url:
            print(f"🔍 Found webhook: {webhook_info.url}")
            print("🗑️ Clearing webhook...")
            await bot.delete_webhook(drop_pending_updates=True)
            print("✅ Webhook cleared successfully!")
        else:
            print("ℹ️ No webhook found - bot is ready for polling")
        
        # Clear any pending updates
        print("🧹 Clearing pending updates...")
        await bot.delete_webhook(drop_pending_updates=True)
        
        print("✅ Bot is now ready for local polling!")
        print("🚀 You can now run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing webhook: {e}")
        if "Unauthorized" in str(e):
            print("🔑 Check your BOT_TOKEN - it might be incorrect")
        elif "Network" in str(e) or "timeout" in str(e).lower():
            print("🌐 Network error - check your internet connection")
        return False

if __name__ == "__main__":
    print("🤖 Bot Conflict Resolver")
    print("=" * 40)
    
    # Run the webhook clearing
    success = asyncio.run(clear_bot_webhook())
    
    if success:
        print("\n" + "=" * 40)
        print("✅ RESOLUTION COMPLETE")
        print("Your bot is ready to run without conflicts!")
    else:
        print("\n" + "=" * 40)
        print("❌ RESOLUTION FAILED")
        print("Please check the error messages above.")
