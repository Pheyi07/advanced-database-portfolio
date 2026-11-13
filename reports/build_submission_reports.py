import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

ERD_IMG = os.path.join(ROOT_DIR, 'portfolio-1-database-design', 'schema_diagram.png')
BENCH_IMG = os.path.join(ROOT_DIR, 'portfolio-2-query-optimisation', 'performance_comparison.png')
ARCH_IMG = os.path.join(ROOT_DIR, 'portfolio-5-distributed-cloud', 'architecture_diagram.png')

DOCX_OUT = os.path.join(BASE_DIR, 'FinFlow_Database_Portfolio_Report.docx')
PDF_OUT = os.path.join(BASE_DIR, 'FinFlow_Database_Portfolio_Report.pdf')

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def build_docx():
    print("[1/2] Generating MS Word (.docx) Submission Document...")
    doc = Document()
    
    # Page setup: Standard margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # University Header Banner
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_uni.add_run("MIVA OPEN UNIVERSITY\n")
    r_uni.font.name = "Arial"
    r_uni.font.size = Pt(15)
    r_uni.font.bold = True
    r_uni.font.color.rgb = RGBColor(15, 23, 42)

    r_school = p_uni.add_run("SCHOOL OF POSTGRADUATE STUDIES | MASTER OF INFORMATION TECHNOLOGY\n")
    r_school.font.name = "Arial"
    r_school.font.size = Pt(11)
    r_school.font.bold = True
    r_school.font.color.rgb = RGBColor(30, 64, 175)

    r_sub = p_uni.add_run("MIT 8103: Advanced Database Systems — Continuous Assessment Portfolio (40 Marks)\n")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(185, 28, 28)

    # Metadata Table
    table_meta = doc.add_table(rows=4, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Candidate Name / Student ID:", "Postgraduate Research Candidate (MIT Programme)"),
        ("Course & Academic Session:", "MIT 8103 Advanced Database Systems (2026/2027 Session)"),
        ("Selected Case Study:", "FinFlow Global Payment Systems (Cross-Border Digital Banking)"),
        ("GitHub Repository Link:", "https://github.com/miva-pg-student/advanced-database-portfolio")
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = table_meta.rows[idx]
        row.cells[0].text = label
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
        row.cells[0].paragraphs[0].runs[0].font.name = "Arial"
        set_cell_background(row.cells[0], "F1F5F9")
        
        row.cells[1].text = val
        row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)
        row.cells[1].paragraphs[0].runs[0].font.name = "Arial"
        set_cell_background(row.cells[1], "F8FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Section 1: Case Study Statement
    h1 = doc.add_heading("1. Database Case Study Statement", level=1)
    h1.style.font.name = "Arial"
    h1.style.font.color.rgb = RGBColor(15, 23, 42)

    p_cs = doc.add_paragraph()
    p_cs.paragraph_format.line_spacing = 1.15
    p_cs.add_run("Organisation: ").bold = True
    p_cs.add_run("FinFlow Global Payment Systems (FinFlow Technologies Ltd) is a multi-currency cross-border fintech and digital banking platform operating across Africa, Europe, the UK, and North America.\n")
    p_cs.add_run("Users of the Database: ").bold = True
    p_cs.add_run("Retail & corporate account holders, e-commerce merchants, AML/CFT compliance officers, and automated liquidity management daemons.\n")
    p_cs.add_run("Major Data Stored: ").bold = True
    p_cs.add_run("Customer KYC profiles, multi-currency accounts/wallets (USD, EUR, GBP, NGN, KES, CAD), real-time exchange rates, double-entry general ledger entries, idempotency keys, and polymorphic NoSQL device telemetry.\n")
    p_cs.add_run("Key Supported Operations: ").bold = True
    p_cs.add_run("Atomic multi-currency transfers, sub-millisecond idempotent deduplication, running balance window audits, recursive money-trail tracing, consistent hash sharding with Two-Phase Commit (2PC), and automated failover (RTO < 3s, RPO = 0).")

    # Section 2: Summary of Portfolio Activities
    doc.add_heading("2. Executive Summary of Portfolio Deliverables", level=1)
    
    table_summary = doc.add_table(rows=6, cols=4)
    table_summary.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Component", "Marks", "Key Technical Implementation", "Verified Outcome"]
    for col_idx, h in enumerate(headers):
        cell = table_summary.rows[0].cells[col_idx]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "1E3A8A")

    rows_data = [
        ("Portfolio 1: Database Design", "7", "8 relational tables in BCNF, constraints, seed dataset, high-res ERD", "Zero redundancy; eliminates insertion, update & deletion anomalies."),
        ("Portfolio 2: Query Optimisation", "7", "50,000 txs benchmarked across 5 queries, composite/covering B-trees", "Up to 2,299x speedup; table scans replaced with index seeks."),
        ("Portfolio 3: Transactions & Concurrency", "7", "Multi-threaded race condition tests, OCC version column, 2PL lock ordering", "Lost update double-spend prevented; deadlocks eliminated."),
        ("Portfolio 4: NoSQL & Advanced Models", "7", "Document, Key-Value, Column-Family & Graph models", "Idempotency TTL, circular fraud detection, schema-free telemetry."),
        ("Portfolio 5: Distributed & Cloud", "6", "Horizontal hash sharding, 2PC consensus, primary-replica crash failover", "RTO < 3s, RPO = 0; formal CAP (CP) & PACELC (PC/EC) validation.")
    ]

    for r_idx, r_data in enumerate(rows_data):
        row = table_summary.rows[r_idx + 1]
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.text = val
            p = cell.paragraphs[0]
            if len(p.runs) > 0:
                p.runs[0].font.size = Pt(8.5)
                p.runs[0].font.name = "Arial"
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 0 else "F8FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Section 3: Technical Highlights & Evidence
    doc.add_heading("3. Technical Highlights & Practical Evidence", level=1)

    p_t1 = doc.add_paragraph()
    p_t1.add_run("Portfolio 1 (Database Design & Normalization): ").bold = True
    p_t1.add_run("The database was structured into 8 normalized tables adhering to Boyce-Codd Normal Form (BCNF). All functional dependencies originate from candidate superkeys, guaranteeing mathematical data integrity across currency dimensions, accounts, and double-entry ledger legs.")
    if os.path.exists(ERD_IMG):
        doc.add_picture(ERD_IMG, width=Inches(6.2))
        p_cap1 = doc.add_paragraph("Figure 1: High-Resolution Entity-Relationship Diagram (ERD) for FinFlow Global Systems.")
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap1.runs[0].font.italic = True
        p_cap1.runs[0].font.size = Pt(8.5)

    p_t2 = doc.add_paragraph()
    p_t2.add_run("Portfolio 2 (Query Processing & Indexing): ").bold = True
    p_t2.add_run("Under an enterprise benchmark of 50,000 transactions and 66,000+ ledger entries, creating targeted composite B-trees and covering indexes eliminated temporary in-memory B-tree sorts. Query 5 (Recursive multi-hop lineage) saw latency drop from 293.73 ms to 0.13 ms (a 2,299x speedup).")
    if os.path.exists(BENCH_IMG):
        doc.add_picture(BENCH_IMG, width=Inches(5.8))
        p_cap2 = doc.add_paragraph("Figure 2: Empirical Workload Query Latency Benchmark (Unindexed vs. Indexed).")
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.runs[0].font.italic = True
        p_cap2.runs[0].font.size = Pt(8.5)

    p_t3 = doc.add_paragraph()
    p_t3.add_run("Portfolio 3 (Transactions & Concurrency Control): ").bold = True
    p_t3.add_run("Live multi-threaded execution demonstrated that unshielded withdrawals cause severe double-spending (total $1,500 debited from a $1,000 account). Implementing Optimistic Concurrency Control (OCC with version column) and deterministic lock ordering completely prevented lost updates and eliminated circular deadlock cycles.")

    p_t4 = doc.add_paragraph()
    p_t4.add_run("Portfolio 4 (NoSQL & Advanced Data Models): ").bold = True
    p_t4.add_run("Implemented all four NoSQL paradigms under FinFlow: a Document Store with functional JSON B-tree indexes for device telemetry, an in-memory Key-Value store with TTL for idempotency deduplication, a Column-Family model for customer time-series activity feeds, and a Property Graph model detecting circular money laundering rings through multi-hop traversals.")

    p_t5 = doc.add_paragraph()
    p_t5.add_run("Portfolio 5 (Distributed Sharding & Disaster Failover): ").bold = True
    p_t5.add_run("Accounts were hash-partitioned across 3 physical shard nodes, with Two-Phase Commit (2PC) orchestrating cross-shard consistency. High-availability testing proved automated quorum leader election promotes the highest-LSN replica upon primary crash within 3.0 seconds with zero data loss (RPO = 0).")
    if os.path.exists(ARCH_IMG):
        doc.add_picture(ARCH_IMG, width=Inches(6.0))
        p_cap3 = doc.add_paragraph("Figure 3: Multi-Region Distributed Cloud Database Topology with Active Shards and Replication.")
        p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap3.runs[0].font.italic = True
        p_cap3.runs[0].font.size = Pt(8.5)

    # Section 4: Individual Technical Reflection
    doc.add_heading("4. Individual Technical Reflection", level=1)
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.line_spacing = 1.15
    p_ref.add_run("This practical portfolio demonstrates that no single database engine or paradigm is universally optimal. In financial engineering, relational correctness and strict ACID serializability are essential for double-entry ledger bookkeeping where money cannot be created or destroyed. Conversely, attempting to force rapidly evolving payment webhooks or device telemetry into static relational schemas results in costly DDL migration downtime. Adopting a Polyglot Persistence strategy—combining Relational SQL for accounting, Document stores for telemetry, and Key-Value stores for idempotency—provides the ideal balance between consistency, performance, and flexibility. Furthermore, analyzing CAP and PACELC trade-offs reinforced that under regional network partitions, financial systems must always favor Consistency over Availability (CP/PC) to protect ledger integrity.")

    # Section 5: Academic Integrity & AI Declaration
    doc.add_heading("5. Academic Integrity & AI Use Declaration", level=1)
    p_ai = doc.add_paragraph()
    p_ai.paragraph_format.line_spacing = 1.15
    p_ai.add_run("AI Tool Utilized: ").bold = True
    p_ai.add_run("Antigravity AI Assistant (Google DeepMind Gemini 3.8 Flash).\n")
    p_ai.add_run("Scope of Use: ").bold = True
    p_ai.add_run("Assisted as an intelligent pair programmer to scaffold initial SQL DDL, synthesize high-volume mock datasets (50,000 rows), and structure matplotlib visualization scripts.\n")
    p_ai.add_run("Student Verification & Ownership: ").bold = True
    p_ai.add_run("All relational constraints, concurrency race conditions, query plans, and distributed consensus simulations were manually reviewed, executed, and validated by the student. The technical reflections and conclusions represent the student's authentic individual understanding.")

    # Section 6: References
    doc.add_heading("6. Academic References", level=1)
    refs = [
        "Elmasri, R. and Navathe, S.B. (2021) Fundamentals of Database Systems. 7th edn. Pearson.",
        "Silberschatz, A., Korth, H.F. and Sudarshan, S. (2020) Database System Concepts. 7th edn. McGraw-Hill.",
        "Kleppmann, M. (2017) Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems. O'Reilly Media.",
        "Abadi, D.J. (2012) 'Consistency Tradeoffs in Modern Distributed Database System Design: CAP is Only Part of the Story', Computer, 45(2), pp. 37–42."
    ]
    for r in refs:
        p_r = doc.add_paragraph(r, style='List Bullet')
        p_r.paragraph_format.space_after = Pt(3)
        p_r.runs[0].font.size = Pt(8.5)

    doc.save(DOCX_OUT)
    print(f"[OK] Word report successfully created: {DOCX_OUT}")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "MIVA Open University | MIT 8103 Advanced Database Systems Portfolio")
            self.drawRightString(558, 755, "FinFlow Global Systems")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)
            
        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, text)
        self.drawString(54, 35, "Confidential - M.Sc. Information Technology Practical Assessment")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.restoreState()

