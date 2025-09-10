# 🚀 Page Craft Bot - Render Deployment Guide

## GitHub Setup

1. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Page Craft Bot"
   ```

2. **Create GitHub Repository**
   - Go to GitHub.com and create a new repository
   - Name it: `page-craft-bot`
   - Don't initialize with README (we already have one)

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/page-craft-bot.git
   git branch -M main
   git push -u origin main
   ```

## 🟦 Deploy to Render (Free Tier)

### Step-by-Step Render Deployment

1. **Go to Render.com**
   - Visit [render.com](https://render.com)
   - Sign up or log in with your GitHub account

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Click "Connect" next to your GitHub account
   - Select the `page-craft-bot` repository

3. **Configure Service Settings**
   - **Name**: `page-craft-bot` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your location
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: **Free** (Perfect for personal use!)

4. **Set Environment Variables**
   - Scroll down to "Environment Variables"
   - Click "Add Environment Variable"
   - **Key**: `BOT_TOKEN`
   - **Value**: Your bot token from @BotFather
   - Click "Add"

5. **Deploy Your Bot**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Your bot will be live 24/7!

## 🤖 Getting Your Bot Token

1. Open Telegram and search for `@BotFather`
2. Start a chat and send `/newbot`
3. Follow the prompts:
   - Bot name: `Page Craft Bot` (or your choice)
   - Bot username: `pagecraft_bot` (must end with 'bot')
4. Copy the token that BotFather gives you
5. Use this token as your `BOT_TOKEN` in Render

## ✅ Render Free Tier Benefits

- **Free forever** for personal projects
- **Automatic deployments** from GitHub
- **750 hours/month** (enough for 24/7 operation)
- **HTTPS included**
- **Auto-restart** if your bot crashes
- **Built-in logging** and monitoring

## ✅ Deployment Checklist

- [ ] Bot token obtained from @BotFather
- [ ] GitHub repository created and pushed
- [ ] Deployment platform chosen (Render/Heroku)
- [ ] Environment variables set
- [ ] Bot deployed and running
- [ ] Bot tested with `/start` command

## 🔧 Environment Variables Required

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `BOT_TOKEN` | Telegram bot token | @BotFather on Telegram |

## 📱 Testing Your Deployed Bot

1. Find your bot on Telegram using the username from @BotFather
2. Send `/start` to test basic functionality
3. Upload a Word document to test conversion
4. Try PDF operations with `/help` for full command list

## 🚨 Troubleshooting

### Bot not responding
- Check if `BOT_TOKEN` is set correctly
- Verify the bot is deployed and running
- Check deployment logs for errors

### Word conversion not working
- Ensure all dependencies are installed
- Check that `python-docx` and `reportlab` packages are available
- Word conversion uses pure Python libraries (Linux-compatible)

### PDF operations failing
- Verify `poppler-utils` is installed (automatic on Render/Heroku)
- Check file size limits on your deployment platform

## 🔄 Updates and Maintenance

To update your deployed bot:
1. Make changes locally
2. Test thoroughly
3. Commit and push to GitHub
4. Platform auto-deploys from GitHub (if configured)

---

**Your Page Craft Bot is now ready for production! 🎉**
