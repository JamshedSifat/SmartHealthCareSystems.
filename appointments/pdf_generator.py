from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings


def generate_prescription_pdf(prescription):
    """Generate PDF for a prescription"""
    
    # Create a BytesIO object
    buffer = BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.75*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leading=14
    )
    
    # ===== Header Section =====
    header_data = []
    
    # Add doctor image if exists
    if prescription.doctor.image:
        doctor_image_path = prescription.doctor.image.path
        if os.path.exists(doctor_image_path):
            img = Image(doctor_image_path, width=1*inch, height=1*inch)
            header_data.append([img])
    
    # Add doctor info
    doctor_info = f"""
    {prescription.doctor.name}<br/>
    <b>Specialty:</b> {prescription.doctor.specialty}<br/>
    <b>Experience:</b> {prescription.doctor.experience_years} years<br/>
    <b>Qualification:</b> {prescription.doctor.qualification or 'N/A'}<br/>
    <b>License:</b> {prescription.doctor.id}
    """
    
    if header_data:
        header_table = Table([header_data + [[Paragraph(doctor_info, normal_style)]]], colWidths=[1.5*inch, 4*inch])
    else:
        header_table = Table([[Paragraph(doctor_info, normal_style)]], colWidths=[5.5*inch])
    
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== Title =====
    elements.append(Paragraph("PRESCRIPTION", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== Patient & Appointment Info =====
    patient_data = [
        ['Patient Name:', prescription.patient.get_full_name() or prescription.patient.username],
        ['Patient Email:', prescription.patient.email],
        ['Appointment Date:', prescription.appointment.appointment_date.strftime('%d-%m-%Y')],
        ['Prescription Date:', prescription.created_at.strftime('%d-%m-%Y %H:%M')],
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 3.5*inch])
    patient_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
    ]))
    
    elements.append(patient_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # ===== Diagnosis Section =====
    elements.append(Paragraph("DIAGNOSIS", heading_style))
    elements.append(Paragraph(prescription.diagnosis, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== Medicines Section =====
    elements.append(Paragraph("MEDICINES", heading_style))
    
    if prescription.medicines.exists():
        medicines_data = [['#', 'Medicine Name', 'Dosage', 'Frequency', 'Duration']]
        
        for idx, medicine in enumerate(prescription.medicines.all(), 1):
            medicines_data.append([
                str(idx),
                medicine.name,
                medicine.dosage,
                medicine.frequency,
                medicine.duration
            ])
        
        medicines_table = Table(medicines_data, colWidths=[0.4*inch, 1.8*inch, 1.2*inch, 1.3*inch, 1*inch])
        medicines_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(medicines_table)
    else:
        elements.append(Paragraph("No medicines prescribed", normal_style))
    
    elements.append(Spacer(1, 0.25*inch))
    
    # ===== Notes Section =====
    if prescription.notes:
        elements.append(Paragraph("NOTES & INSTRUCTIONS", heading_style))
        elements.append(Paragraph(prescription.notes, normal_style))
        elements.append(Spacer(1, 0.2*inch))
    
    # ===== Footer =====
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("_" * 60, footer_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(f"Dr. {prescription.doctor.name}", ParagraphStyle(
        'DoctorSign',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )))
    elements.append(Paragraph(f"Signature Date: {datetime.now().strftime('%d-%m-%Y')}", footer_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        f"This is a digital prescription. Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    
    # Return buffer
    buffer.seek(0)
    return buffer
