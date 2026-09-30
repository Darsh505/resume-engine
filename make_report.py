"""
Script to generate Darshveer_Singh_2449377_Industrial_Training_Report.docx
Strictly aligned with Rayat Bahra Institute of Engineering & Nanotechnology
Guidelines for FINAL PROJECT REPORT (4th Semester Industrial Training)
and Annexure-II / Annexure-III standards.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="506070", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_page_border(section):
    pgBorders = parse_xml(f'''
        <w:pgBorders {nsdecls("w")} w:offsetFrom="page">
            <w:top w:val="single" w:sz="12" w:space="24" w:color="000000"/>
            <w:left w:val="single" w:sz="12" w:space="24" w:color="000000"/>
            <w:bottom w:val="single" w:sz="12" w:space="24" w:color="000000"/>
            <w:right w:val="single" w:sz="12" w:space="24" w:color="000000"/>
        </w:pgBorders>
    ''')
    section._sectPr.append(pgBorders)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    run.underline = True
    run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = True
    run.italic = True
    run.font.color.rgb = RGBColor(0x20, 0x20, 0x20)
    return p

def add_body_p(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
    return p

def add_code_block(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.left_indent = Inches(0.3)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(0x1A, 0x2E, 0x40)
    return p

def add_callout_box(doc, text, title="NOTE"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.rows[0].cells[0]
    c.width = Inches(6.0)
    set_cell_background(c, "F5F8FA")
    set_cell_margins(c, top=80, bottom=80, left=140, right=140)
    set_table_borders(tbl, "003366", "10")
    p = c.paragraphs[0]
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(0)
    r1 = p.add_run(f"[{title}] ")
    r1.bold = True
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    r2 = p.add_run(text)
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(10.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_report():
    doc = docx.Document()
    section = doc.sections[0]
    # Margins per guidelines: Top: 1.0", Bottom: 1.0", Right: 0.8", Left: 1.2"
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.2)
    section.right_margin = Inches(0.8)
    add_page_border(section)

    # Base style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.paragraph_format.line_spacing = 1.5

    # Header and Footer
    header = section.header
    hp = header.paragraphs[0]
    hp.text = "Resume Engine"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.style.font.name = "Times New Roman"
    hp.style.font.size = Pt(9)
    hp.style.font.color.rgb = RGBColor(0x50, 0x50, 0x50)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.text = "Roll No. 2449377"
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fp.style.font.name = "Times New Roman"
    fp.style.font.size = Pt(9)
    fp.style.font.color.rgb = RGBColor(0x50, 0x50, 0x50)

    # =========================================================================
    # FRONT PAGE (ANNEXURE - II)
    # =========================================================================
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.space_before = Pt(10)
    tp.paragraph_format.space_after = Pt(12)
    tp.paragraph_format.line_spacing = 1.5

    r_title = tp.add_run("RESUME ENGINE: GIT-DRIVEN TAG-BASED RESUME COMPILATION SYSTEM\n")
    r_title.bold = True
    r_title.font.size = Pt(18)
    r_title.font.name = "Times New Roman"

    r_sub = tp.add_run("\nA SIX WEEKS INDUSTRIAL TRAINING REPORT\n")
    r_sub.font.size = Pt(14)
    r_sub.font.name = "Times New Roman"

    r_part = tp.add_run("IN THE PARTIAL FULFILLMENT FOR THE AWARD OF THE DEGREE\nOF\n")
    r_part.font.size = Pt(14)
    r_part.font.name = "Times New Roman"

    r_deg = tp.add_run("BACHELOR OF TECHNOLOGY\n")
    r_deg.bold = True
    r_deg.font.size = Pt(16)
    r_deg.font.name = "Times New Roman"

    r_in = tp.add_run("IN\n")
    r_in.font.size = Pt(14)
    r_in.font.name = "Times New Roman"

    r_branch = tp.add_run("COMPUTER SCIENCE & ENGINEERING\n(ARTIFICIAL INTELLIGENCE & MACHINE LEARNING)\n\n")
    r_branch.bold = True
    r_branch.font.size = Pt(14)
    r_branch.font.name = "Times New Roman"

    r_subby = tp.add_run("SUBMITTED BY\n")
    r_subby.italic = True
    r_subby.font.size = Pt(14)
    r_subby.font.name = "Times New Roman"

    r_name = tp.add_run("DARSHVEER SINGH\n")
    r_name.bold = True
    r_name.font.size = Pt(14)
    r_name.font.name = "Times New Roman"

    r_roll = tp.add_run("UNIVERSITY ROLL NO: 2449377\n\n\n")
    r_roll.bold = True
    r_roll.font.size = Pt(12)
    r_roll.font.name = "Times New Roman"

    r_inst = tp.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nRAYAT BAHRA INSTITUTE OF ENGINEERING & NANOTECHNOLOGY\nHOSHIARPUR - 146104, PUNJAB (INDIA)\nJULY, 2026")
    r_inst.bold = True
    r_inst.font.size = Pt(12)
    r_inst.font.name = "Times New Roman"

    # =========================================================================
    # CERTIFICATE (Page i)
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "CERTIFICATE")
    add_body_p(doc, "This is to certify that the Six Weeks Industrial Training Report entitled \"RESUME ENGINE: GIT-DRIVEN TAG-BASED RESUME COMPILATION SYSTEM\" submitted by DARSHVEER SINGH (University Roll No: 2449377) in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology in Computer Science & Engineering (Artificial Intelligence & Machine Learning) of Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur, is an authentic record of industrial training carried out at Mits Academy from 8 June 2026 to 28 July 2026.")
    add_body_p(doc, "The matter embodied in this project report has not been submitted by him for the award of any other degree or diploma to any other institute or university.")

    sig_t = doc.add_table(rows=2, cols=2)
    sig_t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in sig_t.rows:
        r.cells[0].width = Inches(3.2)
        r.cells[1].width = Inches(3.2)

    p0 = sig_t.rows[1].cells[0].paragraphs[0]
    p0.add_run("Verified by:\n\n\n\n").font.size = Pt(11)
    p0.add_run("Mentor Srishti\nTechnical Lead & Corporate Trainer\nMits Academy").bold = True

    p1 = sig_t.rows[1].cells[1].paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.add_run("Approved by:\n\n\n\n").font.size = Pt(11)
    p1.add_run("Head of Department\nDepartment of Computer Science & Engg.\nRBIENT, Hoshiarpur").bold = True

    # =========================================================================
    # ACKNOWLEDGEMENT (Page ii)
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "ACKNOWLEDGEMENT")
    add_body_p(doc, "I express my profound gratitude and sincere appreciation to my respected industrial mentor, Mentor Srishti, Technical Lead at Mits Academy, for her invaluable guidance, constructive critique, and continuous technical support throughout the course of this industrial training. Her deep domain knowledge in software architecture, type-safe Python programming, and applicant tracking systems provided crucial insights that shaped the design of the Resume Engine system.")
    add_body_p(doc, "I am immensely grateful to Mits Academy for providing a state-of-the-art technical environment, industry-standard toolchains, and collaborative learning culture that fostered hands-on software development.")
    add_body_p(doc, "I also extend my heartfelt thanks to the Head of Department, faculty members, and project coordinators of the Department of Computer Science & Engineering at Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur, for their academic encouragement, structural guidelines, and permission to undertake this six-week industrial training program.")
    add_body_p(doc, "Lastly, I wish to thank my family and fellow peers for their unwavering encouragement, technical discussions, and assistance during the project verification phase.")

    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ack.paragraph_format.space_before = Pt(30)
    p_ack.add_run("Darshveer Singh\n").bold = True
    p_ack.add_run("University Roll No: 2449377\nB.Tech CSE (AI & ML), 4th Semester\nRayat Bahra Institute of Engineering & Nanotechnology")

    # =========================================================================
    # DECLARATION (Page iii)
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "DECLARATION")
    add_body_p(doc, "I, DARSHVEER SINGH (University Roll No: 2449377), student of Bachelor of Technology in Computer Science & Engineering (Artificial Intelligence & Machine Learning), 4th Semester at Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur, hereby declare that the industrial training report entitled \"RESUME ENGINE: GIT-DRIVEN TAG-BASED RESUME COMPILATION SYSTEM\" is an authentic and original record of the work carried out by me at Mits Academy during the period from 8 June 2026 to 28 July 2026 under the mentorship of Mentor Srishti.")
    add_body_p(doc, "I further declare that this report has been composed by me and has not been submitted previously in part or in full to this institute or any other institution for the award of any academic degree, diploma, or fellowship.")
    add_body_p(doc, "All external code modules, algorithmic concepts, and library references utilized during development have been appropriately cited and acknowledged in the bibliography.")

    p_dec = doc.add_paragraph()
    p_dec.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_dec.paragraph_format.space_before = Pt(30)
    p_dec.add_run("Darshveer Singh\n").bold = True
    p_dec.add_run("University Roll No: 2449377\nDate: 28 July 2026\nPlace: Hoshiarpur")

    # =========================================================================
    # TABLE OF CONTENTS (Page iv)
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "TABLE OF CONTENTS")
    
    toc_t = doc.add_table(rows=1, cols=3)
    toc_t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(toc_t, "8090A0", "4")
    
    headers = ["CHAPTER / SECTION", "TITLE", "PAGE NO."]
    for idx, text in enumerate(headers):
        cell = toc_t.rows[0].cells[idx]
        set_cell_background(cell, "003366")
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(10)
    
    toc_items = [
        ("", "Certificate", "i"),
        ("", "Acknowledgement", "ii"),
        ("", "Declaration", "iii"),
        ("", "Table of Contents", "iv"),
        ("", "List of Tables", "v"),
        ("", "List of Figures", "vi"),
        ("", "List of Acronyms", "vii"),
        ("CHAPTER-1", "OVERVIEW OF TECHNOLOGY", "1"),
        ("  1.1", "Python 3.14 & Type Annotations", "1"),
        ("  1.2", "ReportLab 5.0 PDF Generation Engine", "2"),
        ("  1.3", "FastAPI Framework & Pydantic Validation", "3"),
        ("  1.4", "Uvicorn Asynchronous Web Server", "4"),
        ("  1.5", "PyYAML & Single Source of Truth Architecture", "5"),
        ("  1.6", "GitPython & Version Control Integration", "6"),
        ("  1.7", "Jinja2 Server-Side Templating", "7"),
        ("  1.8", "Pytest Automated Testing Framework", "8"),
        ("CHAPTER-2", "PROJECT REPORT WORK", "9"),
        ("  2.1", "Introduction to Resume Engine", "9"),
        ("  2.2", "Project Objectives", "10"),
        ("  2.3", "Methodology & Architecture", "11"),
        ("    2.3.1", "Flowcharts and Data Flow Diagrams", "12"),
        ("    2.3.2", "Entity Relationship & Schema Models", "14"),
        ("    2.3.3", "Use Case Diagrams & Data Dictionary", "16"),
        ("    2.3.4", "Project Gantt Chart (37 Working Days)", "18"),
        ("  2.4", "Hardware and Software Requirements", "19"),
        ("  2.5", "Project Source Code & Local Execution Profile", "20"),
        ("CHAPTER-3", "USER GUIDE & RUNNING INSTRUCTIONS", "21"),
        ("  3.1", "System Installation & Environment Setup", "21"),
        ("  3.2", "CLI Compilation Workflow & Command Reference", "22"),
        ("  3.3", "Web Management Interface & Resume Studio", "24"),
        ("  3.4", "Automated Testing & Quality Verification", "26"),
        ("  3.5", "System Verification & Screen Representations", "27"),
        ("CHAPTER-4", "CONCLUSION & FUTURE SCOPE", "29"),
        ("  4.1", "Conclusion", "29"),
        ("  4.2", "Future Scope", "30"),
        ("", "References & Bibliography", "31")
    ]
    
    col_widths = [Inches(1.8), Inches(4.0), Inches(0.8)]
    for row_data in toc_items:
        row = toc_t.add_row()
        for idx, text in enumerate(row_data):
            cell = row.cells[idx]
            cell.width = col_widths[idx]
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if row_data[0].startswith("CHAPTER") or row_data[1] in ["Certificate", "Table of Contents"]:
                r.bold = True
                set_cell_background(cell, "F2F6FA")

    # =========================================================================
    # LIST OF TABLES (Page v)
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "LIST OF TABLES")
    
    tbl_t = doc.add_table(rows=1, cols=3)
    tbl_t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_t, "8090A0", "4")
    
    for idx, text in enumerate(["TABLE NO.", "TITLE", "PAGE NO."]):
        cell = tbl_t.rows[0].cells[idx]
        set_cell_background(cell, "003366")
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(10)
        
    tables_list = [
        ("Table 1.1", "Core Technology Stack & Dependency Specifications", "2"),
        ("Table 2.1", "Resume Engine YAML Data Schema & Field Constraints", "14"),
        ("Table 2.2", "Data Dictionary for Resume Entity Attributes", "17"),
        ("Table 2.3", "Industrial Training Schedule & Milestones (Gantt Summary)", "18"),
        ("Table 2.4", "Hardware and Software Environment Requirements", "19"),
        ("Table 2.5", "Project Source Code & Local Execution Profile", "20"),
        ("Table 3.1", "CLI Compilation Commands and Flag Reference", "23"),
        ("Table 3.2", "FastAPI Route Handlers and HTTP Methods", "25"),
        ("Table 3.3", "Pytest Automated Test Suite Coverage Breakdown", "26")
    ]
    for t_no, title, page in tables_list:
        row = tbl_t.add_row()
        for idx, text in enumerate([t_no, title, page]):
            cell = row.cells[idx]
            cell.width = col_widths[idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(10)

    # =========================================================================
    # LIST OF FIGURES (Page vi)
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "LIST OF FIGURES")
    
    fig_t = doc.add_table(rows=1, cols=3)
    fig_t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(fig_t, "8090A0", "4")
    
    for idx, text in enumerate(["FIGURE NO.", "TITLE", "PAGE NO."]):
        cell = fig_t.rows[0].cells[idx]
        set_cell_background(cell, "003366")
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(10)
        
    figures_list = [
        ("Figure 1.1", "Decoupled Resume Engine Architectural Ecosystem", "4"),
        ("Figure 2.1", "Context Level 0 Data Flow Diagram", "12"),
        ("Figure 2.2", "Level 1 Detailed Processing Pipeline & Budget Filter", "13"),
        ("Figure 2.3", "Entity Relationship Diagram for Resume Data Model", "15"),
        ("Figure 2.4", "Use Case Interaction Diagram for Student & Engine", "16"),
        ("Figure 3.1", "CLI Compilation Output with Colorama Visual Steps", "27"),
        ("Figure 3.2", "FastAPI Local Web Resume Studio Form Interface", "28"),
        ("Figure 3.3", "Final Rendered Single-Page Role-Tailored PDF Resume", "28")
    ]
    for f_no, title, page in figures_list:
        row = fig_t.add_row()
        for idx, text in enumerate([f_no, title, page]):
            cell = row.cells[idx]
            cell.width = col_widths[idx]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(10)

    # =========================================================================
    # LIST OF ACRONYMS (Page vii)
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "LIST OF ACRONYMS")
    
    acro_t = doc.add_table(rows=1, cols=2)
    acro_t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(acro_t, "8090A0", "4")
    
    acro_headers = ["ACRONYM", "EXPANSION / DEFINITION"]
    for idx, text in enumerate(acro_headers):
        cell = acro_t.rows[0].cells[idx]
        set_cell_background(cell, "003366")
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(10)
        
    acronyms_list = [
        ("AI & ML", "Artificial Intelligence & Machine Learning"),
        ("API", "Application Programming Interface"),
        ("ASGI", "Asynchronous Server Gateway Interface"),
        ("ATS", "Applicant Tracking System"),
        ("CLI", "Command Line Interface"),
        ("CRUD", "Create, Read, Update, Delete"),
        ("DFD", "Data Flow Diagram"),
        ("DOM", "Document Object Model"),
        ("ER", "Entity Relationship"),
        ("HTML", "HyperText Markup Language"),
        ("HTTP", "HyperText Transfer Protocol"),
        ("JSON", "JavaScript Object Notation"),
        ("PDF", "Portable Document Format"),
        ("PEP", "Python Enhancement Proposal"),
        ("REST", "Representational State Transfer"),
        ("SSOT", "Single Source of Truth"),
        ("UI / UX", "User Interface / User Experience"),
        ("URL", "Uniform Resource Locator"),
        ("UTF-8", "Unicode Transformation Format (8-bit)"),
        ("VCS", "Version Control System"),
        ("YAML", "YAML Ain't Markup Language")
    ]
    for acr, exp in acronyms_list:
        row = acro_t.add_row()
        row.cells[0].width = Inches(1.8)
        row.cells[1].width = Inches(4.8)
        for idx, text in enumerate([acr, exp]):
            cell = row.cells[idx]
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    # =========================================================================
    # CHAPTER 1: OVERVIEW OF TECHNOLOGY
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 1: OVERVIEW OF TECHNOLOGY")
    add_body_p(doc, "During the Six Weeks Summer Industrial Training at Mits Academy, the software engineering stack was established around contemporary Python systems programming, automated document typesetting, and asynchronous local web architecture. The technological focus centered on creating an offline-first, production-grade utility capable of generating high-precision Portable Document Format (PDF) resumes without third-party cloud dependencies or remote headless browser installations.")

    add_heading_2(doc, "1.1 Python Programming Language & Type Annotations")
    add_body_p(doc, "Python 3.14 serves as the core execution runtime for the Resume Engine project. The architecture strictly adheres to modern typing idioms introduced in PEP 484, PEP 563, and PEP 604, utilizing `from __future__ import annotations` across all script modules. This ensures runtime compatibility, simplifies forward-referencing, and provides comprehensive static verification through type linters.")
    add_body_p(doc, "Strong typing prevents subtle runtime bugs during nested dictionary filtering, data type transformations, and sorting routines. Python's built-in pathlib module guarantees platform-agnostic file path manipulation across Windows, macOS, and Linux platforms.")

    add_heading_2(doc, "1.2 ReportLab 5.0 PDF Generation Engine")
    add_body_p(doc, "ReportLab 5.0 is the premier open-source library for programmatic document creation in Python. Unlike headless browser renderers (such as Puppeteer or wkhtmltopdf) which require heavy rendering runtimes and consume significant memory, ReportLab operates directly at the PostScript and PDF primitive level. It translates typographic specifications directly into PDF bytecode.")
    add_body_p(doc, "Key features utilized in the Resume Engine implementation include:")
    add_body_p(doc, "1. Canvas Low-Level Coordinate System: Direct coordinate positioning with origin (0, 0) at the bottom-left corner of the page, operating on precise PostScript typographic points (72 points = 1 inch).")
    add_body_p(doc, "2. Flowable Typography Math: Utilizing ParagraphStyles, leading measurements, and font baseline calculations to prevent line overlap and enforce strict page bounds.")
    add_body_p(doc, "3. Color Space Consistency: Standardized RGB color definitions ensuring crisp rendering on high-resolution displays and monochrome laser printers.")

    add_heading_2(doc, "1.3 FastAPI Framework & Pydantic Validation")
    add_body_p(doc, "FastAPI 0.142 was selected as the backend controller for the local web management studio. Built on top of Starlette and Pydantic v2, FastAPI provides lightning-fast asynchronous request handling and automated request validation.")
    add_body_p(doc, "Pydantic v2 data models act as the schema boundary between user inputs from web forms and on-disk YAML persistence. By declaring structured schemas with strict field types, Pydantic immediately rejects invalid data payloads with detailed 422 Unprocessable Entity responses, preventing silent data corruption.")

    add_heading_2(doc, "1.4 Uvicorn Asynchronous Web Server")
    add_body_p(doc, "Uvicorn 0.54 is a lightning-fast Asynchronous Server Gateway Interface (ASGI) web server implementation for Python. In the Resume Engine ecosystem, Uvicorn binds strictly to the local loopback interface (http://127.0.0.1:8000), guaranteeing complete privacy and zero data leakage. It supports hot-reloading during development via the `--dev` parameter.")

    add_heading_2(doc, "1.5 PyYAML & Single Source of Truth (SSOT) Architecture")
    add_body_p(doc, "PyYAML 6.0 provides safe deserialization and serialization of the master resume database. The system implements a Single Source of Truth (SSOT) paradigm: the candidate stores all historical professional experience, multiple job roles, varied skillsets, and academic credentials in a single comprehensive YAML file.")
    add_body_p(doc, "Through `yaml.safe_load()`, malicious executable YAML tags are rejected. Furthermore, serialization preserves clean formatting and human readability when saving edits back to disk.")

    add_heading_2(doc, "1.6 GitPython & Version Control Integration")
    add_body_p(doc, "GitPython 3.2 connects the compilation pipeline directly to the candidate's local Git repository. Every time a resume is compiled, the engine stages the newly rendered PDF artifact and creates an automated Git commit with an ISO-8601 timestamp. This establishes an immutable audit log of resume submissions.")

    add_heading_2(doc, "1.7 Jinja2 Server-Side Templating")
    add_body_p(doc, "Jinja2 3.1 powers the server-side rendering of the local web form editor. By combining Jinja2 templates with semantic HTML5 form structures, the web interface loads without node_modules, webpack bundles, or frontend compilation steps.")

    add_heading_2(doc, "1.8 Pytest Automated Testing Framework")
    add_body_p(doc, "Pytest 9.1 provides robust test automation for validating filtering logic, budget capping algorithms, and edge-case handling. The project includes 42 comprehensive unit tests executing in under 0.1 seconds.")

    # Table 1.1
    t1_1 = doc.add_table(rows=1, cols=3)
    t1_1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1_1, "607080", "4")
    for idx, text in enumerate(["MODULE / LIBRARY", "VERSION", "TECHNICAL ROLE IN ARCHITECTURE"]):
        c = t1_1.rows[0].cells[idx]
        set_cell_background(c, "003366")
        p = c.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)
    
    t1_data = [
        ("Python", "3.14.7", "Core execution runtime and typing pipeline"),
        ("ReportLab", "5.0.1", "Typographic rendering and PDF bytecode creation"),
        ("FastAPI", "0.142.2", "Asynchronous HTTP backend and REST endpoints"),
        ("Uvicorn", "0.54.0", "Localhost ASGI web server (127.0.0.1:8000)"),
        ("Pydantic", "2.13.5", "Runtime schema modeling and data validation"),
        ("PyYAML", "6.0.3", "Safe YAML parsing and serialization"),
        ("GitPython", "3.2.0", "Local Git staging and automated commit logging"),
        ("Colorama", "0.4.6", "Terminal ANSI color formatting and status reporting"),
        ("Pytest", "9.1.1", "Automated test suite execution (42 tests)")
    ]
    for mod, ver, role in t1_data:
        row = t1_1.add_row()
        for idx, text in enumerate([mod, ver, role]):
            cell = row.cells[idx]
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_after = Pt(8)
    r = p_t1.add_run("Table 1.1: Core Technology Stack & Dependency Specifications")
    r.bold = True
    r.font.size = Pt(10)

    # =========================================================================
    # CHAPTER 2: PROJECT REPORT WORK
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 2: PROJECT REPORT WORK")

    add_heading_2(doc, "2.1 Introduction")
    add_body_p(doc, "In modern software recruitment, candidates encounter two acute challenges: resume drift and Applicant Tracking System (ATS) filtering. Resume drift occurs when job seekers create multiple disconnected Word documents for different career trajectories (such as Backend Engineer, Data Scientist, or DevOps Specialist). Over time, corrections made in one document fail to propagate to others, leading to inconsistent employment dates, outdated skills, and clerical errors.")
    add_body_p(doc, "Simultaneously, corporate ATS algorithms parse incoming resumes against job description keywords. Submitting a generic resume results in low relevance scoring and automatic rejection. Conversely, manually re-tailoring a document for each target position is time-consuming and introduces formatting regressions that cause single-page resumes to spill over onto an awkward second page.")
    add_body_p(doc, "The Resume Engine project resolves these issues through a deterministic, tag-driven compilation pipeline. The candidate maintains a single, comprehensive YAML document containing all career achievements, each tagged with one or more target identifiers. A single command-line flag or web selection extracts only the relevant bullets, orders them by priority, enforces strict vertical page budgets, and compiles an ATS-optimized, single-page PDF in milliseconds.")

    add_heading_2(doc, "2.2 Objectives")
    add_body_p(doc, "The engineering objectives formulated for the Resume Engine project include:")
    add_body_p(doc, "1. Unified Source of Truth: Centralize all professional credentials within a structured YAML file, eliminating multi-file duplication and version divergence.")
    add_body_p(doc, "2. Role-Based Tag Filtering: Implement an intelligent filter engine that extracts relevant experience, skills, and projects based on designated target tags (e.g. backend, frontend, data-science, devops, general).")
    add_body_p(doc, "3. Deterministic Page Budget Enforcement: Formulate mathematical caps across all resume sections (maximum 4 bullets per role, 3 projects, 4 achievements, 6 coursework items) ensuring strict single-page PDF compliance.")
    add_body_p(doc, "4. Lightweight Offline Architecture: Deliver high-speed rendering (< 250ms per resume) using ReportLab without external cloud APIs, headless browsers, or remote server dependencies.")
    add_body_p(doc, "5. Seamless Dual Interface: Provide both a powerful Command Line Interface (CLI) for batch developers and an interactive local web studio at http://127.0.0.1:8000 for intuitive browser editing.")
    add_body_p(doc, "6. Automated Version Control Ledger: Integrate Git versioning to track and auto-commit rendered PDF resumes upon generation.")

    add_heading_2(doc, "2.3 Methodology & System Architecture")
    add_body_p(doc, "The software engineering methodology adopted for the project is an iterative, decoupled pipeline model. The application architecture is segmented into four distinct layers:")
    add_body_p(doc, "1. Data Storage Layer (web/data_store.py): Manages disk I/O, safely loading data/resume.yaml and defaulting to data/resume.example.yaml when personal data has not yet been populated.")
    add_body_p(doc, "2. Filter & Budget Engine (filter_engine.py): Pure Python functional logic that accepts a raw resume dictionary and a target role tag, filters matching nodes, evaluates integer priorities, and enforces section budgets.")
    add_body_p(doc, "3. Typesetting & PDF Engine (pdf_renderer.py): Translates the filtered data dictionary into ReportLab drawing commands, managing coordinate spaces, typography, rules, and vector margins.")
    add_body_p(doc, "4. Presentation & Interaction Layer: Dual interfaces comprising compile_resume.py for terminal compilation and web/app.py for browser-based interactive form editing.")

    add_heading_3(doc, "2.3.1 Flowcharts & Data Flow Diagrams")
    add_body_p(doc, "The high-level data flow of the Resume Engine is illustrated below in Figure 2.1 (Context Level 0 DFD) and Figure 2.2 (Level 1 Processing Pipeline):")

    add_code_block(doc, 
"""+-----------------------------------------------------------------------+
|                       CONTEXT LEVEL 0 DFD                             |
+-----------------------------------------------------------------------+
|                                                                       |
|   +--------------+      Target Role Flag & Data      +------------+   |
|   |   Candidate  | ================================> |   RESUME   |   |
|   |  (Developer) | <================================ |   ENGINE   |   |
|   +--------------+      Single-Page Tailored PDF     +------------+   |
|                                                                       |
+-----------------------------------------------------------------------+""")

    p_f21 = doc.add_paragraph()
    p_f21.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f21.paragraph_format.space_after = Pt(6)
    r = p_f21.add_run("Figure 2.1: Context Level 0 Data Flow Diagram")
    r.bold = True
    r.font.size = Pt(10)

    add_code_block(doc,
"""+-----------------------------------------------------------------------+
|                   LEVEL 1 DETAILED PROCESSING PIPELINE                |
+-----------------------------------------------------------------------+
|                                                                       |
|  [ data/resume.yaml ]                                                 |
|          |                                                            |
|          v                                                            |
|  (1. Load & Validate) ------> [ Pydantic Schema Check ]               |
|          |                                                            |
|          v                                                            |
|  (2. Tag Matcher) ----------> Target Tag: 'backend' | 'frontend' etc.  |
|          |                    Filters: general + target tags          |
|          v                                                            |
|  (3. Priority Sorter) ------> Sorts items by 'priority: int' (desc)   |
|          |                                                            |
|          v                                                            |
|  (4. Budget Enforcer) ------> Caps: 4 bullets/job, 3 projects, etc.   |
|          |                                                            |
|          v                                                            |
|  (5. ReportLab Canvas) -----> Canvas coordinate calculation (792pt)   |
|          |                    Draws headers, rules, text flowables    |
|          v                                                            |
|  (6. Git Auto-Commit) ------> [ output/resume_<target>.pdf ]          |
|                                                                       |
+-----------------------------------------------------------------------+""")

    p_f22 = doc.add_paragraph()
    p_f22.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f22.paragraph_format.space_after = Pt(8)
    r = p_f22.add_run("Figure 2.2: Level 1 Detailed Processing Pipeline & Budget Filter")
    r.bold = True
    r.font.size = Pt(10)

    add_heading_3(doc, "2.3.2 Entity Relationship Diagram & Resume YAML Schema")
    add_body_p(doc, "The resume data model is organized as a hierarchical entity model where the candidate is the root entity possessing one-to-many relationships with work experience, projects, skills, education, and achievements.")

    add_code_block(doc,
"""+-----------------------------------------------------------------------+
|                      ENTITY RELATIONSHIP DIAGRAM                      |
+-----------------------------------------------------------------------+
|                                                                       |
|    +-------------------+ 1       * +-----------------------+          |
|    |     CANDIDATE     | --------> |    WORK EXPERIENCE    |          |
|    |-------------------|           |-----------------------|          |
|    | name, email,      |           | company, role, dates, |          |
|    | phone, location,  |           | bullets (with tags)   |          |
|    | linkedin, github  |           +-----------------------+          |
|    +-------------------+                                              |
|          | 1        | 1                     | 1                       |
|          |          |                       |                         |
|          | *        | *                     | *                       |
|          v          v                       v                         |
|    +-----------+  +---------------+   +--------------------+          |
|    |  PROJECTS |  |   EDUCATION   |   |    ACHIEVEMENTS    |          |
|    |-----------|  |---------------|   |--------------------|          |
|    | title,    |  | institution,  |   | title, impact,     |          |
|    | desc,     |  | degree, dates,|   | date, priority,    |          |
|    | tags,     |  | coursework,   |   | tags               |          |
|    | priority  |  | gpa           |   +--------------------+          |
|    +-----------+  +---------------+                                   |
|                                                                       |
+-----------------------------------------------------------------------+""")

    p_f23 = doc.add_paragraph()
    p_f23.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f23.paragraph_format.space_after = Pt(8)
    r = p_f23.add_run("Figure 2.3: Entity Relationship Diagram for Resume Data Model")
    r.bold = True
    r.font.size = Pt(10)

    # Table 2.1: Schema Table
    t2_1 = doc.add_table(rows=1, cols=4)
    t2_1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2_1, "607080", "4")
    for idx, text in enumerate(["SECTION", "FIELD NAME", "DATA TYPE", "BUDGET CAP / CONSTRAINT"]):
        c = t2_1.rows[0].cells[idx]
        set_cell_background(c, "003366")
        p = c.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)
        
    s_data = [
        ("Contact", "name, email, phone, links", "string", "Mandatory single header"),
        ("Experience", "company, role, location, dates", "string", "Max 3 positions"),
        ("Experience", "bullets", "list[dict]", "Strict cap: max 4 bullets per job"),
        ("Projects", "title, description, tags, priority", "list[dict]", "Strict cap: max 3 projects"),
        ("Skills", "category, items", "list[dict]", "Max 4 categories (e.g. Languages, Cloud)"),
        ("Education", "degree, institution, dates, gpa", "list[dict]", "Max 2 degrees"),
        ("Achievements", "award, context, priority, tags", "list[dict]", "Strict cap: max 4 achievements")
    ]
    for sec, fld, dt, cap in s_data:
        row = t2_1.add_row()
        for idx, text in enumerate([sec, fld, dt, cap]):
            cell = row.cells[idx]
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9)
            if idx == 0:
                r.bold = True

    p_t21 = doc.add_paragraph()
    p_t21.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t21.paragraph_format.space_after = Pt(8)
    r = p_t21.add_run("Table 2.1: Resume Engine YAML Data Schema & Field Constraints")
    r.bold = True
    r.font.size = Pt(10)

    add_heading_3(doc, "2.3.3 Use Case Diagrams & Data Dictionary")
    add_body_p(doc, "The interaction model for the system supports three core operational use cases:")
    add_body_p(doc, "1. Use Case 1 (CLI Compile): Developer runs `python compile_resume.py --target <role>` to generate a PDF and commit to Git.")
    add_body_p(doc, "2. Use Case 2 (Audit Targets): Developer runs `--targets-report` to view a summary matrix of bullets and skills matching each role.")
    add_body_p(doc, "3. Use Case 3 (Web Studio Edit): Developer launches `python run_web.py` to view, edit, and compile resumes via browser at http://127.0.0.1:8000.")

    add_heading_3(doc, "2.3.4 Industrial Training Gantt Chart")
    add_body_p(doc, "The training progressed across exactly 37 working days (8 June 2026 to 28 July 2026), structured into five distinct engineering milestones:")

    # Table 2.3: Gantt Summary
    t2_3 = doc.add_table(rows=1, cols=4)
    t2_3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2_3, "607080", "4")
    for idx, text in enumerate(["MILESTONE PHASE", "WORKING DAYS", "CALENDAR DATES", "CORE ENGINEERING DELIVERABLES"]):
        c = t2_3.rows[0].cells[idx]
        set_cell_background(c, "003366")
        p = c.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)
        
    g_data = [
        ("Phase I: Inception & Foundations", "Days 1 to 5", "08 Jun - 12 Jun 2026", "Environment setup, Python typing, Git configuration, domain analysis"),
        ("Phase II: Data Modeling & Schema", "Days 6 to 10", "15 Jun - 19 Jun 2026", "YAML schema definition, PyYAML parsing, Pydantic validation models"),
        ("Phase III: Filter Engine & Budgets", "Days 11 to 15", "22 Jun - 26 Jun 2026", "Tag matching algorithms, priority scoring, single-page budget caps"),
        ("Phase IV: ReportLab PDF Renderer", "Days 16 to 25", "29 Jun - 10 Jul 2026", "Canvas math, font scaling, Windows UTF-8 console fix, CLI entrypoint"),
        ("Phase V: Local Web Studio & Tests", "Days 26 to 37", "13 Jul - 28 Jul 2026", "FastAPI web editor, Jinja2 forms, 42 Pytest unit tests, exit review")
    ]
    for ph, days, dates, deliv in g_data:
        row = t2_3.add_row()
        for idx, text in enumerate([ph, days, dates, deliv]):
            cell = row.cells[idx]
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9)
            if idx == 0:
                r.bold = True

    p_t23 = doc.add_paragraph()
    p_t23.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t23.paragraph_format.space_after = Pt(8)
    r = p_t23.add_run("Table 2.3: Industrial Training Schedule & Milestones (Gantt Summary)")
    r.bold = True
    r.font.size = Pt(10)

    add_heading_2(doc, "2.4 Hardware & Software Requirements")
    add_body_p(doc, "The Resume Engine is intentionally engineered as an offline-first, resource-efficient utility. The complete hardware and software operational requirements are specified in Table 2.4:")

    # Table 2.4
    t2_4 = doc.add_table(rows=1, cols=3)
    t2_4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2_4, "607080", "4")
    for idx, text in enumerate(["COMPONENT", "MINIMUM SPECIFICATION", "DEVELOPMENT ENVIRONMENT USED"]):
        c = t2_4.rows[0].cells[idx]
        set_cell_background(c, "003366")
        p = c.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)
        
    hw_data = [
        ("Processor", "Dual Core 1.8 GHz or equivalent", "AMD Ryzen 7 / Intel Core i7 3.2 GHz"),
        ("RAM", "2 GB RAM (Engine consumes < 60 MB)", "16 GB DDR4 Dual-Channel RAM"),
        ("Storage", "100 MB free disk space", "512 GB NVMe Solid State Drive"),
        ("Operating System", "Windows 10+, macOS 12+, Ubuntu 20.04+", "Windows 11 Professional (64-bit)"),
        ("Python Runtime", "Python 3.10 or higher", "Python 3.14.7 (64-bit)"),
        ("Version Control", "Git 2.25+", "Git 2.48.1 with Credential Manager"),
        ("Web Browser", "Any standard browser (Chrome, Edge, Firefox)", "Google Chrome & Microsoft Edge")
    ]
    for comp, min_s, dev_s in hw_data:
        row = t2_4.add_row()
        for idx, text in enumerate([comp, min_s, dev_s]):
            cell = row.cells[idx]
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    p_t24 = doc.add_paragraph()
    p_t24.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t24.paragraph_format.space_after = Pt(8)
    r = p_t24.add_run("Table 2.4: Hardware and Software Environment Requirements")
    r.bold = True
    r.font.size = Pt(10)

    # Dedicated Table 2.5 (Requested by prompt)
    add_heading_2(doc, "2.5 Project Source Code & Local Execution Profile")
    add_body_p(doc, "Table 2.5 presents the official technical repository and local host profile for the Resume Engine project. As an offline-first security-conscious tool, the application is strictly executed on the local loopback interface, safeguarding personal candidate credentials:")

    t2_5 = doc.add_table(rows=1, cols=4)
    t2_5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2_5, "003366", "8")
    for idx, text in enumerate(["PROJECT TITLE", "TECHNICAL DOMAIN", "LOCAL EXECUTION HOST", "GITHUB REPOSITORY"]):
        c = t2_5.rows[0].cells[idx]
        set_cell_background(c, "003366")
        p = c.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)

    r_row = t2_5.add_row()
    p_vals = [
        "Resume Engine",
        "Systems Programming, Document Typesetting, Asynchronous Web Studio",
        "http://127.0.0.1:8000 (Local Offline)",
        "https://github.com/Darsh505/resume-engine"
    ]
    for idx, val in enumerate(p_vals):
        c = r_row.cells[idx]
        set_cell_background(c, "F5F9FC")
        set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(val)
        r.font.size = Pt(9.5)
        if idx == 0:
            r.bold = True

    p_t25 = doc.add_paragraph()
    p_t25.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t25.paragraph_format.space_after = Pt(8)
    r = p_t25.add_run("Table 2.5: Project Source Code & Local Execution Profile")
    r.bold = True
    r.font.size = Pt(10)

    # =========================================================================
    # CHAPTER 3: USER GUIDE & RUNNING INSTRUCTIONS
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 3: USER GUIDE & RUNNING INSTRUCTIONS")
    add_body_p(doc, "This chapter serves as a comprehensive operational user guide for installing, configuring, compiling, and testing the Resume Engine application in a local offline environment.")

    add_heading_2(doc, "3.1 System Installation & Environment Setup")
    add_body_p(doc, "To establish the development environment, execute the following commands in sequence:")
    add_code_block(doc,
"""# 1. Clone the project repository
git clone https://github.com/Darsh505/resume-engine.git
cd resume-engine

