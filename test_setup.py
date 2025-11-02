#!/usr/bin/env python3
"""
Quick test to verify webhook mode setup is correct
Run this before deploying to catch any issues early
"""

import os
import sys

print("🔍 Checking Page Craft Bot - Webhook Mode Setup\n")

errors = []
warnings = []
success = []

# Check 1: Environment variables
print("1️⃣ Checking Environment Variables...")
bot_token = os.getenv("BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")

if not bot_token:
    warnings.append("BOT_TOKEN not set in local environment (OK for local testing, required on Render)")
else:
    success.append("BOT_TOKEN is set")

if not webhook_url:
    warnings.append("WEBHOOK_URL not set in local environment (OK for local testing, required on Render)")
else:
    success.append(f"WEBHOOK_URL is set to: {webhook_url}")

# Check 2: Required files
print("\n2️⃣ Checking Required Files...")
required_files = [
    "main.py",
    "bot/bot.py",
    "bot/bot_handlers.py",
    "requirements.txt",
    "render.yaml"
]

for file_path in required_files:
    if os.path.exists(file_path):
        success.append(f"✅ {file_path} exists")
    else:
        errors.append(f"❌ {file_path} is missing!")

# Check 3: Dependencies
print("\n3️⃣ Checking Dependencies...")
try:
    import flask
    success.append("✅ Flask is installed")
except ImportError:
    errors.append("❌ Flask is not installed. Run: pip install Flask")

try:
    import telegram
    success.append("✅ python-telegram-bot is installed")
except ImportError:
    errors.append("❌ python-telegram-bot is not installed")

try:
    import requests
    success.append("✅ requests is installed")
except ImportError:
    errors.append("❌ requests is not installed")

# Check 4: Imports
print("\n4️⃣ Checking Main Application Import...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    # Don't actually run the app, just check imports
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "from bot.bot_handlers import setup_handlers" in content:
            success.append("✅ Handler imports look correct")
        else:
            warnings.append("⚠️ Handler import might be incorrect in main.py")
            
        if "def auto_wake():" in content:
            success.append("✅ Auto-wake system present")
        else:
            errors.append("❌ Auto-wake system missing in main.py")
            
        if "@app.route('/webhook'" in content:
            success.append("✅ Webhook endpoint present")
        else:
            errors.append("❌ Webhook endpoint missing in main.py")
except Exception as e:
    errors.append(f"❌ Error checking main.py: {e}")

# Print results
print("\n" + "="*60)
print("📊 RESULTS")
print("="*60)

if success:
    print("\n✅ SUCCESS:")
    for msg in success:
        print(f"   {msg}")

if warnings:
    print("\n⚠️  WARNINGS:")
    for msg in warnings:
        print(f"   {msg}")

if errors:
    print("\n❌ ERRORS:")
    for msg in errors:
        print(f"   {msg}")
    print("\n🔧 Please fix the errors above before deploying!")
    sys.exit(1)
else:
    print("\n🎉 All checks passed!")
    print("\n📋 Next Steps:")
    print("   1. git add .")
    print("   2. git commit -m 'Convert to webhook mode'")
    print("   3. git push")
    print("   4. Wait for Render deployment")
    print("   5. Visit https://page-craft-bot.onrender.com/set_webhook")
    print("   6. Test with /start command in Telegram")
    print("\n✨ Your bot will wake up in ~1 minute, just like FrostByte!")
