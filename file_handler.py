"""
Fayl formatlar bilan ishlash moduli
DOCX, PDF, TXT o'qish va yozish
"""

import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


def read_text_file(file_path):
    """TXT faylni o'qish"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Agar UTF-8 ishlamasa, boshqa kodlashlarni sinab ko'rish
        try:
            with open(file_path, 'r', encoding='cp1251') as f:
                return f.read()
        except:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()


def read_docx_file(file_path):
    """DOCX fayldan matnni o'qish"""
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"❌ DOCX faylni o'qishda xatolik: {str(e)}"


def read_pdf_file(file_path):
    """
    PDF fayldan matnni o'qish
    PyPDF2 yoki pdfplumber kerak, agar yo'q bo'lsa xabar beradi
    """
    try:
        # PyPDF2 bilan sinab ko'rish
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    full_text.append(text)
            return '\n'.join(full_text)
    except ImportError:
        return "❌ PDF o'qish uchun PyPDF2 kutubxonasi kerak:\n   pip install PyPDF2"
    except Exception as e:
        return f"❌ PDF faylni o'qishda xatolik: {str(e)}"


def save_as_text(file_path, input_text, output_text):
    """TXT faylga saqlash"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("===== KIRUVCHI MATN =====\n\n")
            f.write(input_text)
            f.write("\n\n===== NATIJAVIY MATN =====\n\n")
            f.write(output_text)
        return True, "✅ TXT fayl muvaffaqiyatli saqlandi"
    except Exception as e:
        return False, f"❌ Xatolik: {str(e)}"


def save_as_docx(file_path, input_text, output_text):
    """DOCX faylga saqlash"""
    try:
        doc = Document()
        
        # Sarlavha
        title = doc.add_heading('Matn Tahlili Natijasi', 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Kiruvchi matn
        doc.add_heading('Kiruvchi Matn', level=1)
        input_para = doc.add_paragraph(input_text)
        input_para.style.font.size = Pt(11)
        
        # Bo'sh qator
        doc.add_paragraph()
        
        # Natijaviy matn
        doc.add_heading('Natijaviy Matn', level=1)
        output_para = doc.add_paragraph(output_text)
        output_para.style.font.size = Pt(11)
        
        # Saqlash
        doc.save(file_path)
        return True, "✅ DOCX fayl muvaffaqiyatli saqlandi"
    except Exception as e:
        return False, f"❌ Xatolik: {str(e)}"


def save_as_pdf(file_path, input_text, output_text):
    """PDF faylga saqlash (reportlab yordamida)"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
        
        # PDF yaratish
        doc = SimpleDocTemplate(file_path, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        # Kontent uchun ro'yxat
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='darkblue',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Heading style
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='darkgreen',
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Normal text style
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.leading = 14
        
        # Sarlavha
        title = Paragraph("Matn Tahlili Natijasi", title_style)
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Kiruvchi matn
        heading1 = Paragraph("Kiruvchi Matn", heading_style)
        story.append(heading1)
        story.append(Spacer(1, 0.2*inch))
        
        # Matnni qismlarga bo'lish (uzun matnlar uchun)
        input_paragraphs = input_text.split('\n')
        for para in input_paragraphs:
            if para.strip():
                p = Paragraph(para, normal_style)
                story.append(p)
                story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Natijaviy matn
        heading2 = Paragraph("Natijaviy Matn", heading_style)
        story.append(heading2)
        story.append(Spacer(1, 0.2*inch))
        
        output_paragraphs = output_text.split('\n')
        for para in output_paragraphs:
            if para.strip():
                p = Paragraph(para, normal_style)
                story.append(p)
                story.append(Spacer(1, 0.1*inch))
        
        # PDF yaratish
        doc.build(story)
        
        return True, "✅ PDF fayl muvaffaqiyatli saqlandi"
        
    except ImportError:
        return False, "❌ PDF yaratish uchun reportlab kutubxonasi kerak:\n   pip install reportlab"
    except Exception as e:
        return False, f"❌ Xatolik: {str(e)}"


def get_file_extension(file_path):
    """Fayl kengaytmasini olish"""
    return os.path.splitext(file_path)[1].lower()


def read_file(file_path):
    """
    Universal fayl o'qish funksiyasi
    TXT, DOCX, PDF formatlarni qo'llab-quvvatlaydi
    """
    ext = get_file_extension(file_path)
    
    if ext == '.txt':
        return read_text_file(file_path)
    elif ext == '.docx':
        return read_docx_file(file_path)
    elif ext == '.pdf':
        return read_pdf_file(file_path)
    else:
        return f"❌ Qo'llab-quvvatlanmaydigan format: {ext}\nQo'llab-quvvatlanadigan formatlar: .txt, .docx, .pdf"


def save_file(file_path, input_text, output_text, format_type=None):
    """
    Universal fayl saqlash funksiyasi
    
    Args:
        file_path: Fayl yo'li
        input_text: Kiruvchi matn
        output_text: Natijaviy matn
        format_type: 'txt', 'docx', 'pdf' yoki None (avtomatik aniqlash)
    
    Returns:
        (success: bool, message: str)
    """
    if format_type is None:
        format_type = get_file_extension(file_path)[1:]  # .txt -> txt
    
    format_type = format_type.lower()
    
    if format_type == 'txt':
        return save_as_text(file_path, input_text, output_text)
    elif format_type == 'docx':
        return save_as_docx(file_path, input_text, output_text)
    elif format_type == 'pdf':
        return save_as_pdf(file_path, input_text, output_text)
    else:
        return False, f"❌ Qo'llab-quvvatlanmaydigan format: {format_type}"
