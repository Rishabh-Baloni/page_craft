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
    Convert Word document to PDF using LibreOffice CLI (best quality preservation).
    Falls back to pypandoc, then basic python-docx if LibreOffice is unavailable.
    
    Args:
        word_file: Path to the input Word file (.docx, .doc)
        output_path: Output file path for PDF
    
    Returns:
        str: Path to the converted PDF file
    """
    import subprocess
    import shutil
    
    # Method 1: LibreOffice CLI (Best option - preserves all formatting, images, tables)
    try:
        # Check if LibreOffice is available
        libreoffice_cmd = None
        for cmd in ['libreoffice', 'libreoffice7.0', 'libreoffice6.4', 'soffice']:
            if shutil.which(cmd):
                libreoffice_cmd = cmd
                break
        
        if libreoffice_cmd:
            # Get output directory and filename
            output_dir = os.path.dirname(os.path.abspath(output_path))
            output_name = os.path.splitext(os.path.basename(output_path))[0]
            
            # LibreOffice command for headless conversion
            cmd = [
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                word_file
            ]
            
            # Run LibreOffice conversion
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # LibreOffice creates PDF with same name as input file
            input_name = os.path.splitext(os.path.basename(word_file))[0]
            generated_pdf = os.path.join(output_dir, f"{input_name}.pdf")
            
            if result.returncode == 0 and os.path.exists(generated_pdf):
                # Rename to desired output name if different
                if generated_pdf != output_path:
                    shutil.move(generated_pdf, output_path)
                print("✅ Word to PDF conversion completed using LibreOffice")
                return output_path
            else:
                print(f"LibreOffice conversion failed: {result.stderr}")
                
    except Exception as e:
        print(f"LibreOffice conversion failed: {e}")
    
    # Method 2: pypandoc (Good fallback with LaTeX)
    try:
        import pypandoc
        
        # Convert using pandoc
        pypandoc.convert_file(
            word_file, 
            'pdf', 
            outputfile=output_path,
            extra_args=['--pdf-engine=pdflatex']
        )
        
        if os.path.exists(output_path):
            print("✅ Word to PDF conversion completed using pypandoc")
            return output_path
            
    except ImportError:
        print("pypandoc not available, trying basic conversion...")
    except Exception as e:
        print(f"pypandoc conversion failed: {e}")
    
    # Method 3: Basic python-docx + reportlab fallback (text only)
    try:
        from docx import Document
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        print("⚠️ Using basic text conversion (formatting may be lost)")
        
        # Read the Word document
        doc = Document(word_file)
        
        # Create PDF
        pdf_doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Add document title
        title = Paragraph("Converted Document", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Process paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                # Basic formatting detection
                style = styles['Normal']
                text = paragraph.text
                
                if paragraph.style.name.startswith('Heading'):
                    style = styles['Heading1'] if '1' in paragraph.style.name else styles['Heading2']
                
                p = Paragraph(text, style)
                story.append(p)
                story.append(Spacer(1, 6))
        
        # Process tables (basic)
        for table in doc.tables:
            story.append(Paragraph("Table Data:", styles['Heading3']))
            for row in table.rows:
                row_text = " | ".join([cell.text for cell in row.cells])
                if row_text.strip():
                    p = Paragraph(row_text, styles['Normal'])
                    story.append(p)
            story.append(Spacer(1, 12))
        
        pdf_doc.build(story)
        print("✅ Basic Word to PDF conversion completed")
        return output_path
        
    except ImportError as e:
        raise Exception(f"Word to PDF conversion requires additional packages: {e}")
    except Exception as e:
        raise Exception(f"Error converting Word document: {e}")
