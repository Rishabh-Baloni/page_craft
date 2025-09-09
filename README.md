# 📄 Page Craft Bot

A powerful Telegram bot for document processing with Word-to-PDF conversion, PDF operations, and file management.

## 🚀 Features

- **📝 Professional Word to PDF**: High-quality conversion using LibreOffice CLI with full formatting preservation
- **📄 PDF Operations**: Merge, split, and convert PDFs to images with professional quality
- **🎨 Advanced Document Processing**: Preserves formatting, images, tables, headers, and complex layouts
- **🔧 Smart Fallback System**: Uses LibreOffice → pypandoc → python-docx for maximum compatibility
- **🔗 Reply Functionality**: Use reply commands on bot-generated files
- **📋 File Management**: Auto-numbering, listing, and clearing files
- **🎯 Smart Commands**: Typo detection and comprehensive help
- **⚡ Auto-Wake**: Automatically wakes Render service on user activity (free tier)

## 🛠️ Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd page-craft-bot
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   # Windows
   $env:BOT_TOKEN="your_telegram_bot_token"
   # Linux/Mac
   export BOT_TOKEN="your_telegram_bot_token"
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## 🚀 Deploy to Render (Free Tier)

### One-Click Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual Deploy (Recommended for Free Tier)

1. **Fork this repository on GitHub**

2. **Create a new Web Service on Render**
   - Go to [Render.com](https://render.com) and sign up/login
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the forked repository

3. **Configure the service**
   - **Name**: `page-craft-bot` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: **Free** (Perfect for personal use)

4. **Set Environment Variables**
   - Click "Environment" tab
   - Add new environment variable:
     - **Key**: `BOT_TOKEN`
     - **Value**: Your Telegram bot token from @BotFather

5. **Deploy!**
   - Click "Create Web Service"
   - Wait for deployment (usually 2-3 minutes)
   - Your bot will be live 24/7 on Render's free tier!

## 🤖 Getting a Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow the prompts to create your bot
4. Copy the token and set it as `BOT_TOKEN`

## 📱 Bot Commands

- `/start` - Welcome message and quick start
- `/help` - Comprehensive help guide
- `/merge` - Merge multiple PDFs
- `/split` - Split PDF by page ranges
- `/to_images` - Convert PDF to PNG images
- `/merge_with` - Merge files with replied PDF
- `/list` - Show uploaded files
- `/clear` - Clear all files

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram bot token from @BotFather |

## 📁 Project Structure

```
page-craft-bot/
├── bot/
│   └── bot.py              # Main bot logic
├── utils/
│   └── pdf_utils.py        # PDF and Word utilities
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── render.yaml            # Render deployment config
└── README.md              # This file
```

## 🎯 Usage Examples

### Word to PDF Conversion
1. Upload a .docx file
2. Enter custom filename when prompted
3. Receive converted PDF

### PDF Operations
1. Upload PDF files (auto-numbered)
2. Use `/merge 1,2,3` to combine files
3. Use `/split 1 1-5` to extract pages
4. Use `/to_images 1` for PNG conversion

### Reply Commands
1. Reply to any bot-generated PDF
2. Use `/merge_with 1,2` to merge with replied file

## 🚀 Performance Features

- ⚡ Optimized timeouts (30s/10s)
- 🗂️ File size limits and cleanup
- 🔥 Minimal logging for better performance
- 📱 Memory-efficient processing

## 🛡️ Production Ready

- ✅ Error handling and fallbacks
- ✅ File cleanup and memory management
- ✅ Secure environment variable usage
- ✅ Comprehensive logging
- ✅ Ready for cloud deployment

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions, please open a GitHub issue or contact the maintainer.

---

**Made with ❤️ for document processing automation**
