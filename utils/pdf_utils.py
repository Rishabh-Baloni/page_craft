# PDF utility functions for merging, splitting, and converting PDFs
import os
import zipfile
from pypdf import PdfReader, PdfWriter
import tempfile

# Note: pdf2image and PIL imports moved to functions for memory optimization

def merge_pdfs(pdf_files, output_path="merged.pdf"):
    """
    Merge multiple PDF files into one.
    
    Args:
        pdf_files: List of file paths to PDF files
        output_path: Output file path for merged PDF
    
    Returns:
        str: Path to the merged PDF file
    """
    if not pdf_files or len(pdf_files) == 0:
        raise ValueError("At least one PDF file is required for merging")
    
    if len(pdf_files) == 1:
        raise ValueError("At least two PDF files are required for merging")
    
    writer = PdfWriter()
    
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")
        
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            raise Exception(f"Error reading PDF file {pdf_file}: {e}")
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    return output_path

def split_pdf(pdf_file, page_range, output_path="split.pdf"):
    """
    Split a PDF file by extracting specific pages.
    
    Args:
        pdf_file: Path to the input PDF file
        page_range: String like "5-8" or "3" for page range or single page
        output_path: Output file path for split PDF
    
    Returns:
        str: Path to the split PDF file
    """
    if not os.path.exists(pdf_file):
        raise FileNotFoundError(f"PDF file not found: {pdf_file}")
    
    try:
        reader = PdfReader(pdf_file)
        total_pages = len(reader.pages)
        
        # Parse page range
        if '-' in page_range:
            start_page, end_page = page_range.split('-')
            start_page = int(start_page) - 1  # Convert to 0-based index
            end_page = int(end_page) - 1      # Convert to 0-based index
        else:
            start_page = end_page = int(page_range) - 1  # Single page
        
        # Validate page range
        if start_page < 0 or end_page >= total_pages or start_page > end_page:
            raise ValueError(f"Invalid page range. PDF has {total_pages} pages.")
        
        writer = PdfWriter()
        for page_num in range(start_page, end_page + 1):
            writer.add_page(reader.pages[page_num])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error splitting PDF: {e}")

def pdf_to_images(pdf_path, output_dir=None):
    """
    Convert PDF pages to images with memory optimization for free tier.
    
    Args:
        pdf_file: Path to the input PDF file
        output_dir: Directory to save images
        format: Image format (PNG or JPEG)
    
    Returns:
        list: List of image file paths
    """
    try:
        # Memory optimized PDF to images conversion
        from pdf2image import convert_from_path
        
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        # Convert with memory optimization settings
        images = convert_from_path(
            pdf_path,
            dpi=150,  # Lower DPI to save memory
            output_folder=output_dir,
            fmt='JPEG',  # JPEG uses less memory than PNG
            jpegopt={'quality': 85, 'progressive': True, 'optimize': True},
            thread_count=1,  # Single thread to limit memory
            poppler_path=None
        )
        
        # Save images with optimized settings
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
            # Optimize image size for memory
            image.save(image_path, "JPEG", quality=85, optimize=True)
            image_paths.append(image_path)
        
        return image_paths
        
    except ImportError:
        raise RuntimeError("PDF to images conversion requires pdf2image package. "
                         "Install with: pip install pdf2image")
    except Exception as e:
        raise RuntimeError(f"Error converting PDF to images: {e}")

def create_zip_from_images(image_paths, zip_path="images.zip"):
    """
    Create a ZIP file containing all images.
    
    Args:
        image_paths: List of image file paths
        zip_path: Output ZIP file path
    
    Returns:
        str: Path to the ZIP file
    """
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for image_path in image_paths:
            zipf.write(image_path, os.path.basename(image_path))
    
    return zip_path

def image_to_pdf(image_path, output_path):
    """Convert a single image to PDF"""
    try:
        from PIL import Image
        
        # Open image and convert to RGB if necessary
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as PDF
        image.save(output_path, "PDF")
        
    except ImportError:
        # Fallback using reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.utils import ImageReader
        
        # Get image dimensions
        img = ImageReader(image_path)
        img_width, img_height = img.getSize()
        
        # Create PDF with image
        c = canvas.Canvas(output_path, pagesize=letter)
        page_width, page_height = letter
        
        # Scale image to fit page
        scale = min(page_width / img_width, page_height / img_height)
        scaled_width = img_width * scale
        scaled_height = img_height * scale
        
        # Center image on page
        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height) / 2
        
        c.drawImage(image_path, x, y, width=scaled_width, height=scaled_height)
        c.save()

def images_to_pdf(image_paths, output_path):
    """Convert multiple images to a single PDF"""
    try:
        from PIL import Image
        
        # Convert first image and prepare for PDF
        images = []
        for image_path in image_paths:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            images.append(image)
        
        # Save all images as PDF pages
        if images:
            images[0].save(output_path, "PDF", save_all=True, append_images=images[1:])
            
    except ImportError:
        # Fallback using reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.utils import ImageReader
        
        c = canvas.Canvas(output_path, pagesize=letter)
        page_width, page_height = letter
        
        for image_path in image_paths:
            # Get image dimensions
            img = ImageReader(image_path)
            img_width, img_height = img.getSize()
            
            # Scale image to fit page
            scale = min(page_width / img_width, page_height / img_height)
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # Center image on page
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            c.drawImage(image_path, x, y, width=scaled_width, height=scaled_height)
            c.showPage()  # Start new page for next image
        
        c.save()
