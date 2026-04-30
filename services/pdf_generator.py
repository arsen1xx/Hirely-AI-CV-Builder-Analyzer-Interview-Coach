from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

try:
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-Bold.ttf'))
    FONT_NAME = 'Inter'
    FONT_BOLD = 'Inter-Bold'
except Exception:
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

def generate_cv_pdf(cv_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=20*mm, 
        leftMargin=20*mm, 
        topMargin=20*mm, 
        bottomMargin=20*mm
    )
    story = []
    
    style_name = ParagraphStyle(
        'Name', fontName=FONT_BOLD, fontSize=28, leading=34, spaceAfter=2*mm, textColor=HexColor("#111111")
    )
    style_position = ParagraphStyle(
        'Position', fontName=FONT_NAME, fontSize=14, leading=18, textColor=HexColor("#555555"), spaceAfter=4*mm
    )
    style_contact = ParagraphStyle(
        'Contact', fontName=FONT_NAME, fontSize=10, leading=14, textColor=HexColor("#777777")
    )
    style_heading = ParagraphStyle(
        'Heading', fontName=FONT_BOLD, fontSize=14, leading=18, spaceBefore=8*mm, spaceAfter=3*mm, textColor=HexColor("#111111")
    )
    style_body = ParagraphStyle(
        'Body', fontName=FONT_NAME, fontSize=11, leading=16, textColor=HexColor("#333333")
    )
    style_bold_body = ParagraphStyle(
        'BoldBody', fontName=FONT_BOLD, fontSize=11, leading=16, textColor=HexColor("#111111")
    )
    style_dates = ParagraphStyle(
        'Dates', fontName=FONT_NAME, fontSize=10, leading=14, textColor=HexColor("#777777"), spaceAfter=2*mm
    )
    
    story.append(Paragraph(cv_data.get('full_name', 'Ім\'я Прізвище'), style_name))
    story.append(Paragraph(cv_data.get('position', 'Посада'), style_position))
    
    city = cv_data.get('city', '')
    phone = cv_data.get('phone', '')
    email = cv_data.get('email', '')
    contacts = " | ".join(filter(None, [city, phone, email]))
    story.append(Paragraph(contacts, style_contact))
    
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#E5E5E5"), spaceAfter=6*mm))
    
    raw_summary = cv_data.get('summary', '')
    clean_summary = raw_summary.split("Твій оригінальний текст:\n")[-1].strip()
    
    if clean_summary:
        story.append(Paragraph("Про себе", style_heading))
        story.append(Paragraph(clean_summary, style_body))
    
    if cv_data.get('experience'):
        story.append(Paragraph("Досвід роботи", style_heading))
        for exp in cv_data['experience']:
            if exp.get('title'):
                story.append(Paragraph(exp.get('title', ''), style_bold_body))
            if exp.get('dates'):
                story.append(Paragraph(exp.get('dates', ''), style_dates))
            if exp.get('description'):
                story.append(Paragraph(exp.get('description', ''), style_body))
            story.append(Spacer(1, 4*mm))

    if cv_data.get('education'):
        story.append(Paragraph("Освіта", style_heading))
        for edu in cv_data['education']:
            if edu.get('institution'):
                story.append(Paragraph(edu.get('institution', ''), style_bold_body))
            if edu.get('years'):
                story.append(Paragraph(edu.get('years', ''), style_dates))
            story.append(Spacer(1, 4*mm))

    if cv_data.get('skills'):
        story.append(Paragraph("Навички", style_heading))
        story.append(Paragraph(cv_data.get('skills', ''), style_body))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()