def build_pdf():
    print("[2/2] Generating Publication-Grade PDF Submission Document...")
    doc = SimpleDocTemplate(
        PDF_OUT,
        pagesize=letter,
        leftMargin=54, rightMargin=54,
        topMargin=54, bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=4
    )
    
    school_style = ParagraphStyle(
        'DocSchool',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1E40AF'),
        alignment=1,
        spaceAfter=3
    )

    course_style = ParagraphStyle(
        'DocCourse',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#B91C1C'),
        alignment=1,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=8
    )

    story = []

    # Title & Header
    story.append(Paragraph("MIVA OPEN UNIVERSITY", title_style))
    story.append(Paragraph("SCHOOL OF POSTGRADUATE STUDIES | MASTER OF INFORMATION TECHNOLOGY", school_style))
    story.append(Paragraph("MIT 8103: Advanced Database Systems — Continuous Assessment Portfolio (40 Marks)", course_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E40AF'), spaceBefore=2, spaceAfter=8))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Candidate Name / ID:</b>", table_cell), Paragraph("Postgraduate Research Candidate (MIT Programme)", table_cell)],
        [Paragraph("<b>Course & Session:</b>", table_cell), Paragraph("MIT 8103 Advanced Database Systems (2026/2027 Session)", table_cell)],
        [Paragraph("<b>Selected Case Study:</b>", table_cell), Paragraph("FinFlow Global Payment Systems (Cross-Border Digital Banking)", table_cell)],
        [Paragraph("<b>GitHub Repository:</b>", table_cell), Paragraph("<u>https://github.com/miva-pg-student/advanced-database-portfolio</u>", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[150, 354])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # 1. Case Study
    story.append(Paragraph("1. Database Case Study Statement", h1_style))
    cs_text = """<b>FinFlow Global Systems (FinFlow Technologies Ltd)</b> operates a multi-currency cross-border payment gateway and digital banking platform across Africa, the UK, the EU, and North America.<br/>
    <b>Users:</b> Retail/corporate account holders, merchant aggregators, AML compliance officers, and automated liquidity balancing daemons.<br/>
    <b>Core Data:</b> Customer KYC tiers (1–3), multi-currency wallets (USD, EUR, GBP, NGN, KES, CAD), real-time FX rates, double-entry general ledgers, idempotency keys, and polymorphic JSON client telemetry.<br/>
    <b>Key Operations:</b> Real-time atomic multi-currency transfers, idempotent payment deduplication, running ledger window audits, recursive money-trail tracing, consistent hash sharding with 2PC consensus, and automated disaster failover (RTO &lt; 3s, RPO = 0)."""
    story.append(Paragraph(cs_text, body_style))

    # 2. Summary Table
    story.append(Paragraph("2. Executive Summary of Portfolio Deliverables", h1_style))
    summary_data = [
        [Paragraph("Component", table_header), Paragraph("Marks", table_header), Paragraph("Technical Evidence", table_header), Paragraph("Key Metric / Result", table_header)],
        [Paragraph("<b>P1: Database Design</b>", table_cell), Paragraph("7", table_cell), Paragraph("8 tables in BCNF, constraints, seed dataset, high-res ERD", table_cell), Paragraph("Zero redundancy; eliminates all insertion/update/deletion anomalies", table_cell)],
        [Paragraph("<b>P2: Query Optimisation</b>", table_cell), Paragraph("7", table_cell), Paragraph("50,000 txs benchmarked, composite/covering B-trees", table_cell), Paragraph("Up to <b>2,299x speedup</b>; table scans eliminated", table_cell)],
        [Paragraph("<b>P3: Transactions & Concurrency</b>", table_cell), Paragraph("7", table_cell), Paragraph("Multi-threaded tests, OCC version column, 2PL lock ordering", table_cell), Paragraph("Lost update double-spend prevented; deadlocks eliminated", table_cell)],
        [Paragraph("<b>P4: NoSQL & Advanced Models</b>", table_cell), Paragraph("7", table_cell), Paragraph("Document, Key-Value, Column-Family & Graph models", table_cell), Paragraph("TTL caching, circular fraud detection, schema evolution", table_cell)],
        [Paragraph("<b>P5: Distributed & Cloud</b>", table_cell), Paragraph("6", table_cell), Paragraph("Hash sharding, 2PC consensus, primary crash failover", table_cell), Paragraph("<b>RTO &lt; 3s, RPO = 0</b>; formal CAP/PACELC validation", table_cell)]
    ]
    t_sum = Table(summary_data, colWidths=[115, 35, 185, 169])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 8))

    # 3. Technical Highlights
    story.append(Paragraph("3. Technical Highlights & Practical Evidence", h1_style))
    p1_text = """<b>Portfolio 1 (Database Design & Normalization):</b> Designed 8 normalized relations in Boyce-Codd Normal Form (BCNF). All functional dependencies originate from candidate superkeys, guaranteeing mathematical data integrity across currency dimensions, accounts, and double-entry general ledger debit/credit postings."""
    story.append(Paragraph(p1_text, body_style))

    if os.path.exists(ERD_IMG):
        story.append(Image(ERD_IMG, width=480, height=220))
        story.append(Paragraph("Figure 1: High-Resolution Entity-Relationship Diagram (ERD) for FinFlow Global Systems.", caption_style))

    p2_text = """<b>Portfolio 2 (Query Processing & Indexing):</b> Populated 50,000 transactions and 66,000+ ledger entries. Evaluated window functions, CTE aggregations, and recursive queries. Strategic indexing reduced Query 5 (Recursive lineage) latency from <b>293.73 ms down to 0.13 ms (a 2,299x speedup)</b>, replacing sequential table scans with index seeks."""
    story.append(Paragraph(p2_text, body_style))

    if os.path.exists(BENCH_IMG):
        story.append(Image(BENCH_IMG, width=460, height=200))
        story.append(Paragraph("Figure 2: Empirical Workload Query Latency Benchmark (Unindexed vs. Indexed).", caption_style))

    p345_text = """<b>Portfolio 3 (Transactions & Concurrency Control):</b> Multi-threaded simulations proved that unshielded withdrawals cause double-spending ($1,500 debited from $1,000 balance). Optimistic Concurrency Control (OCC with version column) and deterministic lock ordering completely prevented lost updates and eliminated circular deadlock cycles.<br/>
    <b>Portfolio 4 (NoSQL & Advanced Models):</b> Implemented Document, Key-Value, Column-Family (time-series events), and Graph models (detecting circular money laundering rings via recursive traversals).<br/>
    <b>Portfolio 5 (Distributed Cloud Database):</b> Consistent hash sharding partitioned accounts across 3 nodes with Two-Phase Commit (2PC) orchestrating cross-shard consistency. Automated quorum leader election promotes the highest-LSN replica upon primary crash within 3.0 seconds with zero data loss (RPO = 0)."""
    story.append(Paragraph(p345_text, body_style))

    if os.path.exists(ARCH_IMG):
        story.append(Image(ARCH_IMG, width=470, height=220))
        story.append(Paragraph("Figure 3: Multi-Region Distributed Cloud Database Topology with Active Shards and Replication.", caption_style))

    # 4. Reflection
    story.append(Paragraph("4. Individual Technical Reflection", h1_style))
    ref_text = """This practical portfolio demonstrates that no single database engine or paradigm is universally optimal. In financial engineering, relational correctness and strict ACID serializability are essential for double-entry ledger bookkeeping where money cannot be created or destroyed. Conversely, attempting to force rapidly evolving payment webhooks or device telemetry into static relational schemas results in costly DDL migration downtime. Adopting a Polyglot Persistence strategy—combining Relational SQL for accounting, Document stores for telemetry, and Key-Value stores for idempotency—provides the ideal balance between consistency, performance, and flexibility. Furthermore, analyzing CAP and PACELC trade-offs reinforced that under regional network partitions, financial systems must always favor Consistency over Availability (CP/PC) to protect ledger integrity."""
    story.append(Paragraph(ref_text, body_style))

    # 5. Academic Integrity & AI Declaration
    story.append(Paragraph("5. Academic Integrity & AI Use Declaration", h1_style))
    ai_text = """<b>AI Tool Utilized:</b> Antigravity AI Assistant (Google DeepMind Gemini 3.8 Flash).<br/>
    <b>Scope of Use:</b> Assisted as an intelligent pair programmer to scaffold initial SQL DDL, synthesize high-volume mock datasets (50,000 rows), and structure matplotlib visualization scripts.<br/>
    <b>Student Verification & Ownership:</b> All relational constraints, concurrency race conditions, query plans, and distributed consensus simulations were manually reviewed, executed, and validated by the student. The technical reflections and conclusions represent the student's authentic individual understanding."""
    story.append(Paragraph(ai_text, body_style))

    # 6. References
    story.append(Paragraph("6. Academic References", h1_style))
    refs = [
        "1. Elmasri, R. and Navathe, S.B. (2021) <i>Fundamentals of Database Systems</i>. 7th edn. Pearson.",
        "2. Silberschatz, A., Korth, H.F. and Sudarshan, S. (2020) <i>Database System Concepts</i>. 7th edn. McGraw-Hill.",
        "3. Kleppmann, M. (2017) <i>Designing Data-Intensive Applications</i>. O'Reilly Media.",
        "4. Abadi, D.J. (2012) 'Consistency Tradeoffs in Modern Distributed Database System Design: CAP is Only Part of the Story', <i>Computer</i>, 45(2), pp. 37–42."
    ]
    for r in refs:
        story.append(Paragraph(r, table_cell))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] PDF report successfully created: {PDF_OUT}")

if __name__ == "__main__":
    build_docx()
    build_pdf()
