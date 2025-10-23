# Page Craft Bot - Memory Optimized for Render Free Tier
import os
import tempfile
import logging
import shutil
import gc
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Note: psutil not available - memory monitoring disabled for local testing")

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Configure minimal logging to reduce memory overhead
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

# Memory optimization: Import utils only when needed (lazy loading)
# from utils.pdf_utils import merge_pdfs, split_pdf, pdf_to_images, create_zip_from_images, word_to_pdf

# Conversation states
WAITING_FOR_FILENAME = 1

# Store user files temporarily (with strict memory limits)
user_files = {}
pending_files = {}

# Memory optimization: Reduce limits for free tier
MAX_FILES_PER_USER = 5  # Reduced from 20
MAX_FILE_SIZE_MB = 10   # Limit individual file size
MAX_TOTAL_MEMORY_MB = 200  # Total memory limit

# Enhanced auto-wake system for Render
RENDER_URL = os.getenv('RENDER_EXTERNAL_URL', None)
AUTO_WAKE_ENABLED = True
WAKE_URLS = [
    "https://page-craft-bot.onrender.com",
    "https://page-craft-bot.onrender.com/health",
    "https://page-craft-bot.onrender.com/"
]

def get_memory_usage():
    """Get current memory usage in MB"""
    try:
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        else:
            return 0  # No monitoring available locally
    except:
        return 0

def cleanup_memory():
    """Force garbage collection and memory cleanup"""
    gc.collect()
    
def check_memory_limit():
    """Check if we're approaching memory limits"""
    memory_mb = get_memory_usage()
    if memory_mb > MAX_TOTAL_MEMORY_MB and memory_mb > 0:
        logging.warning(f"High memory usage: {memory_mb:.1f}MB")
        cleanup_memory()
        return False
    return True

def lazy_import_pdf_utils():
    """Lazy import PDF utilities to save memory"""
    try:
        # Add current directory and parent directory to path for import resolution
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        from utils.pdf_utils import merge_pdfs, split_pdf, pdf_to_images, create_zip_from_images, image_to_pdf
        # Test that functions are actually callable
        if not all(callable(func) for func in [merge_pdfs, split_pdf, image_to_pdf]):
            logging.error("PDF utility functions are not callable")
            return None, None, None, None, None
        return merge_pdfs, split_pdf, pdf_to_images, create_zip_from_images, image_to_pdf
    except ImportError as e:
        logging.error(f"Failed to import PDF utilities: {e}")
        print(f"PDF utils import error: {e}")  # Also print for debugging
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path[:3]}")
        return None, None, None, None, None
    except Exception as e:
        logging.error(f"Unexpected error loading PDF utilities: {e}")
        print(f"PDF utils unexpected error: {e}")  # Also print for debugging
        return None, None, None, None, None

async def wake_service_on_activity():
    """Enhanced auto-wake system with multiple strategies"""
    if not AUTO_WAKE_ENABLED:
        return
        
    import threading
    
    def wake_service():
        """Background wake-up function"""
        try:
            import urllib.request
            import time
            
            # Strategy 1: Immediate wake-up on user activity
            for url in WAKE_URLS:
                try:
                    response = urllib.request.urlopen(url, timeout=5)
                    if response.getcode() == 200:
                        print(f"🚀 Service woke up successfully via {url}")
                        break
                except Exception as e:
                    print(f"⚠️ Wake attempt failed for {url}: {e}")
                    continue
                    
            # Strategy 2: Keep-alive ping
            if RENDER_URL:
                try:
                    urllib.request.urlopen(f"{RENDER_URL}/", timeout=3)
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Wake service error: {e}")
    
    # Run wake-up in background thread to not block user interaction
    try:
        wake_thread = threading.Thread(target=wake_service, daemon=True)
        wake_thread.start()
    except Exception as e:
        print(f"⚠️ Failed to start wake thread: {e}")

def start_auto_wake_service():
    """Start background auto-wake service to prevent sleeping"""
    if not AUTO_WAKE_ENABLED:
        return
        
    import threading
    import time
    
    def periodic_wake():
        """Keep service awake with aggressive pings to prevent 15-min timeout"""
        while True:
            try:
                # CRITICAL: Wait 10 minutes (under 15-min Render timeout)
                # Render free tier sleeps after 15 min of no HTTP activity
                time.sleep(600)  # 10 minutes = 600 seconds
                
                # Ping multiple endpoints aggressively
                import urllib.request
                import socket
                
                # Set socket timeout globally
                socket.setdefaulttimeout(15)
                
                wake_success = False
                for url in WAKE_URLS:
                    try:
                        print(f"🔄 Auto-wake ping to: {url}")
                        
                        # Create request with headers to look like real traffic
                        req = urllib.request.Request(
                            url,
                            headers={
                                'User-Agent': 'PageCraftBot-KeepAlive/1.0',
                                'Accept': 'text/html,application/json'
                            }
                        )
                        
                        response = urllib.request.urlopen(req, timeout=15)
                        if response.getcode() == 200:
                            print(f"✅ Auto-wake successful via {url}")
                            wake_success = True
                            break
                    except Exception as url_error:
                        print(f"⚠️ Wake ping failed for {url}: {url_error}")
                        continue
                
                if not wake_success:
                    print("❌ All wake URLs failed - service may be sleeping")
                    print("💡 TIP: Use external monitoring service like UptimeRobot!")
                        
            except Exception as e:
                print(f"⚠️ Auto-wake error: {e}")
    
    # Start the auto-wake thread
    try:
        wake_thread = threading.Thread(target=periodic_wake, daemon=True)
        wake_thread.start()
        print("🚀 Auto-wake service started (10-minute intervals)")
        print("⚠️ NOTE: Internal pings may not prevent sleeping on Render free tier")
        print("💡 RECOMMENDED: Use UptimeRobot.com for external monitoring")
    except Exception as e:
        print(f"⚠️ Failed to start auto-wake: {e}")

