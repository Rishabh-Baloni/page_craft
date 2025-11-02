# 🚀 Page Craft Bot - Webhook Deployment Checklist

## ✅ Pre-Deployment Checklist

- [x] ✅ Converted to webhook mode
- [x] ✅ Added Flask and requests to requirements.txt
- [x] ✅ Created bot_handlers.py for handler management
- [x] ✅ Added auto-wake system (14-minute intervals)
- [x] ✅ Created webhook endpoints (/webhook, /set_webhook, /health)
- [x] ✅ Updated render.yaml with WEBHOOK_URL
- [x] ✅ Created backup files (main_old.py, bot_polling_backup.py)
- [x] ✅ Verified setup with test_setup.py

---

## 📋 Deployment Steps (Do This Now!)

### Step 1: Review Changes
```bash
git status
git diff
```

### Step 2: Commit and Push
```bash
git add .
git commit -m "Convert to webhook mode - fast wake-up like FrostByte"
git push origin main
```

### Step 3: Wait for Render Deployment
- Go to: https://dashboard.render.com
- Wait for "Deploy succeeded" (usually 2-5 minutes)
- Check logs for: "🚀 Starting Page Craft Bot in WEBHOOK mode"

### Step 4: Verify Environment Variables on Render
Ensure these are set in Render Dashboard → Environment:
- `BOT_TOKEN` = Your bot token from @BotFather
- `WEBHOOK_URL` = `https://page-craft-bot.onrender.com`
- `PORT` = (Auto-set by Render, usually 10000)

### Step 5: Activate Webhook (CRITICAL!)
Visit this URL in your browser:
```
https://page-craft-bot.onrender.com/set_webhook
```

Expected response:
```json
{
  "status": "success",
  "message": "Webhook set to https://page-craft-bot.onrender.com/webhook",
  "webhook_url": "https://page-craft-bot.onrender.com/webhook"
}
```

### Step 6: Verify Webhook
```
https://page-craft-bot.onrender.com/webhook_info
```

Should show:
```json
{
  "status": "success",
  "webhook_info": {
    "url": "https://page-craft-bot.onrender.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

### Step 7: Test the Bot! 🎉
1. Open Telegram
2. Find your bot
3. Send: `/start`
4. Wait ~1 minute (service wakes up)
5. Bot responds! ⚡

---

## 🔍 Verification Endpoints

| Endpoint | Purpose | Expected Result |
|----------|---------|-----------------|
| `/` | Home | Bot info JSON |
| `/health` | Health check | `{"status": "healthy"}` |
| `/webhook` | Telegram updates | POST only |
| `/set_webhook` | Configure webhook | Success message |
| `/webhook_info` | Webhook status | Current config |
| `/delete_webhook` | Remove webhook | Success message |

---

## 🆘 Troubleshooting

### Issue: Bot doesn't respond
**Solution:**
1. Check webhook is set: Visit `/webhook_info`
2. Check service is running: Visit `/health`
3. Check Render logs for errors

### Issue: "Webhook not set" error
**Solution:**
- Visit `/set_webhook` endpoint
- Ensure WEBHOOK_URL env var is correct (no trailing slash)
- Must be HTTPS (Render provides this)

### Issue: Service keeps sleeping
**Solution:**
- Auto-wake should prevent this
- Check Render logs for "Auto-wake ping sent" every 14 minutes
- Optional: Add UptimeRobot monitor for extra reliability

### Issue: Webhook set but bot still not responding
**Solution:**
1. Delete webhook: `/delete_webhook`
2. Wait 30 seconds
3. Set webhook again: `/set_webhook`
4. Test with `/start`

---

## 📊 Comparison: Before vs After

### Before (Polling Mode)
```python
# Old main.py
app.run_polling(
    drop_pending_updates=True,
    allowed_updates=Update.ALL_TYPES,
)
```
- ❌ Never wakes up when sleeping
- ❌ No auto-wake system
- ❌ Uses more resources

### After (Webhook Mode)
```python
# New main.py
app.run(host='0.0.0.0', port=port)

# Flask handles webhooks
@app.route('/webhook', methods=['POST'])
def webhook():
    # Processes Telegram updates
```
- ✅ Wakes up in ~1 minute
- ✅ Auto-wake every 14 minutes
- ✅ Uses fewer resources
- ✅ Just like FrostByte!

---

## 🎯 Success Indicators

You'll know it's working when:

1. ✅ `/set_webhook` returns success
2. ✅ `/webhook_info` shows your webhook URL
3. ✅ `/health` returns healthy status
4. ✅ Bot responds to `/start` within 1 minute
5. ✅ Render logs show "Auto-wake ping sent" every 14 min

---

## 🔄 Rollback Instructions (If Needed)

If something goes wrong, rollback:

```bash
# Restore old files
git mv main_old.py main.py
git mv bot/bot_polling_backup.py bot/bot.py

# Revert requirements.txt
git checkout HEAD~1 requirements.txt

# Revert render.yaml
git checkout HEAD~1 render.yaml

# Remove new files
git rm bot/bot_handlers.py

# Commit and push
git commit -m "Rollback to polling mode"
git push
```

---

## 📞 Need Help?

- Check logs in Render Dashboard
- Review `WEBHOOK_SETUP.md` for detailed docs
- Test locally with `python test_setup.py`

---

## 🎉 You're All Set!

Your bot now works exactly like FrostByte:
- ⚡ Fast wake-up (1 minute)
- 🔄 Auto-wake system
- 🌐 Webhook-based
- 🚀 Production-ready

**Next**: Push to GitHub and deploy! 🚀

---

**Created**: November 3, 2025
**Status**: ✅ Ready for Deployment
