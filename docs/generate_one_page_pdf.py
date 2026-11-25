import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Colors
NAVY_PRIMARY = colors.HexColor("#0f172a")
BLUE_ACCENT  = colors.HexColor("#0284c7")
BLUE_LIGHT   = colors.HexColor("#e0f2fe")
SLATE_DARK   = colors.HexColor("#1e293b")
SLATE_MUTED  = colors.HexColor("#64748b")
BG_CARD      = colors.HexColor("#f8fafc")
BORDER_LIGHT = colors.HexColor("#cbd5e1")
WHITE        = colors.HexColor("#ffffff")
TAG_BG       = colors.HexColor("#eff6ff")
TAG_TEXT     = colors.HexColor("#1d4ed8")

class SinglePageCanvas(canvas.Canvas):
    """Enforces header/footer drawing and tracks page count"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            # Draw top accent bar
            self.setFillColor(BLUE_ACCENT)
            self.rect(0, 836, 595.27, 6, fill=1, stroke=0)
            
            # Draw bottom footer line
            self.setStrokeColor(BORDER_LIGHT)
            self.setLineWidth(0.5)
            self.line(25, 25, 570, 25)
            
            # Footer text
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(SLATE_MUTED)
            self.drawString(25, 16, "Verification: Tested locally on http://localhost:5000/academiapro • 25 Normalized Tables (BCNF)")
            self.drawRightString(570, 16, "Student Signature: _______________________")
            
            super().showPage()
        super().save()

def generate_pdf(output_path):
    # Setup document with tight margins to fit exactly 1 page
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=22,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    
    # Custom typography
    styles.add(ParagraphStyle(
        'MainTitle',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=17,
        textColor=NAVY_PRIMARY
    ))
    styles.add(ParagraphStyle(
        'Subtitle',
        fontName='Helvetica',
        fontSize=8.5,
        leading=10.5,
        textColor=SLATE_MUTED
    ))
    styles.add(ParagraphStyle(
        'BadgeText',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=SLATE_DARK,
        alignment=2 # Right align
    ))
    styles.add(ParagraphStyle(
        'SectionHeading',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=BLUE_ACCENT,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        'ExecSummary',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10,
        textColor=SLATE_DARK
    ))
    styles.add(ParagraphStyle(
        'StatNum',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=14,
        textColor=BLUE_ACCENT,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'StatLabel',
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=8,
        textColor=SLATE_MUTED,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'CardTitle',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=9.5,
        textColor=NAVY_PRIMARY
    ))
    styles.add(ParagraphStyle(
        'CardBody',
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=SLATE_DARK
    ))
    styles.add(ParagraphStyle(
        'TableBodyBold',
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        textColor=SLATE_DARK
    ))
    styles.add(ParagraphStyle(
        'TableBody',
        fontName='Helvetica',
        fontSize=7.2,
        leading=9,
        textColor=SLATE_DARK
    ))

    story = []

    # 1. Header (Title + Metadata)
    header_data = [
        [
            Paragraph("<b>AcademiaPro: College Management ERP</b>", styles['MainTitle']),
            Paragraph("<b>Student:</b> Sana Hameed<br/><b>Evaluation:</b> Progress Review & Viva", styles['BadgeText'])
        ],
        [
            Paragraph("Academic Relational DBMS Design, BCNF Implementation & Progress Report", styles['Subtitle']),
            Paragraph("<b>Date:</b> November 2026 | <b>Course:</b> DBMS", styles['BadgeText'])
        ]
    ]
    t_header = Table(header_data, colWidths=[360, 187])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceAfter=5, spaceBefore=1))

    # 2. Key Metrics Bar (4 Stats)
    stat_w = 547 / 4.0
    stats_data = [
        [
            Paragraph("6", styles['StatNum']),
            Paragraph("25 (BCNF)", styles['StatNum']),
            Paragraph("Dual-Engine", styles['StatNum']),
            Paragraph("Multi-Tier", styles['StatNum'])
        ],
        [
            Paragraph("RELATIONAL SCHEMAS", styles['StatLabel']),
            Paragraph("NORMALIZED TABLES", styles['StatLabel']),
            Paragraph("POSTGRESQL & SQLITE3", styles['StatLabel']),
            Paragraph("RBAC & AI SHIELD", styles['StatLabel'])
        ]
    ]
    t_stats = Table(stats_data, colWidths=[stat_w]*4)
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 5))

    # 3. Executive Summary Card
    exec_text = (
        "<b>Executive Summary:</b> AcademiaPro is an enterprise-grade academic ERP and DBMS engineered strictly under "
        "relational theory, functional dependency mathematics, and BCNF normalization. It eliminates ad-hoc spreadsheets "
        "by unifying student lifecycle, grading, tuition invoicing, library circulation, lab inventory, and a secure AI query sandbox "
        "into an ACID-compliant relational system."
    )
    t_exec = Table([[Paragraph(exec_text, styles['ExecSummary'])]], colWidths=[547])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_exec)
    story.append(Spacer(1, 5))

    # 4. Two-Column Body: Left (Developments) & Right (Learnings & Stack)
    col_w = (547 - 12) / 2.0  # ~267.5 pt each

    # --- LEFT COLUMN (Developments) ---
    left_flowables = [
        Paragraph("KEY DEVELOPMENTS & DELIVERABLES", styles['SectionHeading']),
        HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT, spaceAfter=4, spaceBefore=1),
        
        # Dev 1
        Paragraph("<b>1. 6 Logical Relational Schemas (BCNF Certified)</b>", styles['CardTitle']),
        Paragraph(
            "• <b>system_core:</b> RBAC roles, user auth, immutable forensic audit log.<br/>"
            "• <b>academics:</b> Departments, programs, semesters, faculty, courses, sections, enrollments, attendance, decoupled assessments & marks.<br/>"
            "• <b>finance:</b> Fee tariff matrices, automated invoices, payment ledgers.<br/>"
            "• <b>library:</b> Physical barcode copies, circulation, overdue fine trigger.<br/>"
            "• <b>inventory:</b> Lab rooms, procurement items, purchase orders & issuance.<br/>"
            "• <b>ai:</b> Read-only query sessions, query telemetry, Roman Urdu intent logs.",
            styles['CardBody']
        ),
        Spacer(1, 4),

        # Dev 2
        Paragraph("<b>2. Full-Stack Web Portal & Multi-Role ERP</b>", styles['CardTitle']),
        Paragraph(
            "Engineered responsive UI (Flask + Bootstrap 5) providing role-based portals for Admin, Faculty, Student, and Accountant. Features real-time client-side search, batch enrollment, transcript generation, and tuition ledger reconciliation.",
            styles['CardBody']
        ),
        Spacer(1, 4),

        # Dev 3
        Paragraph("<b>3. Cyber Threat Defense & Security Shield</b>", styles['CardTitle']),
        Paragraph(
            "Integrated sliding-window IP rate limiting (120 req/min), dynamic anti-bot math CAPTCHA, automated IP auto-ban after 5 failed attempts, brute-force account lockout, and real-time administrator threat notification polling.",
            styles['CardBody']
        ),
        Spacer(1, 4),

        # Dev 4
        Paragraph("<b>4. Sandboxed Read-Only AI Assistant</b>", styles['CardTitle']),
        Paragraph(
            "Natural language & Roman Urdu classifier (detects queries like <i>'suspicious activity alerts'</i>, <i>'fee defaulters'</i>, <i>'attendance shortage'</i>). Sandboxed via dedicated view-only permissions, eliminating SQL injection vulnerability.",
            styles['CardBody']
        ),
    ]

    # --- RIGHT COLUMN (Learnings & Tech Stack) ---
    table_stack_data = [
        [Paragraph("Backend:", styles['TableBodyBold']), Paragraph("Python 3 (Flask), psycopg2, sqlite3 driver", styles['TableBody'])],
        [Paragraph("Database:", styles['TableBodyBold']), Paragraph("PostgreSQL 16+ & SQLite3 (Dual-Engine)", styles['TableBody'])],
        [Paragraph("Frontend:", styles['TableBodyBold']), Paragraph("HTML5, Custom CSS3 Tokens, Bootstrap 5", styles['TableBody'])],
        [Paragraph("Security:", styles['TableBodyBold']), Paragraph("RBAC, Forensic Logs, Sliding-Window Shield", styles['TableBody'])],
        [Paragraph("Current Status:", styles['TableBodyBold']), Paragraph("<b>ERP Active • Chatbot Ready • 100% Tested</b>", styles['TableBody'])],
    ]
    t_stack = Table(table_stack_data, colWidths=[70, col_w - 70])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))

    right_flowables = [
        Paragraph("KEY ACADEMIC LEARNINGS (DBMS THEORY)", styles['SectionHeading']),
        HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT, spaceAfter=4, spaceBefore=1),

        # Learning 1
        Paragraph("<b>• Normalization & Elimination of Anomalies:</b>", styles['CardTitle']),
        Paragraph(
            "Decomposed data from UNF to 1NF (atomic attributes), 2NF (eliminated composite partial dependencies), 3NF (eliminated transitive chains), and certified BCNF (every determinant is a candidate key). Successfully prevented Insertion, Deletion, and Update anomalies.",
            styles['CardBody']
        ),
        Spacer(1, 3.5),

        # Learning 2
        Paragraph("<b>• ACID Transactions & Row-Level Locking:</b>", styles['CardTitle']),
        Paragraph(
            "Gained mastery over concurrency control using <code>SELECT ... FOR UPDATE</code> to eliminate race conditions during high-volume course enrollments. Automated fines via transactional triggers.",
            styles['CardBody']
        ),
        Spacer(1, 3.5),

        # Learning 3
        Paragraph("<b>• Analytical Relational Views & Joins:</b>", styles['CardTitle']),
        Paragraph(
            "Engineered complex views (<code>v_student_transcript</code>, <code>v_defaulters</code>, <code>v_attendance_shortage</code>) using multi-table equi-joins, aggregations, and Cartesian product safeguards.",
            styles['CardBody']
        ),
        Spacer(1, 5),

        Paragraph("TECHNOLOGY STACK & STATUS", styles['SectionHeading']),
        HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT, spaceAfter=3, spaceBefore=1),
        t_stack,
        Spacer(1, 4),

        Paragraph("LINKEDIN & ACADEMIC OUTREACH", styles['SectionHeading']),
        HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT, spaceAfter=2, spaceBefore=1),
        Paragraph(
            "Prepared 5 professional engineering posters (Full-Stack Architecture, BCNF Theory, ACID Concurrency, AI Shield, and SaaS Dashboard) with technical write-ups ready for immediate release.",
            styles['CardBody']
        )
    ]

    # Combine into 2-column table
    two_col_table = Table([[left_flowables, right_flowables]], colWidths=[col_w, col_w])
    two_col_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('RIGHTPADDING', (0,0), (0,0), 6),
        ('LEFTPADDING', (1,0), (1,0), 6),
        ('RIGHTPADDING', (1,0), (1,0), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(two_col_table)

    # Build document using SinglePageCanvas
    doc.build(story, canvasmaker=SinglePageCanvas)
    print(f"SUCCESS: Generated PDF at {output_path}")

if __name__ == "__main__":
    out_pdf = sys.argv[1] if len(sys.argv) > 1 else "AcademiaPro_OnePage_Progress_Report.pdf"
    generate_pdf(out_pdf)