def emergency_wake():
    """Emergency wake-up for critical bot operations"""
    try:
        import urllib.request
        
        # Try to wake the service immediately
        for url in WAKE_URLS:
            try:
                response = urllib.request.urlopen(url, timeout=10)
                if response.getcode() == 200:
                    print(f"🆘 Emergency wake successful via {url}")
                    return True
            except:
                continue
        return False
    except:
        return False

def find_replied_pdf(update: Update, user_id: int):
    """Find the PDF file that was replied to"""
    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        return None
    
    replied_message_id = update.message.reply_to_message.message_id
    
    if user_id not in user_files:
        return None
    
    # Quick lookup for performance
    for file_info in user_files[user_id]:
        if file_info.get('message_id') == replied_message_id:
            return file_info
    
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    # Memory check before processing
    if not check_memory_limit():
        await update.message.reply_text("⚠️ Service temporarily busy. Please try again in a moment.")
        return
        
    # Lightweight service wake
    await wake_service_on_activity()
    
    await update.message.reply_text(
        "📄 Page Craft Bot - Memory Optimized\n\n"
        "Upload files (max 10MB each, 5 files per user):\n"
        "• 📄 PDFs: /merge, /split, /to_images\n"
        "• �️ Images: /convert_image, /combine_images\n"
        "• /help - Full help\n\n"
        "Files are auto-numbered as uploaded."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    if not check_memory_limit():
        await update.message.reply_text("⚠️ Service temporarily busy. Please try again.")
        return
        
    await wake_service_on_activity()
    
    help_message = """
📄 Page Craft Bot Commands:

📤 **Upload Files** then use:

🔗 **Merge PDFs:**
• /merge - Merge all uploaded PDFs
• /merge 1,3,2 - Merge specific PDFs in order

✂️ **Split PDF:**
• /split 1 5-8 - Split PDF #1, pages 5 to 8  
• /split 2 3 - Split PDF #2, page 3 only

🖼️ **PDF to Images:**
• /to_images - Convert latest PDF to images
• /to_images 1 - Convert PDF #1 to images

� **Image to PDF:**
• Upload images → Stored for processing
• /convert_image - Convert latest image to PDF
• /convert_image 2 - Convert image #2 to PDF
• /combine_images - Combine ALL images into 1 PDF

💡 **Reply Feature:**
Reply to any PDF message with commands:
• Reply + /merge → Shows merge options
• Reply + /split pages → Splits that PDF
• Reply + /to_images → Converts that PDF

📝 **Custom Filenames:**
After processing, you'll be asked to name your file!

📋 **File Management:**
• /list - Show all uploaded files
• /clear - Clear all uploaded files

📁 **Supported Formats:**
• PDF files (merge, split, convert to images)
• Image files (JPG, PNG, GIF, BMP → convert/combine to PDF)

📁 Files are numbered in upload order.
    """
    await update.message.reply_text(help_message)

async def ask_for_filename(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str, file_type: str, operation_info: str):
    """Ask user for custom filename before sending processed file"""
    user_id = update.effective_user.id
    
    # Store file info for later use
    pending_files[user_id] = {
        'file_path': file_path,
        'file_type': file_type,
        'operation_info': operation_info,
        'message_to_reply': update.message
    }
    
    await update.message.reply_text(
        f"✅ {operation_info}\n\n"
        f"📝 **Please enter a filename for your {file_type}:**\n"
        f"(Just type the name, extension will be added automatically)\n\n"
        f"Example: `my_document` → `my_document.{file_type.split('.')[-1]}`"
    )
    
    return WAITING_FOR_FILENAME

async def handle_filename_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the filename input from user"""
    user_id = update.effective_user.id
    
    # Immediate acknowledgment
    await update.message.reply_text("⚡ Processing...")
    
    if user_id not in pending_files:
        await update.message.reply_text("❌ No pending file to rename. Please try the operation again.")
        return ConversationHandler.END
    
    file_info = pending_files[user_id]
    filename = update.message.text.strip()
    
    # Sanitize filename
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if not filename:
        filename = "document"
    
    # Add extension based on file type
    if file_info['file_type'] == 'pdf':
        final_filename = f"{filename}.pdf"
    elif file_info['file_type'] == 'zip':
        final_filename = f"{filename}.zip"
    else:
        final_filename = filename
    
    # Send the file with custom name
    try:
        # Show processing status first
        status_msg = await update.message.reply_text(f"📤 Sending {final_filename}...")
        
        with open(file_info['file_path'], 'rb') as f:
            sent_message = await file_info['message_to_reply'].reply_document(
                document=f,
                filename=final_filename,
                caption=f"📄 **{final_filename}**\n{file_info['operation_info']}",
                read_timeout=30,
                write_timeout=30,
                connect_timeout=10
            )
        
        # Store the sent file for future reply commands
        if user_id not in user_files:
            user_files[user_id] = []
        
        # Create a copy of the file for reply functionality
        temp_dir = tempfile.mkdtemp()
        new_file_path = os.path.join(temp_dir, final_filename)
        
        # Copy file before cleaning up original
        shutil.copy2(file_info['file_path'], new_file_path)
        
        # Add to user files with new message ID
        user_files[user_id].append({
            'name': final_filename,
            'path': new_file_path,
            'message_id': sent_message.message_id
        })
        
        # Clean up original file
        os.remove(file_info['file_path'])
        del pending_files[user_id]
        
        # Update status message
        await status_msg.edit_text(f"✅ File sent as `{final_filename}`! You can now reply to it with commands.")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error sending file: {str(e)}")
        if user_id in pending_files:
            del pending_files[user_id]
    
    return ConversationHandler.END

async def cancel_rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the rename operation"""
    user_id = update.effective_user.id
    
    if user_id in pending_files:
        # Send with default name
        file_info = pending_files[user_id]
        default_filename = f"document.{file_info['file_type'].split('.')[-1]}"
        
        try:
            with open(file_info['file_path'], 'rb') as f:
                sent_message = await file_info['message_to_reply'].reply_document(
                    document=f,
                    filename=default_filename,
                    caption=f"📄 **{default_filename}**\n{file_info['operation_info']}",
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=10
                )
            
            # Store the sent file for future reply commands
            if user_id not in user_files:
                user_files[user_id] = []
            
            # Create a copy of the file for reply functionality
            temp_dir = tempfile.mkdtemp()
            new_file_path = os.path.join(temp_dir, default_filename)
            
            # Copy file before cleaning up original
            shutil.copy2(file_info['file_path'], new_file_path)
            
            # Add to user files with new message ID
            user_files[user_id].append({
                'name': default_filename,
                'path': new_file_path,
                'message_id': sent_message.message_id
            })
            
            os.remove(file_info['file_path'])
            del pending_files[user_id]
            await update.message.reply_text("✅ File sent with default name! You can now reply to it with commands.")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error sending file: {str(e)}")
            if user_id in pending_files:
                del pending_files[user_id]
    else:
        await update.message.reply_text("❌ No pending file to cancel.")
    
    return ConversationHandler.END

async def list_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all uploaded files"""
    user_id = update.effective_user.id
    
    if user_id not in user_files or len(user_files[user_id]) == 0:
        await update.message.reply_text("📁 No files uploaded yet! Send me a PDF or image file to get started.")
        return
    
    # Separate files by type
    pdf_files = [f for f in user_files[user_id] if f.get('type', 'pdf') == 'pdf']
    image_files = [f for f in user_files[user_id] if f.get('type') == 'image']
    
    file_list = "📁 **Your uploaded files:**\n\n"
    
    if pdf_files:
        file_list += "📄 **PDFs:**\n"
        for i, file_info in enumerate(pdf_files, 1):
            file_list += f"{i}. {file_info['name']}\n"
        file_list += "\n"
    
    if image_files:
        file_list += "🖼️ **Images:**\n"
        for i, file_info in enumerate(image_files, 1):
            file_list += f"{i}. {file_info['name']}\n"
        file_list += "\n"
    
    file_list += f"📊 **Total:** {len(user_files[user_id])} files"
    
    await update.message.reply_text(file_list)

async def clear_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all uploaded files"""
    user_id = update.effective_user.id
    
    if user_id in user_files:
        # Clean up temporary files
        for file_info in user_files[user_id]:
            try:
                os.remove(file_info['path'])
            except:
                pass
        del user_files[user_id]
    
    await update.message.reply_text("🗑️ All uploaded files cleared!")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF document uploads with memory optimization"""
    user_id = update.effective_user.id
    
    # Memory check first
    if not check_memory_limit():
        await update.message.reply_text("⚠️ Service busy. Please try again in a moment.")
        return
    
    if not update.message.document.mime_type == 'application/pdf':
        await update.message.reply_text("❌ Please send PDF files only.")
        return
    
    # Check file size before download
    file_size_mb = update.message.document.file_size / 1024 / 1024
    if file_size_mb > MAX_FILE_SIZE_MB:
        await update.message.reply_text(f"❌ File too large ({file_size_mb:.1f}MB). Max size: {MAX_FILE_SIZE_MB}MB")
        return
    
    # Check user file limits
    if user_id in user_files and len(user_files[user_id]) >= MAX_FILES_PER_USER:
        await update.message.reply_text(f"⚠️ File limit reached ({MAX_FILES_PER_USER}). Use /clear to remove old files.")
        return
    
    try:
        # Download file with memory monitoring
        file = await update.message.document.get_file()
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, update.message.document.file_name)
        await file.download_to_drive(file_path)
        
        # Check memory after download
        if not check_memory_limit():
            # Cleanup and abort
            try:
                os.remove(file_path)
                os.rmdir(temp_dir)
            except:
                pass
            await update.message.reply_text("⚠️ Memory limit reached. File removed.")
            return
        
        # Store file info
        if user_id not in user_files:
            user_files[user_id] = []
        
        file_number = len(user_files[user_id]) + 1
        user_files[user_id].append({
            'name': update.message.document.file_name,
            'path': file_path,
            'message_id': update.message.message_id
        })
        
        await update.message.reply_text(f"📄 PDF uploaded as file #{file_number}: {update.message.document.file_name}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing PDF: {str(e)}")

async def handle_image_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image uploads and store for PDF conversion"""
    user_id = update.effective_user.id
    
    # Check file type
    mime_type = update.message.document.mime_type
    file_name = update.message.document.file_name
    
    # Check if it's an image
    if not (mime_type and mime_type.startswith('image/')):
        await update.message.reply_text("❌ Please send image files only.")
        return
    
    # Performance optimization: limit files per user
    if user_id in user_files and len(user_files[user_id]) >= MAX_FILES_PER_USER:
        await update.message.reply_text(f"⚠️ File limit reached ({MAX_FILES_PER_USER}). Use /clear to remove old files.")
        return
    
    # Show processing status
    status_message = await update.message.reply_text("� Processing image...")
    
    try:
        # Download file
        file = await update.message.document.get_file()
        temp_dir = tempfile.mkdtemp()
        image_file_path = os.path.join(temp_dir, file_name)
        await file.download_to_drive(image_file_path)
        
        # Store image in user files for combining
        if user_id not in user_files:
            user_files[user_id] = []
        
        user_files[user_id].append({
            'name': file_name,
            'path': image_file_path,
            'type': 'image',
            'size': update.message.document.file_size
        })
        
        await status_message.edit_text(
            f"✅ Image received: {file_name}\n\n"
            f"📁 Your uploaded images: {len([f for f in user_files[user_id] if f['type'] == 'image'])}\n\n"
            f"📋 Options:\n"
            f"• Upload more images and use /combine_images\n"
            f"• Use /convert_image to convert this image to PDF\n"
            f"• Use /list to see all files"
        )
        
    except Exception as e:
        error_msg = str(e)
        await status_message.edit_text(f"❌ Error processing image: {error_msg}")
        await status_message.edit_text(f"❌ Error converting image: {error_msg}")

async def handle_any_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any document upload and route to appropriate handler"""
    # Emergency wake for file uploads (critical operation)
    emergency_wake()
    await wake_service_on_activity()
    
    mime_type = update.message.document.mime_type
    file_name = update.message.document.file_name.lower() if update.message.document.file_name else ""
    
    # Check if it's a PDF
    if mime_type == 'application/pdf':
        return await handle_document(update, context)
    
    # Check if it's an image
    elif mime_type and mime_type.startswith('image/'):
        return await handle_image_document(update, context)
    
    # Unsupported file type
    else:
        await update.message.reply_text(
            "❌ Unsupported file type!\n\n"
            "📄 **Supported formats:**\n"
            "• PDF files (.pdf)\n"
            "• Image files (.jpg, .png, .jpeg, .gif, .bmp)\n\n"
            "💡 Upload one of these file types to get started!"
        )

async def merge_with_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show merge options when replying to a PDF"""
    user_id = update.effective_user.id
    
    replied_pdf = find_replied_pdf(update, user_id)
    if not replied_pdf:
        await update.message.reply_text("❌ Please reply to a PDF file to merge with others.")
        return
    
    if user_id not in user_files or len(user_files[user_id]) <= 1:
        await update.message.reply_text("❌ You need at least 2 PDFs to merge. Upload more files first.")
        return
    
    # Show available files to merge with
    merge_list = f"🔗 **Merge {replied_pdf['name']} with:**\n\n"
    merge_list += "Available files:\n"
    for i, file_info in enumerate(user_files[user_id], 1):
        if file_info['message_id'] != replied_pdf['message_id']:
            merge_list += f"{i}. {file_info['name']}\n"
    
    merge_list += f"\n💡 **Usage:** Reply with /merge to include this PDF in merge order"
    
    await update.message.reply_text(merge_list)
    
    file_list += "\n📋 Use commands:\n"
    file_list += "• /merge 1,2,3\n• /split 2 5-10\n• /to_images 1"
    
    await update.message.reply_text(file_list)

async def clear_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all uploaded files"""
    user_id = update.effective_user.id
    
    if user_id in user_files:
        # Clean up temporary files
        for file_info in user_files[user_id]:
            try:
                if os.path.exists(file_info['path']):
                    os.remove(file_info['path'])
            except Exception:
                pass
        
        del user_files[user_id]
        await update.message.reply_text("✅ All your uploaded files have been cleared!")
    else:
        await update.message.reply_text("No files to clear!")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded PDF documents"""
    document = update.message.document
    user_id = update.effective_user.id
    
    # Check if it's a PDF
    if not document.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("Please send only PDF files!")
        return
    
    try:
        # Download the file
        file = await context.bot.get_file(document.file_id)
        
        # Create temp directory if not exists
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, document.file_name)
        
        # Download file
        await file.download_to_drive(file_path)
        
        # Store file info
        if user_id not in user_files:
            user_files[user_id] = []
        
        file_info = {
            'name': document.file_name,
            'path': file_path,
            'message_id': update.message.message_id  # Store message ID for reply detection
        }
        user_files[user_id].append(file_info)
        
        # Show updated file list
        file_list = ""
        for i, file_info in enumerate(user_files[user_id], 1):
            file_list += f"{i}. {file_info['name']}\n"
        
        await update.message.reply_text(
            f"✅ PDF received: {update.message.document.file_name}\n\n"
            f"📁 Your uploaded PDFs:\n{file_list}\n"
            f"📋 Use commands:\n"
            f"• /merge [numbers] - e.g., /merge 1,3,2\n"
            f"• /split [number] [pages] - e.g., /split 2 5-8\n"
            f"• /to_images [number] - e.g., /to_images 1\n"
            f"• /list - Show all uploaded files\n"
            f"• /clear - Clear all files\n\n"
            f"💡 **NEW: Reply Feature!**\n"
            f"• Reply with: /merge\n"
            f"• Reply with: /split pages\n"
            f"• Reply with: /to_images"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing PDF: {str(e)}")

async def merge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memory-optimized merge PDF command handler"""
    user_id = update.effective_user.id
    
    # Memory check before processing
    if not check_memory_limit():
        await update.message.reply_text("⚠️ Service busy. Please try again in a moment.")
        return
    
    if user_id not in user_files or len(user_files[user_id]) == 0:
        await update.message.reply_text("Please upload PDF files before merging.")
        return
    
    # Check if this is a reply to a PDF
    replied_pdf = find_replied_pdf(update, user_id)
    
    if replied_pdf:
        # Reply mode: show list of other files to merge with
        other_files = [f for f in user_files[user_id] if f != replied_pdf]
        
        if not other_files:
            await update.message.reply_text("❌ No other files available to merge with this PDF!")
            return
        
        file_list = f"📋 **Merge with {replied_pdf['name']}**\n\nChoose files to merge:\n\n"
        for i, file_info in enumerate(other_files, 1):
            file_list += f"{i}. {file_info['name']}\n"
        
        file_list += f"\n💡 Use: `/merge_with 1,2,3` to merge selected files with {replied_pdf['name']}"
        
        await update.message.reply_text(file_list)
        return
    
    # Regular merge logic
    try:
        all_files = user_files[user_id]
        
        if len(context.args) > 0:
            # Parse specific file numbers
            try:
                file_numbers = [int(x.strip()) for x in context.args[0].split(',')]
                selected_files = []
                file_names = []
                
                for num in file_numbers:
                    if 1 <= num <= len(all_files):
                        selected_files.append(all_files[num-1])
                        file_names.append(all_files[num-1]['name'])
                    else:
                        await update.message.reply_text(f"❌ File #{num} doesn't exist. Use /list to see available files.")
                        return
                
            except ValueError:
                await update.message.reply_text("❌ Invalid format. Use: /merge 1,2,3")
                return
        else:
            # Merge all files
            selected_files = all_files
            file_names = [f['name'] for f in selected_files]
        
        if len(selected_files) < 2:
            await update.message.reply_text("Need at least 2 files to merge!")
            return
        
        # Show processing status
        status_message = await update.message.reply_text(f"🔄 Merging {len(selected_files)} PDF files...")
        
        # Create temporary output file
        temp_dir = tempfile.mkdtemp()
        merged_file = os.path.join(temp_dir, "merged.pdf")
        
        # Merge PDFs using lazy import
        merge_pdfs, _, _, _, _ = lazy_import_pdf_utils()
        if merge_pdfs is None:
            await update.message.reply_text("❌ PDF utilities not available.")
            return
        
        file_paths = [f['path'] for f in selected_files]
        merge_pdfs(file_paths, merged_file)
        
        # Update status
        await status_message.edit_text(f"✅ Merge completed!")
        
        # Create merge summary
        merge_summary = f"Successfully merged {len(selected_files)} PDF files!\n\nMerged files:\n" + "\n".join([f"• {name}" for name in file_names])
        
        # Ask for filename instead of sending directly
        return await ask_for_filename(update, context, merged_file, "pdf", merge_summary)
        
    except Exception as e:
        error_msg = str(e)
        if "timed out" in error_msg.lower():
            await update.message.reply_text(
                "⚠️ Processing took longer than expected, but your files are likely being merged.\n"
                "Please wait a moment for the result."
            )
        else:
            await update.message.reply_text(f"❌ Error merging PDFs: {error_msg}")

async def merge_with_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Merge with replied PDF using specified file numbers"""
    user_id = update.effective_user.id
    
    if user_id not in user_files or len(user_files[user_id]) == 0:
        await update.message.reply_text("Please upload PDF files first.")
        return
    
    # Find the replied PDF
    replied_pdf = find_replied_pdf(update, user_id)
    if not replied_pdf:
        # Show available files to merge with if no reply
        file_list = "🔗 **Available PDFs to merge:**\n\n"
        for i, file_info in enumerate(user_files[user_id], 1):
            file_list += f"{i}. {file_info['name']}\n"
        file_list += f"\n💡 Use: `/merge_with 1,2,3` to merge selected files\n💡 Or reply to a PDF and use `/merge_with 1,2` to merge with it"
        await update.message.reply_text(file_list)
        return
    
    if not context.args:
        # Show available files to merge with the replied PDF
        merge_list = f"🔗 **Merge '{replied_pdf['name']}' with:**\n\n"
        merge_list += "Available files:\n"
        for i, file_info in enumerate(user_files[user_id], 1):
            if file_info['message_id'] != replied_pdf['message_id']:
                merge_list += f"{i}. {file_info['name']}\n"
        merge_list += f"\n💡 **Usage:** `/merge_with 1,2,3` (file numbers to merge with {replied_pdf['name']})"
        await update.message.reply_text(merge_list)
        return
    
    try:
        # Parse file numbers from all files (including the replied one)
        file_numbers = [int(x.strip()) for x in context.args[0].split(',')]
        selected_files = [replied_pdf]  # Start with replied PDF
        file_names = [replied_pdf['name']]
        
        # Add other selected files
        for num in file_numbers:
            if 1 <= num <= len(user_files[user_id]):
                selected_file = user_files[user_id][num-1]
                # Don't add the replied PDF twice
                if selected_file['message_id'] != replied_pdf['message_id']:
                    selected_files.append(selected_file)
                    file_names.append(selected_file['name'])
            else:
                await update.message.reply_text(f"❌ File #{num} doesn't exist. Use /list to see available files.")
                return
        
        if len(selected_files) < 2:
            await update.message.reply_text("❌ You need at least 2 files to merge. Select more files.")
            return
        
        # Show processing status
        status_message = await update.message.reply_text(f"🔄 Merging {len(selected_files)} PDF files...")
        
        # Create temporary output file
        temp_dir = tempfile.mkdtemp()
        merged_file = os.path.join(temp_dir, "merged.pdf")
        
        # Merge PDFs using lazy import
        merge_pdfs, _, _, _, _ = lazy_import_pdf_utils()
        if merge_pdfs is None:
            await update.message.reply_text("❌ PDF utilities not available.")
            return
        
        file_paths = [f['path'] for f in selected_files]
        merge_pdfs(file_paths, merged_file)
        
        # Update status
        await status_message.edit_text(f"✅ Merge completed!")
        
        # Create merge summary
        merge_summary = f"Successfully merged {len(selected_files)} PDF files!\n\nMerged files:\n" + "\n".join([f"• {name}" for name in file_names])
        
        # Ask for filename instead of sending directly
        return await ask_for_filename(update, context, merged_file, "pdf", merge_summary)
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error merging PDFs: {str(e)}")

async def split_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Split PDF command handler"""
    user_id = update.effective_user.id
    
    if user_id not in user_files or len(user_files[user_id]) == 0:
        await update.message.reply_text("Please upload a PDF file before splitting.")
        return
    
    # Check if this is a reply to a PDF
    replied_pdf = find_replied_pdf(update, user_id)
    
    if replied_pdf:
        # Reply mode: use the replied PDF directly
        if not context.args:
            await update.message.reply_text(
                f"📄 **Split {replied_pdf['name']}**\n\n"
                "Please specify page range:\n"
                "• Reply with: `/split 5-8` (pages 5 to 8)\n"
                "• Reply with: `/split 3` (page 3 only)"
            )
            return
        
        page_range = " ".join(context.args)
        selected_file = replied_pdf
        
        try:
            # Show processing status
            status_message = await update.message.reply_text(f"🔄 Splitting {selected_file['name']}...")
            
            # Create output directory
            temp_dir = tempfile.mkdtemp()
            output_filename = f"split_{selected_file['name']}"
            output_path = os.path.join(temp_dir, output_filename)
            
            pdf_path = selected_file['path']
            
            # Split PDF using lazy import
            _, split_pdf, _, _, _ = lazy_import_pdf_utils()
            if split_pdf is None:
                await status_message.edit_text("❌ PDF utilities not available.")
                return
            
            split_file = split_pdf(pdf_path, page_range, output_path)
            
            # Update status
            await status_message.edit_text(f"✅ Split completed!")
            
            # Ask for filename instead of sending directly
            operation_info = f"Extracted pages {page_range} from {selected_file['name']}!"
            return await ask_for_filename(update, context, split_file, "pdf", operation_info)
        
        except Exception as e:
            error_msg = str(e)
            if "timed out" in error_msg.lower():
                await update.message.reply_text(
                    "⚠️ Processing took longer than expected, but your file is likely being split.\n"
                    "Please wait a moment for the result."
                )
            else:
                await update.message.reply_text(f"❌ Error splitting PDF: {error_msg}")
        return
    
    # Regular split command logic
    if len(context.args) < 2:
        await update.message.reply_text(
            "Please specify file number and page range.\n\n"
            "Examples:\n"
            "• /split 1 5-8 (split file #1, pages 5-8)\n"
            "• /split 2 3 (split file #2, page 3 only)\n\n"
            "Use /list to see your uploaded files.\n\n"
            "💡 **TIP**: Reply to any PDF with /split [pages]"
        )
        return
    
    try:
        file_number = int(context.args[0])
        page_range = " ".join(context.args[1:])
        
        if file_number < 1 or file_number > len(user_files[user_id]):
            await update.message.reply_text("❌ Invalid file number. Use /list to see your files.")
            return
        
        selected_file = user_files[user_id][file_number - 1]
        
        # Show processing status
        status_message = await update.message.reply_text(f"🔄 Splitting {selected_file['name']}...")
        
        # Create output directory
        temp_dir = tempfile.mkdtemp()
        output_filename = f"split_{selected_file['name']}"
        output_path = os.path.join(temp_dir, output_filename)
        
        pdf_path = selected_file['path']
        
        # Split PDF using lazy import
        _, split_pdf, _, _, _ = lazy_import_pdf_utils()
        if split_pdf is None:
            await status_message.edit_text("❌ PDF utilities not available.")
            return
        
        split_file = split_pdf(pdf_path, page_range, output_path)
        
        # Update status
        await status_message.edit_text(f"✅ Split completed!")
        
        # Ask for filename instead of sending directly
        operation_info = f"Extracted pages {page_range} from {selected_file['name']}!"
        return await ask_for_filename(update, context, split_file, "pdf", operation_info)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid file number. Please use a valid number from your file list.")
    except Exception as e:
        error_msg = str(e)
        if "timed out" in error_msg.lower():
            await update.message.reply_text(
                "⚠️ Processing took longer than expected, but your file is likely being split.\n"
                "Please wait a moment for the result."
            )
        else:
            await update.message.reply_text(f"❌ Error splitting PDF: {error_msg}")

async def to_images_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert PDF to images command handler"""
    if not check_memory_limit():
        await update.message.reply_text("⚠️ Service temporarily busy. Please try again.")
        return
        
    await wake_service_on_activity()
    
    user_id = update.effective_user.id
    
    # Check if this is a reply to a PDF
    replied_pdf = find_replied_pdf(update, user_id)
    
    if replied_pdf:
        # Reply mode: use the replied PDF directly
        selected_file = replied_pdf
        
        try:
            pdf_path = selected_file['path']
            
            # Create output directory
            temp_dir = tempfile.mkdtemp()
            images_dir = os.path.join(temp_dir, "images")
            
            # Get PDF utilities
            _, _, pdf_to_images_func, create_zip_from_images, _ = lazy_import_pdf_utils()
            if pdf_to_images_func is None or create_zip_from_images is None:
                await update.message.reply_text("❌ PDF utilities not available.")
                return
            
            # Convert to images
            image_paths = pdf_to_images_func(pdf_path, images_dir)
            
            # Create ZIP file
            zip_filename = f"images_{selected_file['name'].replace('.pdf', '')}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            zip_file = create_zip_from_images(image_paths, zip_path)
            
            # Ask for filename instead of sending directly
            operation_info = f"Converted {len(image_paths)} pages from {selected_file['name']} to images!"
            return await ask_for_filename(update, context, zip_file, "zip", operation_info)
            
        except Exception as e:
            error_msg = str(e)
            await update.message.reply_text(f"❌ Error converting PDF to images: {error_msg}")
        return
    
    # Regular to_images command logic
    if user_id not in user_files or not user_files[user_id]:
        await update.message.reply_text("❌ No PDFs uploaded. Please upload a PDF first.")
        return
        
    try:
        if len(context.args) > 0:
            file_number = int(context.args[0])
            if file_number < 1 or file_number > len(user_files[user_id]):
                await update.message.reply_text("❌ Invalid file number. Use /list to see your files.")
                return
            selected_file = user_files[user_id][file_number - 1]
        else:
            # Use the latest uploaded file
            selected_file = user_files[user_id][-1]
        
        pdf_path = selected_file['path']
        
        # Create output directory
        temp_dir = tempfile.mkdtemp()
        images_dir = os.path.join(temp_dir, "images")
        
        # Get PDF utilities
        _, _, pdf_to_images_func, create_zip_from_images, _ = lazy_import_pdf_utils()
        if pdf_to_images_func is None or create_zip_from_images is None:
            await update.message.reply_text("❌ PDF utilities not available.")
            return
        
        # Convert to images
        image_paths = pdf_to_images_func(pdf_path, images_dir)
        
        # Create ZIP file
        zip_filename = f"images_{selected_file['name'].replace('.pdf', '')}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        zip_file = create_zip_from_images(image_paths, zip_path)
        
        # Ask for filename instead of sending directly
        operation_info = f"Converted {len(image_paths)} pages from {selected_file['name']} to images!"
        return await ask_for_filename(update, context, zip_file, "zip", operation_info)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid file number. Use /list to see your files.")
    except Exception as e:
        error_msg = str(e)
        await update.message.reply_text(f"❌ Error converting PDF to images: {error_msg}")

async def convert_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert a single image to PDF"""
    if not check_memory_limit():
        await update.message.reply_text("⚠️ Service temporarily busy. Please try again.")
        return
        
    await wake_service_on_activity()
    
    user_id = update.effective_user.id
    
    if user_id not in user_files or not user_files[user_id]:
        await update.message.reply_text("❌ No files uploaded. Please upload an image first.")
        return
    
    # Find image files
    image_files = [f for f in user_files[user_id] if f.get('type') == 'image']
    if not image_files:
        await update.message.reply_text("❌ No image files found. Please upload an image first.")
        return
    
    try:
        # Use specified image or latest
        if len(context.args) > 0:
            file_number = int(context.args[0])
            if file_number < 1 or file_number > len(image_files):
                await update.message.reply_text(f"❌ Invalid image number. You have {len(image_files)} images.")
                return
            selected_file = image_files[file_number - 1]
        else:
            selected_file = image_files[-1]  # Latest image
        
        # Convert to PDF
        temp_dir = tempfile.mkdtemp()
        pdf_filename = selected_file['name'].rsplit('.', 1)[0] + '.pdf'
        pdf_file_path = os.path.join(temp_dir, pdf_filename)
        
        _, _, _, _, image_to_pdf = lazy_import_pdf_utils()
        if image_to_pdf is None:
            await update.message.reply_text("❌ PDF utilities not available.")
            return
        
        image_to_pdf(selected_file['path'], pdf_file_path)
        
        # Ask for filename
        operation_info = f"Converted image '{selected_file['name']}' to PDF!"
        return await ask_for_filename(update, context, pdf_file_path, "pdf", operation_info)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid image number.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error converting image: {e}")

async def combine_images_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Combine multiple images into a single PDF"""
    if not check_memory_limit():
        await update.message.reply_text("⚠️ Service temporarily busy. Please try again.")
        return
        
    await wake_service_on_activity()
    
    user_id = update.effective_user.id
    
    if user_id not in user_files or not user_files[user_id]:
        await update.message.reply_text("❌ No files uploaded. Please upload images first.")
        return
    
    # Find image files
    image_files = [f for f in user_files[user_id] if f.get('type') == 'image']
    if len(image_files) < 2:
        await update.message.reply_text(f"❌ Need at least 2 images to combine. You have {len(image_files)} images.")
        return
    
    try:
        status_message = await update.message.reply_text("🔄 Combining images into PDF...")
        
        # Get image paths
        image_paths = [f['path'] for f in image_files]
        
        # Create combined PDF
        temp_dir = tempfile.mkdtemp()
        pdf_filename = "combined_images.pdf"
        pdf_file_path = os.path.join(temp_dir, pdf_filename)
        
        # Import images_to_pdf function
        from utils.pdf_utils import images_to_pdf
        images_to_pdf(image_paths, pdf_file_path)
        
        await status_message.edit_text("✅ Images combined successfully!")
        
        # Ask for filename
        operation_info = f"Combined {len(image_files)} images into PDF!"
        return await ask_for_filename(update, context, pdf_file_path, "pdf", operation_info)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error combining images: {e}")

def start_bot():
    """Start the bot with conflict prevention"""
    print("🔍 Testing PDF utilities import at startup...")
    print(f"Current working directory: {os.getcwd()}")
    
    # Start auto-wake service to prevent sleeping
    start_auto_wake_service()
    
    # Test PDF utilities import
    merge_pdfs, split_pdf, pdf_to_images, create_zip_from_images, image_to_pdf = lazy_import_pdf_utils()
    if merge_pdfs is not None:
        print("✅ PDF utilities loaded successfully")
    else:
        print("❌ PDF utilities failed to load")
        
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TOKEN')
    
    if BOT_TOKEN == 'YOUR_TOKEN':
        print("❌ Please set your bot token!")
        print("Set BOT_TOKEN environment variable or edit bot.py")
        return
    
    # Enhanced conflict prevention - clear webhooks and pending updates
    try:
        import telegram
        bot = telegram.Bot(token=BOT_TOKEN)
        
        print("🔧 Checking for webhook conflicts...")
        
        # Get current webhook info
        import asyncio
        loop = asyncio.get_event_loop()
        webhook_info = loop.run_until_complete(bot.get_webhook_info())
        
        if webhook_info.url:
            print(f"🔍 Found existing webhook: {webhook_info.url}")
            print("🗑️ Clearing webhook to enable polling...")
            loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
            print("✅ Webhook cleared successfully")
        else:
            print("ℹ️ No webhook found - clearing pending updates...")
            loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
            print("✅ Ready for polling")
            
        # Small delay to ensure Telegram servers process the webhook deletion
        import time
        time.sleep(2)
        
    except Exception as webhook_error:
        print(f"⚠️ Could not clear webhook: {webhook_error}")
    
    # Configure HTTP timeouts in the application builder
    app = ApplicationBuilder().token(BOT_TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()
    
    # Create conversation handler for filename input from commands
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
    
    # Create a global message handler for filename input
    filename_input_handler = MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_filename_input
    )
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_files_command))
    app.add_handler(CommandHandler("clear", clear_files_command))
    
    # Add document handler BEFORE conversation handler
    app.add_handler(MessageHandler(filters.Document.ALL, handle_any_document))
    
    # Add conversation handler for commands
    app.add_handler(command_filename_handler)
    
    # Add global filename input handler
    app.add_handler(filename_input_handler)
    
    # Add a generic message handler for unknown commands/typos (must be last)
    async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands and suggest corrections"""
        text = update.message.text.lower() if update.message.text else ""
        
        if text.startswith("/merge_wth") or text.startswith("/mergewth"):
            await update.message.reply_text(
                "❓ Did you mean `/merge_with`?\n\n"
                "💡 **Usage:**\n"
                "• Reply to a PDF and use `/merge_with 1,2,3`\n"
                "• Or use `/merge` to see merge options"
            )
        elif text.startswith("/") and len(text) > 1:
            await update.message.reply_text(
                "❓ Unknown command. Use /help to see all available commands.\n\n"
                "📋 **Quick commands:**\n"
                "• /merge - Merge PDFs\n"
                "• /split - Split PDF\n" 
                "• /to_images - Convert to images\n"
                "• /merge_with - Merge with replied PDF\n"
                "• /list - Show files\n"
                "• /help - Full help"
            )
    
    app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, handle_unknown_command))
    
    # Add error handler for the application
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot"""
        logger = logging.getLogger(__name__)
        
        # Log the error
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Handle specific types of errors
        if "Conflict" in str(context.error):
            logger.warning("Conflict error detected - another bot instance may be running")
            # Don't send a message to user, just log it
            return
        elif "timed out" in str(context.error).lower():
            logger.warning("Timeout error - network issues")
            return
        
        # For other errors, try to inform the user if possible
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ Sorry, something went wrong. Please try again later."
                )
        except Exception:
            # If we can't even send an error message, just log it
            pass
    
    app.add_error_handler(error_handler)
    
    print("🚀 Page Craft Bot is starting...")
    
    # Run with error handling to prevent conflicts
    try:
        app.run_polling(
            drop_pending_updates=True,  # Clear any pending updates
            allowed_updates=Update.ALL_TYPES,
            poll_interval=2.0,  # Increase poll interval to reduce conflicts
            timeout=20,  # Increase timeout
            bootstrap_retries=3  # Retry connection failures
        )
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")
        if "Conflict" in str(e):
            print("🔄 Another bot instance may be running. Retrying in 30 seconds...")
            import time
            time.sleep(30)
            # Try again with even higher timeouts
            try:
                app.run_polling(
                    drop_pending_updates=True,
                    allowed_updates=Update.ALL_TYPES,
                    poll_interval=5.0,
                    timeout=30,
                    bootstrap_retries=5
                )
            except Exception as retry_error:
                print(f"❌ Bot failed to start after retry: {retry_error}")
                raise retry_error
        else:
            raise e
