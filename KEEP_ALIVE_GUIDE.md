# 🔄 Keep Alive Guide - Preventing Bot from Sleeping

## ⚠️ The Problem

**Render Free Tier sleeps your service after 15 minutes of HTTP inactivity.**

Your bot uses **polling mode** which doesn't generate HTTP requests, so:
- ❌ After 15 minutes → Service sleeps
- ❌ Bot stops responding to Telegram messages
- ❌ Only wakes up when someone visits the external URL

## ✅ Solutions (Pick ONE)

---

## **Solution 1: UptimeRobot (EASIEST & RECOMMENDED)** ⭐

### Setup (5 minutes):

1. **Go to**: https://uptimerobot.com
2. **Sign up** for free account
3. **Click**: "Add New Monitor"
4. **Configure**:
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Page Craft Bot Keep Alive
   URL: https://page-craft-bot.onrender.com/health
   Monitoring Interval: 5 minutes
   ```
5. **Click**: "Create Monitor"

### Result:
- ✅ Your bot will NEVER sleep
- ✅ Free forever
- ✅ Email alerts if bot goes down
- ✅ Uptime statistics dashboard

**This is what I recommend!**

---

## **Solution 2: Cron-Job.org (Alternative)**

### Setup:

1. **Go to**: https://cron-job.org/en/
2. **Sign up** for free
3. **Create new cronjob**:
   ```
   Title: Page Craft Bot Ping
   URL: https://page-craft-bot.onrender.com/health
   Execution: Every 10 minutes
   ```
4. **Save**

### Result:
- ✅ Bot stays awake
- ✅ Free service

---

## **Solution 3: Switch to Webhook Mode (Most Efficient)**

### Why Webhook?
- Every Telegram message = HTTP request to your server
- Render sees activity and doesn't sleep
- More efficient than polling

### Setup:

1. **Update Render Environment Variables**:
   ```
   RENDER_EXTERNAL_URL=https://page-craft-bot.onrender.com
   BOT_TOKEN=your_token_here
   USE_WEBHOOK=true
   ```

2. **Update `main.py`**:
   ```python
   from bot.bot_webhook import start_webhook_bot
   
   if os.getenv('USE_WEBHOOK', 'false').lower() == 'true':
       start_webhook_bot()
   else:
       start_bot()
   ```

3. **Redeploy**

### Result:
- ✅ No sleeping issues
- ✅ Faster response times
- ✅ Lower resource usage

---

## **Solution 4: Render Cron Job (Native)**

### Setup:

1. **In Render Dashboard**:
   - Click "New +" → "Cron Job"
   
2. **Configure**:
   ```
   Name: page-craft-bot-keepalive
   Command: curl https://page-craft-bot.onrender.com/health
   Schedule: */10 * * * *
   ```
   (Every 10 minutes)

3. **Save**

### Result:
- ✅ Native Render solution
- ⚠️ Requires paid plan for cron jobs

---

## **Current Auto-Wake System (Built-in)**

Your bot already has internal auto-wake:
- Pings itself every 10 minutes
- ⚠️ **May not work reliably** because:
  - Internal pings might not count as "external traffic"
  - If service sleeps, internal ping can't run

### To check if it's working:
```bash
# Check Render logs for these messages:
"🚀 Auto-wake service started (10-minute intervals)"
"✅ Auto-wake successful"
```

---

## 🎯 Recommendation

**Best Approach**: Use **UptimeRobot** (Solution 1)

### Why?
- ✅ 100% free forever
- ✅ External monitoring (guaranteed to work)
- ✅ 5-minute pings (well under 15-min timeout)
- ✅ Email alerts if bot fails
- ✅ 5 minutes to set up
- ✅ Works with your current code (no changes needed)

---

## 📊 Comparison Table

| Solution | Free? | Reliability | Setup Time | Code Changes |
|----------|-------|-------------|------------|--------------|
| **UptimeRobot** ⭐ | ✅ Yes | ⭐⭐⭐⭐⭐ | 5 min | None |
| Cron-Job.org | ✅ Yes | ⭐⭐⭐⭐ | 5 min | None |
| Webhook Mode | ✅ Yes | ⭐⭐⭐⭐⭐ | 15 min | Moderate |
| Render Cron | ❌ No | ⭐⭐⭐⭐⭐ | 5 min | None |
| Internal Auto-Wake | ✅ Yes | ⭐⭐ | 0 min | None |

---

## 🔍 Testing

After setting up UptimeRobot:

1. **Wait 1 hour** without using the bot
2. **Send a message** to your bot
3. **Should respond immediately** ✅

If it still sleeps:
- Check UptimeRobot dashboard for ping failures
- Verify your Render URL is correct
- Check Render logs for errors

---

## 💡 Pro Tips

1. **Use UptimeRobot's free tier**: 50 monitors, 5-minute intervals
2. **Set up email alerts**: Get notified if bot goes down
3. **Monitor multiple endpoints**:
   - `/health` - Health check
   - `/` - Root endpoint

4. **Free tier limits**:
   - Render: 750 hours/month (31.25 days) ✅ Perfect for 24/7
   - UptimeRobot: Unlimited monitoring ✅

---

## ❓ FAQ

**Q: Why does my bot sleep after 1-2 weeks?**
A: Render free tier sleeps after 15 min of no HTTP activity. Polling mode doesn't generate HTTP traffic.

**Q: Does the built-in auto-wake work?**
A: Partially. Internal pings may not prevent sleeping. Use UptimeRobot for guaranteed uptime.

**Q: Will this cost money?**
A: No! UptimeRobot free tier is sufficient.

**Q: What's better - UptimeRobot or Webhook?**
A: Both work great:
- UptimeRobot = Easier setup, no code changes
- Webhook = Slightly more efficient, faster responses

**Q: Can I use multiple solutions?**
A: Yes! UptimeRobot + Internal auto-wake = Maximum reliability

---

## 🆘 Still Having Issues?

1. **Check Render logs**: Look for sleep/wake messages
2. **Verify UptimeRobot**: Ensure pings are successful (green)
3. **Test health endpoint**: Visit `https://your-app.onrender.com/health`
4. **Check environment variables**: Ensure `RENDER_EXTERNAL_URL` is set correctly

---

**Remember**: Render free tier is perfect for hobby projects, but requires active HTTP traffic. UptimeRobot solves this beautifully! 🎉