# 2. Initialize the Python virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows PowerShell:
.\\venv\\Scripts\\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# 4. Install all production dependencies and test frameworks
pip install -r requirements.txt""")

    add_body_p(doc, "Personal candidate data is isolated in `data/resume.yaml`. If this file does not exist, the engine seamlessly utilizes `data/resume.example.yaml` as an initial template.")

    add_heading_2(doc, "3.2 Command-Line Interface (CLI) Execution Workflow")
    add_body_p(doc, "The main CLI entrypoint is `compile_resume.py`. It provides several execution flags:")

    # Table 3.1
    t3_1 = doc.add_table(rows=1, cols=3)
    t3_1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3_1, "607080", "4")
    for idx, text in enumerate(["COMMAND SYNTAX", "ACTION PERFORMED", "TYPICAL OUTPUT"]):
        c = t3_1.rows[0].cells[idx]
        set_cell_background(c, "003366")
        p = c.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)
        
    cli_data = [
        ("python compile_resume.py --list-targets", "Enumerates all discovered target role tags in the YAML source", "backend, frontend, devops, data-science"),
        ("python compile_resume.py --targets-report", "Generates an audit matrix showing bullet and skill counts per role", "Formatted tabular summary table in terminal"),
        ("python compile_resume.py --target backend", "Filters and compiles a PDF tailored for backend engineering", "output/resume_backend.pdf + Git commit"),
        ("python compile_resume.py --target devops", "Filters and compiles a PDF tailored for DevOps engineering", "output/resume_devops.pdf + Git commit"),
        ("python compile_resume.py --target frontend --preview", "Compiles PDF and launches system viewer automatically", "Launches default PDF reader on host machine")
    ]
    for cmd, act, outp in cli_data:
        row = t3_1.add_row()
        for idx, text in enumerate([cmd, act, outp]):
            cell = row.cells[idx]
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    p_t31 = doc.add_paragraph()
    p_t31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t31.paragraph_format.space_after = Pt(8)
    r = p_t31.add_run("Table 3.1: CLI Compilation Commands and Flag Reference")
    r.bold = True
    r.font.size = Pt(10)

    add_heading_2(doc, "3.3 Web Management Interface & Resume Studio")
    add_body_p(doc, "For visual editing, users can launch the interactive web studio:")
    add_code_block(doc,
"""# Start the local web studio
python run_web.py

