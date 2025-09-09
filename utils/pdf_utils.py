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
    Convert Word document to PDF preserving formatting using Linux-compatible libraries.
    
    Args:
        word_file: Path to the input Word file (.docx, .doc)
        output_path: Output file path for PDF
    
    Returns:
        str: Path to the converted PDF file
    """
    try:
        from docx import Document
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
        
        # Read the Word document
        doc = Document(word_file)
        
        # Create PDF with better margins
        pdf_doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Create custom styles for different formatting
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.black,
            alignment=TA_LEFT,
            leftIndent=0,
            rightIndent=0
        )
        
        # Process paragraphs with formatting
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                # Detect paragraph style
                para_style = normal_style
                
                # Check for heading styles
                if paragraph.style.name.startswith('Heading'):
                    if '1' in paragraph.style.name:
                        para_style = title_style
                    else:
                        para_style = heading_style
                
                # Process runs to preserve bold/italic
                formatted_text = ""
                for run in paragraph.runs:
                    text = run.text
                    if text:
                        # Apply formatting tags
                        if run.bold and run.italic:
                            text = f"<b><i>{text}</i></b>"
                        elif run.bold:
                            text = f"<b>{text}</b>"
                        elif run.italic:
                            text = f"<i>{text}</i>"
                        elif run.underline:
                            text = f"<u>{text}</u>"
                        
                        formatted_text += text
                
                if formatted_text.strip():
                    # Handle different alignments
                    if paragraph.alignment == 1:  # Center
                        para_style.alignment = TA_CENTER
                    elif paragraph.alignment == 2:  # Right
                        para_style.alignment = TA_RIGHT
                    elif paragraph.alignment == 3:  # Justify
                        para_style.alignment = TA_JUSTIFY
                    else:
                        para_style.alignment = TA_LEFT
                    
                    p = Paragraph(formatted_text, para_style)
                    story.append(p)
                    story.append(Spacer(1, 6))
        
        # Process tables
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    # Get cell text with basic formatting
                    cell_text = ""
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            text = run.text
                            if text:
                                if run.bold:
                                    text = f"<b>{text}</b>"
                                elif run.italic:
                                    text = f"<i>{text}</i>"
                                cell_text += text
                    row_data.append(cell_text or " ")
                table_data.append(row_data)
            
            if table_data:
                # Create table with styling
                pdf_table = Table(table_data)
                pdf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(pdf_table)
                story.append(Spacer(1, 12))
        
        # Build the PDF
        pdf_doc.build(story)
        return output_path
        
    except ImportError as e:
        raise Exception(f"Word to PDF conversion requires python-docx and reportlab packages: {e}")
    except Exception as e:
        raise Exception(f"Error converting Word document: {e}")
