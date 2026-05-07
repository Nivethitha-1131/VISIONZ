#!/usr/bin/env python3
"""
Quick Project Report Generator for VISIONZ
Generates a professional PDF report with key project information
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

# Create PDF
pdf_path = 'VISIONZ_QUICK_REPORT.pdf'
doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch, 
                        leftMargin=0.75*inch, rightMargin=0.75*inch)

styles = getSampleStyleSheet()
story = []

# Define custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=28,
    textColor=colors.HexColor('#667eea'),
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=12,
    textColor=colors.HexColor('#555555'),
    spaceAfter=20,
    alignment=TA_CENTER
)

heading1_style = ParagraphStyle(
    'Heading1Custom',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#667eea'),
    spaceAfter=12,
    spaceBefore=12,
    borderColor=colors.HexColor('#667eea'),
    borderWidth=2,
    borderPadding=5
)

heading2_style = ParagraphStyle(
    'Heading2Custom',
    parent=styles['Heading2'],
    fontSize=13,
    textColor=colors.HexColor('#444444'),
    spaceAfter=10,
    spaceBefore=10
)

body_style = ParagraphStyle(
    'BodyCustom',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#333333'),
    alignment=TA_JUSTIFY,
    spaceAfter=8
)

# ============= TITLE PAGE =============
story.append(Paragraph('VISIONZ', title_style))
story.append(Paragraph('AI-Powered Video Quality Control System', subtitle_style))
story.append(Spacer(1, 0.3*inch))

# Project info box
info_data = [
    ['Project Name', 'VISIONZ'],
    ['Status', '✅ Production Ready'],
    ['Version', '3.0.0'],
    ['Generated', datetime.now().strftime('%B %d, %Y')],
]

info_table = Table(info_data, colWidths=[2*inch, 2.5*inch])
info_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
    ('BACKGROUND', (1, 0), (1, -1), colors.white),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
]))
story.append(info_table)
story.append(Spacer(1, 0.4*inch))

# ============= EXECUTIVE SUMMARY =============
story.append(Paragraph('EXECUTIVE SUMMARY', heading1_style))
story.append(Paragraph(
    'VISIONZ is an enterprise-grade AI-powered video quality control system designed for manufacturing environments. '
    'It automatically detects product defects in real-time using YOLOv8 object detection combined with Claude AI and Llama2 '
    'analysis. The system reduces inspection time from 2+ hours to 3 minutes per batch with 85%+ accuracy.',
    body_style
))
story.append(Spacer(1, 0.15*inch))

# Key metrics
metrics_data = [
    ['Metric', 'Value'],
    ['Detection Speed', '3-4 minutes per video'],
    ['Defect Classes', '17 specialized categories'],
    ['Detection Accuracy', '85-92%'],
    ['Concurrent Users', '100+ supported'],
    ['API Endpoints', '20+ available'],
    ['Security Level', 'Enterprise-grade'],
]

metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2.5*inch])
metrics_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
]))
story.append(metrics_table)
story.append(Spacer(1, 0.3*inch))

# ============= KEY FEATURES =============
story.append(Paragraph('KEY FEATURES', heading1_style))

features = [
    ('Detection & Analysis', [
        '17 Specialized Defect Classes (structural, surface, labeling, color, components)',
        'YOLOv8 real-time detection with >85% accuracy',
        'Intelligent frame resizing and adaptive processing',
        'Color-coded visualization (red=critical, orange=warning)',
        'Batch processing up to 10 videos simultaneously'
    ]),
    ('AI-Powered Intelligence', [
        'Claude Sonnet 4 for advanced quality insights',
        'Llama2 local model for offline analysis',
        'Automatic fallback between models',
        'Root cause analysis and actionable recommendations',
        'Quality verdicts and trend predictions'
    ]),
    ('Security & Performance', [
        'Bcrypt password hashing with 12-salt rounds',
        'JWT tokens with 30-minute session timeout',
        'Rate limiting (100 requests/minute)',
        'Security headers (CSP, HSTS, X-Frame-Options)',
        'Database transactions with ACID compliance'
    ]),
]

for feature_title, feature_list in features:
    story.append(Paragraph(feature_title, heading2_style))
    for feature in feature_list:
        story.append(Paragraph('• ' + feature, body_style))
    story.append(Spacer(1, 0.1*inch))

story.append(PageBreak())

# ============= TECHNOLOGY STACK =============
story.append(Paragraph('TECHNOLOGY STACK', heading1_style))

tech_data = [
    ['Component', 'Technology'],
    ['Language', 'Python 3.10+'],
    ['Framework', 'FastAPI 0.110.1'],
    ['Database', 'SQLite (scalable to PostgreSQL)'],
    ['Detection', 'YOLOv8 + PyTorch 2.9.0+'],
    ['Vision', 'OpenCV 4.8.0'],
    ['AI/LLM', 'Claude API + Ollama/Llama2'],
    ['Frontend', 'HTML5, CSS3, Vanilla JavaScript'],
    ['Frontend Host', 'Vercel'],
    ['Backend Host', 'Render'],
    ['Authentication', 'JWT + Bcrypt'],
]

tech_table = Table(tech_data, colWidths=[2.5*inch, 2.5*inch])
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
]))
story.append(tech_table)
story.append(Spacer(1, 0.2*inch))

# ============= SYSTEM ARCHITECTURE =============
story.append(Paragraph('SYSTEM ARCHITECTURE', heading1_style))
story.append(Paragraph(
    'VISIONZ follows a three-tier architecture with clear separation of concerns:',
    body_style
))
story.append(Spacer(1, 0.1*inch))

arch_data = [
    ['Layer', 'Components'],
    ['Frontend', 'Web Dashboard (Vercel) - Video upload, analytics, reporting'],
    ['API Backend', 'FastAPI server (Render) - Routes, authentication, processing'],
    ['AI/ML Services', 'YOLOv8 detection, Claude API, Llama2 analysis'],
    ['Data Storage', 'SQLite database - Users, sessions, detections, reports'],
]

arch_table = Table(arch_data, colWidths=[1.5*inch, 3.5*inch])
arch_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
]))
story.append(arch_table)
story.append(Spacer(1, 0.3*inch))

# ============= DEFECT DETECTION =============
story.append(Paragraph('DEFECT DETECTION CAPABILITIES', heading1_style))
story.append(Paragraph(
    'VISIONZ detects 17 different defect types organized into 5 categories, '
    'each classified by severity level:',
    body_style
))
story.append(Spacer(1, 0.1*inch))

defects_data = [
    ['Category', 'Defect Types', 'Severity'],
    ['Structural', 'Dent, Damage, Torn, Shape Deformation', 'Critical/Warning'],
    ['Surface', 'Scratch, Crack, Dent', 'Critical/Warning'],
    ['Labeling', 'Mislabeling, Barcode, Batch Number, Expiry', 'Critical'],
    ['Appearance', 'Color Fade, Color Deviation, Discoloration', 'Warning'],
    ['Components', 'Missing Component, Loose Component', 'Critical/Warning'],
]

defects_table = Table(defects_data, colWidths=[1.3*inch, 2.7*inch, 1*inch])
defects_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
]))
story.append(defects_table)
story.append(Spacer(1, 0.2*inch))

story.append(PageBreak())

# ============= DEPLOYMENT =============
story.append(Paragraph('DEPLOYMENT CONFIGURATION', heading1_style))

story.append(Paragraph('Frontend Deployment (Vercel)', heading2_style))
story.append(Paragraph(
    'The React-free frontend is deployed on Vercel with zero-configuration deployment. '
    'HTML, CSS, and vanilla JavaScript files are automatically optimized and distributed ' 
    'via Vercel\'s CDN for fast global access.',
    body_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph('Backend Deployment (Render)', heading2_style))
story.append(Paragraph(
    'The FastAPI backend runs on Render with Python 3.10 runtime. The service includes '
    'automatic deployments from Git, environment variable management, and horizontal scaling '
    'to handle up to 100+ concurrent users.',
    body_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph('Environment Variables', heading2_style))
env_vars = [
    'ENVIRONMENT=production',
    'SECRET_KEY=[auto-generated]',
    'CORS_ORIGINS=https://your-frontend.vercel.app',
    'CLAUDE_API_KEY=[your-api-key]',
    'DEBUG=false',
    'LOG_LEVEL=INFO',
]
for var in env_vars:
    story.append(Paragraph('• ' + var, body_style))
story.append(Spacer(1, 0.2*inch))

# ============= ANALYTICS & REPORTING =============
story.append(Paragraph('ANALYTICS & REPORTING', heading1_style))

analytics_features = [
    'Real-time Dashboard: Live defect statistics and system health',
    'Defect Breakdown: Category-wise, severity-wise, and time-based analysis',
    'Trend Analysis: Historical pattern recognition and predictive insights',
    'Export Capabilities: Download reports in multiple formats',
    'Performance Metrics: System uptime, processing speed, accuracy metrics',
]

for feature in analytics_features:
    story.append(Paragraph('• ' + feature, body_style))
story.append(Spacer(1, 0.2*inch))

# ============= SECURITY FEATURES =============
story.append(Paragraph('SECURITY FEATURES', heading1_style))

security_features = [
    'JWT Authentication: Secure token-based session management',
    'Bcrypt Hashing: 12-salt round password encryption',
    'Rate Limiting: 100 requests per minute per IP',
    'CORS Protection: Controlled cross-origin resource sharing',
    'Security Headers: CSP, HSTS, X-Frame-Options implementation',
    'Database Security: Transaction support, foreign key constraints, audit logging',
    'Role-Based Access: Admin, Manager, Operator permission levels',
]

for feature in security_features:
    story.append(Paragraph('• ' + feature, body_style))
story.append(Spacer(1, 0.3*inch))

# ============= PROJECT STRUCTURE =============
story.append(PageBreak())
story.append(Paragraph('PROJECT STRUCTURE', heading1_style))

story.append(Paragraph('Directory Organization', heading2_style))
story.append(Paragraph(
    'VISIONZ follows a modular, scalable architecture with clear separation between frontend and backend:',
    body_style
))
story.append(Spacer(1, 0.1*inch))

structure_items = [
    ('backend/', 'FastAPI application with routes, services, and models'),
    ('backend/app/routes/', 'API endpoints for auth, detections, analytics, reports'),
    ('backend/app/services/', 'Business logic: YOLOv8, Llama, Claude integration'),
    ('frontend/', 'HTML/CSS/JavaScript web interface'),
    ('frontend/js/', 'API client and UI interaction logic'),
    ('docs/', 'Project documentation and guides'),
]

for path, description in structure_items:
    story.append(Paragraph(f'<b>{path}</b> - {description}', body_style))
story.append(Spacer(1, 0.2*inch))

# ============= PERFORMANCE METRICS =============
story.append(Paragraph('PERFORMANCE METRICS', heading1_style))

perf_data = [
    ['Metric', 'Value', 'Target'],
    ['Video Processing Time', '3-4 minutes', '<5 minutes'],
    ['Detection Accuracy', '85-92%', '>85%'],
    ['API Response Time', '<500ms', '<1s'],
    ['Database Query Time', '<100ms', '<500ms'],
    ['Concurrent Users', '100+', '100+'],
    ['System Uptime', '99.5%', '>99%'],
]

perf_table = Table(perf_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
perf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
]))
story.append(perf_table)
story.append(Spacer(1, 0.3*inch))

# ============= GETTING STARTED =============
story.append(Paragraph('QUICK START GUIDE', heading1_style))

story.append(Paragraph('Prerequisites', heading2_style))
story.append(Paragraph('• Python 3.10 or higher', body_style))
story.append(Paragraph('• Node.js (for frontend development only)', body_style))
story.append(Paragraph('• YOLOv8 model weights (yolov8s.pt)', body_style))
story.append(Paragraph('• Claude API key (for advanced analysis)', body_style))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph('Installation Steps', heading2_style))
steps = [
    'Clone the VISIONZ repository',
    'Install dependencies: pip install -r backend/requirements.txt',
    'Configure environment variables in .env file',
    'Run database migrations: python backend/app/main.py --migrate',
    'Start the backend: python backend/run.py',
    'Open frontend in browser at http://localhost:3000',
]
for i, step in enumerate(steps, 1):
    story.append(Paragraph(f'{i}. {step}', body_style))
story.append(Spacer(1, 0.2*inch))

# ============= SUPPORT & DOCUMENTATION =============
story.append(Paragraph('DOCUMENTATION & SUPPORT', heading1_style))

resources = [
    ('API Documentation', 'FastAPI auto-generated docs at /docs endpoint'),
    ('Defect Classes', 'Detailed definitions in backend/DEFECT_CLASSES.md'),
    ('Deployment Guide', 'Step-by-step guide for Vercel and Render in docs/'),
    ('Tech Stack', 'Full technology details in docs/TECH_STACK.md'),
]

for title, description in resources:
    story.append(Paragraph(f'<b>{title}:</b> {description}', body_style))
story.append(Spacer(1, 0.3*inch))

# ============= FOOTER =============
story.append(Spacer(1, 0.2*inch))
footer_text = f"Report Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')} | VISIONZ v3.0.0"
story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                                     textColor=colors.HexColor('#999999'), alignment=TA_CENTER)))

# Build PDF
doc.build(story)
print(f"✅ PDF Report generated successfully: {pdf_path}")
print(f"📄 File size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
