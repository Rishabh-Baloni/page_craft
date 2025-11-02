# Page Craft Bot - Webhook Mode Setup Guide

## 🎉 Successfully Converted to Webhook Mode!

Your bot has been converted from polling mode to webhook mode, just like FrostByte. This means:
- ⚡ **Fast wake-up**: Bot responds in ~1 minute even after sleeping
- 🔄 **Auto-wake system**: Keeps the service alive on Render
- 🌐 **Webhook-based**: Uses Flask to handle Telegram updates

---

## 📋 Required Environment Variables

Set these in your Render dashboard:

### 1. **BOT_TOKEN** (Required)
- Your Telegram bot token from @BotFather
- Example: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. **WEBHOOK_URL** (Required)
- Your Render service URL
- Example: `https://page-craft-bot.onrender.com`
- ⚠️ **IMPORTANT**: Update this with YOUR actual Render URL!

### 3. **PORT** (Auto-set by Render)
- Render automatically sets this
- Default: `10000`

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Convert to webhook mode like FrostByte"
git push
```

### Step 2: Deploy on Render
1. Go to your Render dashboard
2. The service will auto-deploy (if autoDeploy is enabled)
3. Wait for deployment to complete

### Step 3: Set the Webhook
**CRITICAL STEP**: After deployment, visit this URL in your browser:
```
https://page-craft-bot.onrender.com/set_webhook
```

You should see:
```json
{
  "status": "success",
  "message": "Webhook set to https://page-craft-bot.onrender.com/webhook",
  "webhook_url": "https://page-craft-bot.onrender.com/webhook"
}
```

### Step 4: Test Your Bot
1. Open Telegram
2. Send `/start` to your bot
3. The service will wake up and respond in ~1 minute!

---

## 🔍 Verification Endpoints

### Check Bot Status
```
https://page-craft-bot.onrender.com/health
```

### Check Webhook Info
```
https://page-craft-bot.onrender.com/webhook_info
```

### Delete Webhook (if needed)
```
https://page-craft-bot.onrender.com/delete_webhook
```

---

## ⚙️ How It Works

### Auto-Wake System
The bot pings itself every 14 minutes to prevent Render from sleeping:
```python
def auto_wake():
    while True:
        time.sleep(840)  # 14 minutes
        requests.get(f"{WEBHOOK_URL}/health")
```

### Webhook Flow
1. User sends message to Telegram bot
2. Telegram servers send webhook POST to `/webhook`
3. Render wakes up your service (if sleeping)
4. Flask receives the update
5. Update is processed by bot handlers
6. Response sent back to user

---

## 🆚 Webhook vs Polling Comparison

| Feature | Webhook (New) | Polling (Old) |
|---------|---------------|---------------|
| Wake-up time | ~1 minute | Never wakes up |
| Auto-wake | ✅ Yes | ❌ No |
| Resource usage | Lower | Higher |
| Response time | Faster | Slower |
| Render compatible | ✅ Yes | ⚠️ Problematic |

---

## 🐛 Troubleshooting

### Bot not responding?
1. Check webhook is set: Visit `/webhook_info`
2. Check service is running: Visit `/health`
3. Check logs in Render dashboard

### Webhook not setting?
- Ensure `WEBHOOK_URL` environment variable is correct
- URL must be HTTPS (Render provides this automatically)
- No trailing slash in WEBHOOK_URL

### Service keeps sleeping?
- The auto-wake system should prevent this
- Optional: Set up external monitoring (UptimeRobot) for extra reliability

---

## 📁 Files Changed

- ✅ `main.py` - New Flask-based webhook server
- ✅ `bot/bot_handlers.py` - Handler setup module (NEW)
- ✅ `requirements.txt` - Added Flask and requests
- ✅ `render.yaml` - Added WEBHOOK_URL env var
- 💾 `main_old.py` - Backup of original polling version
- 💾 `bot/bot_polling_backup.py` - Backup of original bot.py

---

## 🔄 Reverting to Polling Mode

If you need to revert:
```bash
mv main_old.py main.py
mv bot/bot_polling_backup.py bot/bot.py
git add .
git commit -m "Revert to polling mode"
git push
```

---

## 🎯 Next Steps

1. ✅ Push changes to GitHub
2. ✅ Wait for Render deployment
3. ✅ Visit `/set_webhook` endpoint
4. ✅ Test bot with `/start` command
5. 🎉 Enjoy fast wake-up times like FrostByte!

---

**Made with ❤️ - Webhook Mode Conversion**
