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
    Convert PDF pages to images (disabled for memory optimization).
    
    Args:
        pdf_file: Path to the input PDF file
        output_dir: Directory to save images
        format: Image format (PNG or JPEG)
    
    Returns:
        list: Empty list (feature disabled for memory constraints)
    """
    raise Exception("PDF to images conversion disabled to save memory on free tier. "
                   "Please use PDF merge/split features instead.")

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
    Lightweight Word document to PDF conversion for memory-constrained environments.
    Uses only python-docx + basic text extraction to minimize memory usage.
    
    Args:
        word_file: Path to the input Word file (.docx, .doc)
        output_path: Output file path for PDF
    
    Returns:
        str: Path to the converted PDF file
    """
    try:
        from docx import Document
        
        print("⚡ Using lightweight Word to PDF conversion")
        
        # Read the Word document
        doc = Document(word_file)
        
        # Create simple text file first (memory efficient)
        text_content = []
        text_content.append("Converted Word Document")
        text_content.append("=" * 40)
        text_content.append("")
        
        # Extract text only (no heavy formatting)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text.strip())
        
        # Extract table data (simple)
        for table in doc.tables:
            text_content.append("\nTable Data:")
            for row in table.rows:
                row_text = " | ".join([cell.text.strip() for cell in row.cells])
                if row_text.strip():
                    text_content.append(row_text)
        
        # Create simple PDF with minimal dependencies
        try:
            # Try reportlab if available (lightweight usage)
            from reportlab.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            pdf_doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            for line in text_content:
                if line.startswith("="):
                    continue  # Skip separator lines
                p = Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), styles['Normal'])
                story.append(p)
            
            pdf_doc.build(story)
            print("✅ Word to PDF conversion completed (lightweight mode)")
            return output_path
            
        except ImportError:
            # Fallback: create text file if no PDF library
            txt_output = output_path.replace('.pdf', '.txt')
            with open(txt_output, 'w', encoding='utf-8') as f:
                f.write('\n'.join(text_content))
            print("✅ Word to text conversion completed (fallback mode)")
            return txt_output
        
    except ImportError as e:
        raise Exception(f"Word conversion requires python-docx package: {e}")
    except Exception as e:
        raise Exception(f"Error converting Word document: {e}")
