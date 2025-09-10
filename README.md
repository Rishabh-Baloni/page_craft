# 📄 Page Craft Bot

A memory-optimized Telegram bot for PDF processing and document management, designed for deployment on Render's free tier.

## 🚀 Features

### 📁 PDF Processing
- **Merge PDFs**: Combine multiple PDF files in custom order
- **Split PDFs**: Extract specific pages or page ranges  
- **Reply System**: Reply to any PDF message with commands

### �️ Image Processing
- **Image to PDF**: Convert single or multiple images to PDF
- **PDF to Images**: Extract pages as high-quality JPEG images
- **Custom Filenames**: User-friendly file naming system

### 🔧 Advanced Features
- **Memory Optimized**: Designed for 512MB memory limit (Render free tier)
- **Auto-Wake System**: Prevents service from sleeping with HTTP health checks
- **Lazy Loading**: PDF utilities loaded only when needed
- **File Management**: Upload limits and automatic cleanup

## 🛠️ Technology Stack

- **Python 3.8+**
- **python-telegram-bot 20.3** (compatibility-tested version)
- **pypdf 3.17.4** - PDF processing
- **pdf2image 1.16.3** - PDF to image conversion
- **reportlab 4.0.8** - PDF generation
- **Pillow 10.0.1** - Image processing
- **psutil 5.9.5** - Memory monitoring

## 📋 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Rishabh-Baloni/page_craft.git
cd page_craft
```

### 2. Local Development Setup  
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file or set environment variables:
```env
BOT_TOKEN=your_telegram_bot_token
RENDER_EXTERNAL_URL=your_render_app_url  # For production only
```

### 4. Run Locally
```bash
python bot/bot.py
```

## 🌐 Deploy to Render

### 1. Connect Repository
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"  
3. Connect your GitHub repository: `Rishabh-Baloni/page_craft`

### 2. Configure Service
```yaml
# Build Command
pip install -r requirements.txt

# Start Command  
python main.py

# Environment Variables
BOT_TOKEN=your_telegram_bot_token_here
RENDER_EXTERNAL_URL=https://your-app-name.onrender.com
```

### 3. Advanced Settings
- **Plan**: Free
- **Region**: Choose closest to your users
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

## 🤖 Bot Commands

### Basic Commands
- `/start` - Initialize bot and see welcome message
- `/help` - Show detailed help and commands
- `/list` - Display all uploaded files
- `/clear` - Remove all uploaded files

### PDF Operations
```
/merge              # Merge all uploaded files
/merge 1,3,2        # Merge specific files in order
/split 1 5-8        # Split file #1, pages 5-8
/split 2 3          # Split file #2, page 3 only
```

### Reply Features
Reply to any PDF message with:
- `/merge` - Shows merge options with that PDF
- `/split 5-8` - Splits that specific PDF

## 🔧 Architecture

### Memory Optimization
```python
# Strict memory limits for free tier
MAX_FILES_PER_USER = 5      # Limit concurrent files
MAX_FILE_SIZE_MB = 10       # Individual file size limit  
MAX_TOTAL_MEMORY_MB = 200   # Total memory threshold
```

### Auto-Wake System
```python
# Prevents Render free tier from sleeping
def wake_service_on_activity():
    """HTTP ping to keep service active"""
    # Lightweight self-ping mechanism
```

### Lazy Loading
```python
def lazy_import_pdf_utils():
    """Import PDF libraries only when needed"""
    # Reduces startup memory usage
```

## 📊 Performance Metrics

### Memory Usage
- **Startup**: ~50MB (with lazy loading)
- **Peak Processing**: ~150MB (during PDF operations)
- **Idle**: ~30MB (after cleanup)

### File Limits
- **Max Files per User**: 5 concurrent
- **Max File Size**: 10MB per file
- **Supported Formats**: PDF, JPG, PNG, GIF, BMP

## 🐛 Troubleshooting

### Common Issues

**1. Bot Not Responding**
```bash
# Check bot token
echo $BOT_TOKEN

# Verify deployment logs on Render
```

**2. Memory Errors**
```python
# Automatic memory cleanup implemented
# Check logs for memory warnings
```

**3. PDF Processing Fails**
```bash
# Check file size limits
# Ensure valid PDF format
```

## 🚀 Deployment Status

✅ **Production Ready**
- Telegram library compatibility confirmed (v20.3)
- Memory optimization active for Render free tier
- Auto-wake system implemented
- All deployment tests passing

---

**Made with ❤️ for efficient PDF processing on Telegram**