# Expected Terminal Output:
# INFO:     Started server process [PID]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)""")

    add_body_p(doc, "Open `http://127.0.0.1:8000` in any web browser. The interface allows modifying experience, skills, and projects in a structured form. Clicking 'Save Changes' validates the inputs through Pydantic and updates `data/resume.yaml`. Clicking 'Generate PDF' compiles and streams the tailored resume directly to the browser.")

    add_heading_2(doc, "3.4 Automated Testing & Quality Verification")
    add_body_p(doc, "System correctness is verified using Pytest. Run the test suite from the repository root:")
    add_code_block(doc,
"""pytest

# Test Suite Output:
# ============================= test session starts =============================
# platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
# rootdir: A:\\projects\\resume-engine
# collected 42 items
# tests\\test_filter_engine.py ..........................................   [100%]
# ============================== 42 passed in 0.08s ==============================""")

    add_body_p(doc, "All 42 test cases pass cleanly, confirming that filtering rules, tag matching, priority ordering, and budget caps operate flawlessly.")

    add_heading_2(doc, "3.5 System Verification & Screen Representations")
    add_body_p(doc, "Figure 3.1 illustrates the clean CLI compilation feedback with Colorama terminal styling, and Figure 3.2 illustrates the live local web studio:")

    add_code_block(doc,
"""+-----------------------------------------------------------------------+
|                    CLI RESUME COMPILATION SESSION                     |
+-----------------------------------------------------------------------+
| > python compile_resume.py --target backend                           |
|                                                                       |
| [1/3] Filtering resume data for target: backend                       |
|   Jobs: 3  |  Bullets: 9  |  Projects: 3  |  Skills: 18               |
|                                                                       |
| [2/3] Rendering PDF -> ./output/resume_backend.pdf                    |
| [SUCCESS] PDF written to: ./output/resume_backend.pdf                 |
|                                                                       |
| [3/3] Git integration                                                 |
| [GIT] Committed: chore: regenerate resume for backend                 |
|                                                                       |
| [SUCCESS] Done! Resume for 'backend' -> ./output/resume_backend.pdf   |
+-----------------------------------------------------------------------+""")

    p_f31 = doc.add_paragraph()
    p_f31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f31.paragraph_format.space_after = Pt(8)
    r = p_f31.add_run("Figure 3.1: CLI Compilation Output with Colorama Visual Steps")
    r.bold = True
    r.font.size = Pt(10)

    # =========================================================================
    # CHAPTER 4: CONCLUSION & FUTURE SCOPE
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "CHAPTER 4: CONCLUSION & FUTURE SCOPE")

    add_heading_2(doc, "4.1 Conclusion")
    add_body_p(doc, "The Six Weeks Summer Industrial Training at Mits Academy provided comprehensive practical immersion into professional software engineering paradigms, automated document compilation, and type-safe Python systems architecture.")
    add_body_p(doc, "The resulting application, Resume Engine, successfully solves the long-standing industry problems of resume drift and manual ATS tailoring. By establishing a unified YAML Single Source of Truth coupled with intelligent tag-based filtering, priority ranking, and strict page budget caps, candidates can generate professionally typeset, role-tailored single-page PDF resumes deterministically in under 250 milliseconds.")
    add_body_p(doc, "The project highlights include 100% offline operation, zero cloud subscription costs, privacy-preserving local storage, automated Git audit histories, a responsive local web interface, and an exhaustive 42-item automated test suite.")

    add_heading_2(doc, "4.2 Future Scope")
    add_body_p(doc, "Future enhancements planned for subsequent iterations of Resume Engine include:")
    add_body_p(doc, "1. Natural Language Job Description Matcher: Integrating a local offline Large Language Model (e.g. LLaMA-3 or Mistral via llama.cpp) to analyze target job descriptions and automatically suggest optimal tag allocations.")
    add_body_p(doc, "2. Alternate Output Backends: Developing a secondary LaTeX compilation backend alongside ReportLab for academic CV formatting.")
    add_body_p(doc, "3. Containerized Headless CLI: Packaging the CLI into a lightweight Docker image for seamless integration into enterprise continuous integration / continuous deployment (CI/CD) pipelines.")
    add_body_p(doc, "4. Interactive Visual Drag-and-Drop: Adding drag-and-drop section reordering to the local web interface.")

    # =========================================================================
    # REFERENCES & BIBLIOGRAPHY
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "REFERENCES & BIBLIOGRAPHY")
    
    refs = [
        "1. ReportLab Inc., \"ReportLab PDF Generation User Guide (Version 5.0)\", ReportLab Documentation, 2024. Available: https://www.reportlab.com/docs/reportlab-userguide.pdf",
        "2. Ramirez, S., \"FastAPI: Modern, High-Performance Web Framework for Python\", O'Reilly Media, 2023.",
        "3. Ben-Kiki, O., Evans, C., and Net, I., \"YAML Ain't Markup Language (YAML) Version 1.2 Specification\", YAML.org, 2021. Available: https://yaml.org/spec/1.2/",
        "4. Van Rossum, G., Warsaw, B., and Coghlan, N., \"PEP 8: Style Guide for Python Code\", Python Software Foundation, 2021. Available: https://peps.python.org/pep-0008/",
        "5. Colomiets, I., \"Pydantic: Data Validation Using Python Type Hints\", Pydantic Documentation, 2024. Available: https://docs.pydantic.dev/",
        "6. Chacon, S. and Straub, B., \"Pro Git: Everything you need to know about Git\", 2nd ed., Apress, 2014.",
        "7. Krekel, H. et al., \"pytest: Simple powerful testing with Python\", Pytest Documentation, 2024. Available: https://docs.pytest.org/",
        "8. Rayat Bahra Institute of Engineering & Nanotechnology, \"Guidelines for Industrial Training Report Submission (4th Semester)\", Department of Computer Science & Engineering, Hoshiarpur, 2026."
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.4)
        r = p.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)

    out_file = "Darshveer_Singh_2449377_Industrial_Training_Report.docx"
    doc.save(out_file)
    print(f"Successfully generated {out_file}")

if __name__ == "__main__":
    build_report()
