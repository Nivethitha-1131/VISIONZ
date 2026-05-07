from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import os

# Read markdown file
with open('VISIONZ_PROJECT_REPORT.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Create PDF
pdf_path = 'VISIONZ_PROJECT_REPORT.pdf'
doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)

styles = getSampleStyleSheet()
story = []

# Add title
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=22,
    textColor=colors.HexColor('#667eea'),
    spaceAfter=20,
    alignment=1
)

story.append(Paragraph('VISIONZ PROJECT REPORT', title_style))
story.append(Paragraph('AI-Powered FMCG Quality Control System', styles['Normal']))
story.append(Spacer(1, 0.2*inch))

# Parse markdown and create PDF content
lines = content.split('\n')
page_count = 0
for i, line in enumerate(lines):
    if line.startswith('# ') and i > 0:  # Skip first heading
        story.append(Paragraph(line[2:], styles['Heading1']))
        story.append(Spacer(1, 0.1*inch))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:], styles['Heading2']))
        story.append(Spacer(1, 0.08*inch))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:], styles['Heading3']))
        story.append(Spacer(1, 0.05*inch))
    elif line.startswith('```'):
        continue
    elif line.strip().startswith('- ') or line.strip().startswith('✅'):
        story.append(Paragraph('• ' + line.strip()[2:] if line.strip().startswith('- ') else line.strip(), styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
    elif line.strip() and not line.startswith('|') and not line.startswith('['):
        if len(line.strip()) > 3:
            story.append(Paragraph(line.strip(), styles['Normal']))
    
    # Add page break every ~80 lines
    page_count += 1
    if page_count % 80 == 0 and i > 100:
        story.append(PageBreak())

try:
    doc.build(story)
    size = os.path.getsize(pdf_path) / 1024
    print(f'✅ PDF created successfully!')
    print(f'📄 File: VISIONZ_PROJECT_REPORT.pdf')
    print(f'📊 Size: {size:.1f} KB')
    print(f'📍 Location: {os.path.abspath(pdf_path)}')
except Exception as e:
    print(f'⚠️ Error creating PDF: {e}')
    import traceback
    traceback.print_exc()
