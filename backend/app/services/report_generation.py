from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER


def generate_pdf_report(image_path1: str, image_path2: str, output_path: str = "report.pdf") -> str:
    """
    Generate a PDF safety compliance report with images and a title page.
    
    Args:
        image_path1: Path to the first image file
        image_path2: Path to the second image file
        output_path: Path where the PDF will be saved (default: "report.pdf")
        
    Returns:
        str: Path to the generated PDF file
        
    Raises:
        FileNotFoundError: If either image file does not exist
    """
    # Verify image files exist
    img1_path = Path(image_path1)
    img2_path = Path(image_path2)
    
    if not img1_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path1}")
    if not img2_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path2}")
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=0.75 * inch,
    )
    
    # Container for PDF elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor='#2c3e50',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor='#34495e',
        alignment=TA_CENTER,
        spaceAfter=30,
    )
    
    # Title Page
    elements.append(Spacer(1, 2 * inch))
    elements.append(Paragraph("Safety Compliance Report", title_style))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Add current date
    current_date = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Generated on: {current_date}", date_style))
    
    # Page break after title page
    elements.append(PageBreak())
    
    # Add images section
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12,
    )
    
    elements.append(Paragraph("Inspection Images", section_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Add first image
    try:
        img1 = Image(str(img1_path), width=5 * inch, height=4 * inch)
        elements.append(img1)
        elements.append(Spacer(1, 0.3 * inch))
    except Exception as e:
        elements.append(Paragraph(f"Error loading image 1: {str(e)}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
    
    # Add second image
    try:
        img2 = Image(str(img2_path), width=5 * inch, height=4 * inch)
        elements.append(img2)
        elements.append(Spacer(1, 0.3 * inch))
    except Exception as e:
        elements.append(Paragraph(f"Error loading image 2: {str(e)}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
    
    # Build PDF
    doc.build(elements)
    
    return output_path
