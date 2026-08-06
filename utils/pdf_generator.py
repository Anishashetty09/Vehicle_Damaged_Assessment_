import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_pdf_report(report_data, output_path):
    """
    Generates a professional PDF Vehicle Inspection Report reflecting genuine binary classification.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2563EB'),
        alignment=TA_LEFT
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    # 1. Header & Title Block
    header_table_data = [
        [
            Paragraph("AI VEHICLE DAMAGE DETECTION REPORT", title_style),
            Paragraph("BINARY AI MODEL EVALUATION", subtitle_style)
        ]
    ]
    header_table = Table(header_table_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3B82F6'), spaceAfter=12))

    # 2. Status Banner (Damaged = Red, No Damage Detected = Green)
    prediction = report_data.get('prediction', 'No Damage Detected')
    is_damaged = prediction == 'Damaged'
    bg_color = colors.HexColor('#DC2626') if is_damaged else colors.HexColor('#16A34A')
    status_text = f"VEHICLE STATUS: {prediction.upper()}"

    status_table = Table(
        [[Paragraph(f"<b>{status_text}</b>", badge_style)]],
        colWidths=[540],
        rowHeights=[32]
    )
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 14))

    # 3. Metadata Grid
    meta_left = [
        [Paragraph("<b>Inspection ID:</b>", body_style), Paragraph(str(report_data.get('inspection_id', 'N/A')), body_style)],
        [Paragraph("<b>Inspector Name:</b>", body_style), Paragraph(str(report_data.get('inspector_name', 'N/A')), body_style)],
        [Paragraph("<b>Vehicle Number:</b>", body_style), Paragraph(str(report_data.get('vehicle_no', 'N/A')), body_style)],
        [Paragraph("<b>Policy Number:</b>", body_style), Paragraph(str(report_data.get('policy_no', 'N/A')), body_style)],
    ]

    meta_right = [
        [Paragraph("<b>AI Engine:</b>", body_style), Paragraph(str(report_data.get('framework', 'PyTorch 2.13')), body_style)],
        [Paragraph("<b>Inference Speed:</b>", body_style), Paragraph(f"{report_data.get('inference_time_ms', 0)} ms", body_style)],
        [Paragraph("<b>Classification:</b>", body_style), Paragraph(f"<b>{prediction}</b>", body_style)],
        [Paragraph("<b>Date & Time:</b>", body_style), Paragraph(str(report_data.get('date_time', 'N/A')), body_style)],
    ]

    meta_table_data = [
        [
            Table(meta_left, colWidths=[100, 160]),
            Table(meta_right, colWidths=[110, 150])
        ]
    ]

    meta_grid = Table(meta_table_data, colWidths=[270, 270])
    meta_grid.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(Paragraph("INSPECTION METADATA & EVALUATION SUMMARY", section_heading))
    story.append(meta_grid)
    story.append(Spacer(1, 14))

    # 4. Embedded Image Section
    image_path = report_data.get('image_path')
    if image_path and os.path.exists(image_path):
        story.append(Paragraph("CAPTURED VEHICLE IMAGE SNAPSHOT", section_heading))
        try:
            img = RLImage(image_path, width=280, height=200)
            img_table = Table([[img]], colWidths=[540])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
                ('PADDING', (0,0), (-1,-1), 8)
            ]))
            story.append(img_table)
            story.append(Spacer(1, 14))
        except Exception as e:
            print(f"[PDF GENERATOR] Warning embedding image: {e}")

    # 5. AI Summary & Inspector Remarks
    summary_text = report_data.get('summary') or (
        "The AI model detected visible signs that indicate the vehicle is damaged. This prediction is based on image analysis."
        if is_damaged else
        "The AI model did not detect visible damage in the uploaded image."
    )

    rec_box_data = [
        [Paragraph("<b>AI Prediction Summary:</b>", body_style)],
        [Paragraph(f"<i>{summary_text}</i>", body_style)],
        [Paragraph("<b>Inspector Remarks:</b>", body_style)],
        [Paragraph(f"{report_data.get('notes', 'No additional remarks provided.')}", body_style)]
    ]
    rec_table = Table(rec_box_data, colWidths=[540])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#93C5FD')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("MODEL SUMMARY & REMARKS", section_heading))
    story.append(rec_table)
    story.append(Spacer(1, 18))

    # 6. Signature Block
    sig_data = [
        [
            Paragraph("<b>PyTorch AI Binary Classification Engine</b>", body_style),
            Paragraph("<b>Authorized Signature:</b><br/><br/>___________________________", body_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[300, 240])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(sig_table)

    # Build PDF
    doc.build(story)
    print(f"[SUCCESS] PDF Inspection Report generated at: {output_path}")
    return output_path
