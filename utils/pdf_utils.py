# PDF utility functions for merging, splitting, and converting PDFs
import os
import zipfile
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import tempfile

def merge_pdfs(pdf_files, output_path="merged.pdf"):
    """
    Merge multiple PDF files into one.
    
    Args:
        pdf_files: List of file paths to PDF files
        output_path: Output file path for merged PDF
    
    Returns:
        str: Path to the merged PDF file
    """
    writer = PdfWriter()
    
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            writer.add_page(page)
    
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
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    
    # Parse page range
    if '-' in page_range:
        start_page, end_page = map(int, page_range.split('-'))
        start_page -= 1  # Convert to 0-based indexing
        end_page -= 1
    else:
        start_page = int(page_range) - 1  # Convert to 0-based indexing
        end_page = start_page
    
    # Add pages to writer
    for page_num in range(start_page, end_page + 1):
        if page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    return output_path

def pdf_to_images(pdf_file, output_dir="images", format="PNG"):
    """
    Convert PDF pages to images.
    
    Args:
        pdf_file: Path to the input PDF file
        output_dir: Directory to save images
        format: Image format (PNG or JPEG)
    
    Returns:
        list: List of image file paths
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert PDF to images
        images = convert_from_path(pdf_file)
        image_paths = []
        
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"page_{i+1}.{format.lower()}")
            image.save(image_path, format)
            image_paths.append(image_path)
        
        return image_paths
    
    except Exception as e:
        # Handle poppler not installed error
        if "poppler" in str(e).lower():
            raise Exception("Poppler is required for PDF to image conversion. "
                          "Please install poppler-utils (Linux) or poppler (Windows/Mac)")
        else:
            raise e

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

def word_to_pdf(word_file, output_path="converted.pdf"):
    """
    Convert Word document to PDF using Linux-compatible pure Python libraries.
    
    Args:
        word_file: Path to the input Word file (.docx, .doc)
        output_path: Output file path for PDF
    
    Returns:
        str: Path to the converted PDF file
    """
    try:
        from docx import Document
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Read the Word document
        doc = Document(word_file)
        
        # Create PDF
        pdf_doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                p = Paragraph(paragraph.text, styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 12))
        
        pdf_doc.build(story)
        return output_path
        
    except ImportError as e:
        raise Exception(f"Word to PDF conversion requires python-docx and reportlab packages: {e}")
    except Exception as e:
        raise Exception(f"Error converting Word document: {e}")
