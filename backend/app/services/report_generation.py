from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors


def calculate_compliance_metrics(summary: Dict[str, Any], detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate detailed compliance metrics and risk assessment."""
    total_persons = summary.get("total_persons", 0)
    wearing_hardhat = summary.get("wearing_hardhat", 0)
    missing_hardhat = summary.get("missing_hardhat", 0)
    
    compliance_rate = (wearing_hardhat / total_persons * 100) if total_persons > 0 else 0
    
    # Assess risk level based on compliance
    if compliance_rate == 100:
        risk_level = "LOW"
        risk_color = colors.HexColor("#27ae60")  # Green
    elif compliance_rate >= 90:
        risk_level = "LOW-MEDIUM"
        risk_color = colors.HexColor("#f39c12")  # Orange
    elif compliance_rate >= 75:
        risk_level = "MEDIUM"
        risk_color = colors.HexColor("#e74c3c")  # Red
    else:
        risk_level = "HIGH"
        risk_color = colors.HexColor("#c0392b")  # Dark Red
    
    return {
        "total_persons": total_persons,
        "wearing_hardhat": wearing_hardhat,
        "missing_hardhat": missing_hardhat,
        "compliance_rate": round(compliance_rate, 1),
        "risk_level": risk_level,
        "risk_color": risk_color,
        "avg_confidence": summary.get("average_confidence", 0)
    }


def generate_pdf_report(
    image_path1: str, 
    image_path2: str, 
    output_path: str = "report.pdf",
    summary: Dict[str, Any] | None = None,
    detections: List[Dict[str, Any]] | None = None
) -> str:
    """
    Generate a comprehensive PDF safety compliance report with industry-standard metrics.
    
    Args:
        image_path1: Path to the original image file
        image_path2: Path to the annotated image file
        output_path: Path where the PDF will be saved (default: "report.pdf")
        summary: Summary statistics from detection (e.g., total_persons, wearing_hardhat, etc.)
        detections: List of detection objects with class_name, confidence, and bbox
        
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
    
    # Provide defaults if summary/detections are None
    if summary is None:
        summary = {
            "total_persons": 0,
            "wearing_hardhat": 0,
            "missing_hardhat": 0,
            "average_confidence": 0
        }
    if detections is None:
        detections = []
    
    # Calculate compliance metrics
    metrics = calculate_compliance_metrics(summary, detections)
    
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
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor='#2c3e50',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor='#34495e',
        alignment=TA_CENTER,
        spaceAfter=24,
        fontName='Helvetica',
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor("#34495e"),
        borderWidth=1,
        borderPadding=6,
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    
    # ===== TITLE PAGE =====
    elements.append(Spacer(1, 1.5 * inch))
    elements.append(Paragraph("SAFETY COMPLIANCE REPORT", title_style))
    elements.append(Paragraph("PPE Detection & Inspection Analysis", subtitle_style))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Add current date and unique ID
    current_date = datetime.now().strftime("%B %d, %Y at %H:%M")
    elements.append(Paragraph(f"<b>Report Generated:</b> {current_date}", body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Executive Summary Box
    exec_summary_data = [
        ["COMPLIANCE STATUS", f"{metrics['compliance_rate']}%"],
        ["RISK LEVEL", metrics['risk_level']],
        ["PERSONS INSPECTED", str(metrics['total_persons'])],
        ["HARDHAT COMPLIANCE", f"{metrics['wearing_hardhat']} / {metrics['total_persons']}"],
    ]
    
    exec_table = Table(exec_summary_data, colWidths=[3 * inch, 2.5 * inch])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, -1), colors.HexColor("#ecf0f1")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#2c3e50")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
    ]))
    
    elements.append(exec_table)
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(PageBreak())
    
    # ===== FINDINGS SECTION =====
    elements.append(Paragraph("INSPECTION FINDINGS", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Overview paragraph
    overview_text = f"""
    This safety inspection identified <b>{metrics['total_persons']} personnel</b> in the captured image(s).
    Of these, <b>{metrics['wearing_hardhat']} individuals ({metrics['compliance_rate']}%)</b> were properly wearing hardhats,
    while <b>{metrics['missing_hardhat']} individuals ({100 - metrics['compliance_rate']}%)</b> were not compliant with PPE requirements.
    The current <b>risk assessment is {metrics['risk_level']}</b> based on observed compliance rates.
    """
    
    elements.append(Paragraph(overview_text, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # ===== DETAILED VIOLATIONS =====
    if metrics['missing_hardhat'] > 0:
        elements.append(Paragraph("Identified Non-Compliance Instances", ParagraphStyle(
            'SubSectionTitle',
            parent=styles['Heading3'],
            fontSize=11,
            textColor='#c0392b',
            spaceAfter=8,
            fontName='Helvetica-Bold',
        )))
        
        # Count violations by class
        violation_count = sum(1 for d in detections if d["class_name"] == "NO-Hardhat")
        elements.append(Paragraph(
            f"<b>Total Non-Compliance Detections:</b> {violation_count}",
            body_style
        ))
        elements.append(Spacer(1, 0.15 * inch))
        
        # Create violations table if there are detections
        if detections:
            no_hardhat_detections = [d for d in detections if d["class_name"] == "NO-Hardhat"]
            
            if no_hardhat_detections:
                violation_data = [["Detection #", "Confidence Score", "Severity"]]
                
                for idx, detection in enumerate(no_hardhat_detections[:10], 1):  # Show top 10
                    confidence = detection.get("confidence", 0)
                    confidence_pct = round(confidence * 100, 1)
                    
                    # Assign severity based on confidence
                    if confidence >= 0.8:
                        severity = "HIGH"
                    elif confidence >= 0.6:
                        severity = "MEDIUM"
                    else:
                        severity = "LOW"
                    
                    violation_data.append([
                        str(idx),
                        f"{confidence_pct}%",
                        severity
                    ])
                
                violation_table = Table(violation_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch])
                violation_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e74c3c")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#fadbd8")]),
                ]))
                
                elements.append(violation_table)
                elements.append(Spacer(1, 0.3 * inch))
    else:
        elements.append(Paragraph(
            "<b style='color:#27ae60;'>✓ No violations detected. All personnel are in compliance.</b>",
            body_style
        ))
        elements.append(Spacer(1, 0.3 * inch))
    
    # ===== RISK ASSESSMENT =====
    elements.append(Paragraph("RISK ASSESSMENT", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    risk_text = f"""
    <b>Risk Level: {metrics['risk_level']}</b><br/>
    Based on the current compliance rate of {metrics['compliance_rate']}%, the site presents a <b>{metrics['risk_level']}</b> risk
    for PPE-related incidents. """
    
    if metrics['compliance_rate'] == 100:
        risk_text += "All personnel are properly equipped with hardhats. Continue current safety protocols."
    elif metrics['compliance_rate'] >= 90:
        risk_text += f"While most personnel are compliant, {metrics['missing_hardhat']} instances of non-compliance were identified. Immediate corrective action is recommended."
    elif metrics['compliance_rate'] >= 75:
        risk_text += f"Multiple instances of non-compliance ({metrics['missing_hardhat']} identified) represent a significant safety hazard. Urgent corrective measures are required."
    else:
        risk_text += f"A substantial portion of personnel ({metrics['missing_hardhat']} out of {metrics['total_persons']}) are not wearing hardhats. This represents an unacceptable safety risk. Immediate intervention is mandatory."
    
    elements.append(Paragraph(risk_text, body_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # ===== RECOMMENDATIONS =====
    elements.append(Paragraph("CORRECTIVE ACTIONS & RECOMMENDATIONS", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    recommendations = []
    
    if metrics['compliance_rate'] < 100:
        recommendations.append(
            "<b>1. Immediate Actions:</b><br/>"
            "   • Stop work and implement mandatory PPE requirements immediately<br/>"
            "   • Conduct on-site safety briefing with all personnel<br/>"
            "   • Verify proper hardhat fit and adjustment<br/>"
            "   • Document all non-compliant individuals for training records"
        )
    
    recommendations.extend([
        "<b>2. Short-Term (Within 24 hours):</b><br/>"
        "   • Conduct mandatory safety training covering PPE requirements<br/>"
        "   • Perform follow-up inspection to verify compliance<br/>"
        "   • Issue corrective action forms to supervisory staff",
        
        "<b>3. Long-Term (Ongoing):</b><br/>"
        "   • Implement regular safety audits and inspections<br/>"
        "   • Establish incentive programs for perfect compliance records<br/>"
        "   • Maintain inspection records for regulatory compliance<br/>"
        "   • Schedule refresher training quarterly"
    ])
    
    for rec in recommendations:
        elements.append(Paragraph(rec, body_style))
        elements.append(Spacer(1, 0.15 * inch))
    
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())
    
    # ===== INSPECTION IMAGES PAGE =====
    elements.append(Paragraph("ANNOTATED INSPECTION IMAGES", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    elements.append(Paragraph("<b>Original Image:</b>", ParagraphStyle(
        'ImageLabel',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        spaceAfter=6,
    )))
    
    # Add first image
    try:
        img1 = Image(str(img1_path), width=5.5 * inch, height=4.125 * inch)
        elements.append(img1)
    except Exception as e:
        elements.append(Paragraph(f"Error loading original image: {str(e)}", body_style))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    elements.append(Paragraph("<b>Annotated Image (with detections):</b>", ParagraphStyle(
        'ImageLabel',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        spaceAfter=6,
    )))
    
    # Add second image
    try:
        img2 = Image(str(img2_path), width=5.5 * inch, height=4.125 * inch)
        elements.append(img2)
    except Exception as e:
        elements.append(Paragraph(f"Error loading annotated image: {str(e)}", body_style))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # ===== FOOTER PAGE =====
    elements.append(PageBreak())
    elements.append(Paragraph("REPORT SUMMARY & SIGN-OFF", section_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Summary statistics
    summary_text = f"""
    <b>Inspection Summary:</b><br/>
    • Date: {current_date}<br/>
    • Total Personnel Inspected: {metrics['total_persons']}<br/>
    • Compliant Personnel: {metrics['wearing_hardhat']}<br/>
    • Non-Compliant Personnel: {metrics['missing_hardhat']}<br/>
    • Overall Compliance Rate: {metrics['compliance_rate']}%<br/>
    • Detection Confidence: {metrics['avg_confidence']}%<br/>
    • Risk Assessment: {metrics['risk_level']}<br/>
    """
    
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.4 * inch))
    
    # Signature block
    signature_text = """
    <b>Inspector Information:</b><br/>
    Name (Print): ________________________     Date: ________________________<br/>
    Signature: ____________________________     Title: ________________________<br/>
    <br/>
    <b>Site Supervisor Sign-Off:</b><br/>
    Name (Print): ________________________     Date: ________________________<br/>
    Signature: ____________________________     Title: ________________________<br/>
    """
    
    elements.append(Paragraph(signature_text, ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        leading=14,
    )))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Disclaimer
    disclaimer = """
    <i>This report is generated using automated vision-based detection and should be reviewed by qualified safety personnel.
    While the detection system aims for high accuracy, it is not infallible and should not be the sole basis for safety decisions.
    All findings should be verified through manual inspection and professional judgment. This report is for internal safety documentation only.</i>
    """
    
    elements.append(Paragraph(disclaimer, ParagraphStyle(
        'DisclaimerStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor='#7f8c8d',
        alignment=TA_JUSTIFY,
    )))
    
    # Build PDF
    doc.build(elements)
    
    return output_path
