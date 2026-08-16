from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os
import time


# ================= BORDER FUNCTION =================
def draw_border(canvas, doc):
    width, height = letter

    canvas.setStrokeColorRGB(0.55, 0.25, 0.85)  # purple
    canvas.setLineWidth(2)

    # border box
    canvas.rect(40, 40, width - 80, height - 80)


# ================= MAIN FUNCTION =================
def convert_word_to_pdf(input_path, output_folder):
    try:
        doc = Document(input_path)

        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(
            output_folder, f"converted_{int(time.time())}.pdf"
        )

        pdf = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=60,
            rightMargin=60,
            topMargin=60,
            bottomMargin=60
        )

        # ================= STYLES =================
        title_style = ParagraphStyle(
            name="Title",
            fontSize=22,
            leading=26,
            spaceAfter=20,
            alignment=1,  # center
            textColor=colors.black
        )

        heading_style = ParagraphStyle(
            name="Heading",
            fontSize=16,
            leading=20,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.black
        )

        body_style = ParagraphStyle(
            name="Body",
            fontSize=12,
            leading=16,
            spaceAfter=8,
            textColor=colors.black
        )

        bullet_style = ParagraphStyle(
            name="Bullet",
            fontSize=12,
            leading=16,
            leftIndent=15,
            spaceAfter=5
        )

        elements = []

        first_line = True

        # ================= CONTENT PROCESS =================
        for para in doc.paragraphs:
            text = para.text.strip()

            if not text:
                continue

            # TITLE (first line)
            if first_line:
                elements.append(Paragraph(text, title_style))
                first_line = False
                continue

            # HEADINGS
            if para.style.name.startswith("Heading"):
                elements.append(Paragraph(text, heading_style))

            # BULLETS
            elif text.startswith(("-", "*", "•")):
                clean_text = text.lstrip("-*• ").strip()
                elements.append(Paragraph(f"• {clean_text}", bullet_style))

            # NORMAL TEXT
            else:
                elements.append(Paragraph(text, body_style))

        # ================= BUILD PDF =================
        pdf.build(
            elements,
            onFirstPage=draw_border,
            onLaterPages=draw_border
        )

        return output_path

    except Exception as e:
        raise Exception(f"Word to PDF conversion failed: {str(e)}")