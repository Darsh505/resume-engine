"""
Script to generate Darshveer_Singh_2449377_Daily_Training_Diary.docx
Fully compliant with University Guidelines & Mits Academy requirements.
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

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="7F7F7F", sz="4"):
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

def build_diary():
    doc = docx.Document()
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.2)
    section.right_margin = Inches(1.0)
    add_page_border(section)

    # Base style setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x20, 0x20, 0x20)
    normal_style.paragraph_format.line_spacing = 1.3
    normal_style.paragraph_format.space_after = Pt(4)

    # Header & Footer
    header = section.header
    hp = header.paragraphs[0]
    hp.text = "Rayat Bahra Institute of Engineering & Nanotechnology | Daily Training Diary"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.style.font.name = "Times New Roman"
    hp.style.font.size = Pt(8.5)
    hp.style.font.color.rgb = RGBColor(0x70, 0x70, 0x70)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.text = "Student: Darshveer Singh (Roll No: 2449377)       |       Mits Academy"
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.style.font.name = "Times New Roman"
    fp.style.font.size = Pt(8.5)
    fp.style.font.color.rgb = RGBColor(0x70, 0x70, 0x70)

    # Title Block
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = title.add_run("RAYAT BAHRA INSTITUTE OF ENGINEERING & NANOTECHNOLOGY\n")
    r1.bold = True
    r1.font.size = Pt(14)
    r1.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

    r2 = title.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n")
    r2.bold = True
    r2.font.size = Pt(12)

    r3 = title.add_run("DAILY INDUSTRIAL TRAINING DIARY (ACADEMIC SESSION 2026)\n")
    r3.bold = True
    r3.font.size = Pt(13)
    r3.underline = True

    # Metadata Summary Box Table
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, "4A607A", "8")
    
    meta_data = [
        ("Student Name:", "Darshveer Singh"),
        ("University Roll Number:", "2449377"),
        ("Degree & Branch:", "B.Tech Computer Science & Engineering (AI & ML)"),
        ("Training Organisation:", "Mits Academy"),
        ("Training Duration & Mentor:", "8 June 2026 to 28 July 2026 (45 Calendar Days, 37 Working Days) | Mentor: Srishti")
    ]
    for i, (label, val) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.0)
        set_cell_background(c0, "F0F4F8")
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.line_spacing = 1.15
        p0.paragraph_format.space_after = Pt(0)
        r = p0.add_run(label)
        r.bold = True
        r.font.size = Pt(10)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.15
        p1.paragraph_format.space_after = Pt(0)
        r = p1.add_run(val)
        r.font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 37 Working Days Data
    daily_records = [
        {
            "day": 1, "date": "Monday, 8 June 2026",
            "work": "Attended the industrial orientation program at Mits Academy conducted by Mentor Srishti. Received an overview of organizational workflows, corporate coding standards, and project expectations. Set up local development environment with Python 3.14, Git CLI, and workspace directories.",
            "tools": "Python 3.14, Git CLI, Virtualenv, Visual Studio Code, Windows Terminal.",
            "learning": "Understood corporate version control workflows and the necessity of strict virtual environment isolation for professional software engineering."
        },
        {
            "day": 2, "date": "Tuesday, 9 June 2026",
            "work": "Deep dive into advanced Python 3 typing and modern language idioms. Studied type hinting, TypedDict, Generic types, and runtime type checking protocols for building robust offline data processing systems.",
            "tools": "Python Typing Module, Mypy static analyzer, PEP 484 and PEP 563 standards.",
            "learning": "Static type annotations prevent runtime regressions, enforce clean function contracts, and streamline cross-module integration in large Python codebases."
        },
        {
            "day": 3, "date": "Wednesday, 10 June 2026",
            "work": "Configured the primary Git repository for Resume Engine under mentor guidance. Formulated branch protection rules, conventional commit message standards, and multi-platform .gitignore rules to prevent artifact pollution.",
            "tools": "Git, Conventional Commits specification, GitHub remote repository management.",
            "learning": "Structured commit messages and proactive .gitignore strategies maintain clean working trees and enable auditability in agile software teams."
        },
        {
            "day": 4, "date": "Thursday, 11 June 2026",
            "work": "Conducted in-depth domain analysis on resume drift and multi-role tailoring problems. Mapped out technical deficiencies in existing ATS parsers, font rendering inconsistencies, and the manual overhead of maintaining multiple Word files.",
            "tools": "ATS specification benchmarks, Document Object Model analysis, LaTeX comparison studies.",
            "learning": "Identified the core engineering requirement: a unified single source of truth capable of dynamic filtering without destructive copy-pasting."
        },
        {
            "day": 5, "date": "Friday, 12 June 2026",
            "work": "Formulated the system architecture and architectural blueprint for the Resume Engine project. Drafted data flow diagrams, module interaction boundaries, and offline-first runtime requirements under Mentor Srishti.",
            "tools": "System Architecture Modeling, Data Flow Diagrams (DFD Level 0 and Level 1).",
            "learning": "Designing decoupled boundaries between data storage, filtering engines, and presentation renderers ensures long-term testability and maintainability."
        },
        {
            "day": 6, "date": "Monday, 15 June 2026",
            "work": "Engineered the hierarchical YAML data schema for the resume repository. Defined strongly structured models for contact details, summary statements, work experiences, technical projects, skills lists, and education records.",
            "tools": "YAML Specification 1.2, PyYAML parser, Hierarchical Data Modeling.",
            "learning": "Human-readable YAML formats provide a cleaner, more diffable, and less error-prone editing surface than raw JSON or binary formats for resume content."
        },
        {
            "day": 7, "date": "Tuesday, 16 June 2026",
            "work": "Implemented the safe YAML deserialization layer. Programmed error handling routines to gracefully capture indentation errors, unclosed strings, and malformed tags without crashing the host process.",
            "tools": "PyYAML (yaml.safe_load), Python Exception Handling hierarchies, Unicode normalization.",
            "learning": "Always isolate file I/O operations inside resilient choke points to avoid unhandled OS exceptions during user configuration loading."
        },
        {
            "day": 8, "date": "Wednesday, 17 June 2026",
            "work": "Architected web/data_store.py as the unified file system choke-point. Engineered fallback resolution: defaulting to data/resume.yaml if present, with automatic fallback to data/resume.example.yaml.",
            "tools": "Python pathlib.Path, File I/O Streams, Seam Architecture Pattern.",
            "learning": "Decoupling route handlers from hardcoded file system paths makes the application modular and ready for potential future database transitions."
        },
        {
            "day": 9, "date": "Thursday, 18 June 2026",
            "work": "Integrated Pydantic v2 data models for rigorous schema validation. Programmed field-level validators for dates, URL strings, bullet point lists, and mandatory contact fields.",
            "tools": "Pydantic v2, BaseModel, ValidationError, Field constraints.",
            "learning": "Fail-fast validation at runtime guarantees that rendering engines receive strictly conforming data, preventing layout crashes downstream."
        },
        {
            "day": 10, "date": "Friday, 19 June 2026",
            "work": "Constructed the role-based tagging taxonomy. Defined standard target role tags ('backend', 'frontend', 'data-science', 'devops') and established inheritance rules for the universal 'general' tag.",
            "tools": "Taxonomy Classification, Set Theory, Python Set Intersection algorithms.",
            "learning": "A disciplined tagging taxonomy allows a single bullet point or project to serve multiple target roles without content duplication."
        },
        {
            "day": 11, "date": "Monday, 22 June 2026",
            "work": "Commenced development of the core filter engine module (filter_engine.py). Programmed the primary data extraction routines for filtering experience bullets and project entries according to active target tags.",
            "tools": "filter_engine.py, Functional Python, List Comprehensions, Lambda sorting.",
            "learning": "Filtering must operate non-destructively on in-memory copies to keep the master resume dataset pure and immutable."
        },
        {
            "day": 12, "date": "Tuesday, 23 June 2026",
            "work": "Implemented hierarchical tag matching and fallback algorithms. Added logic so that items lacking explicit role tags inherit fallback visibility when relevant, while strictly tagging domain-specific accomplishments.",
            "tools": "Python Algorithm Design, Conditional Predicates, Set Membership Testing.",
            "learning": "Fallback hierarchies ensure that universal accomplishments (such as core education and leadership) are never inadvertently excluded."
        },
        {
            "day": 13, "date": "Wednesday, 24 June 2026",
            "work": "Designed and coded the priority ranking engine. Implemented an integer priority weighting algorithm (`priority: int`) allowing high-impact achievements to dynamically bubble to the top of each section.",
            "tools": "Sorting Algorithms, Python sorted() with custom key functions, Stable Sort semantics.",
            "learning": "Stable sorting with secondary criteria (such as recency or impact factor) guarantees deterministic, repeatable resume compilation."
        },
        {
            "day": 14, "date": "Thursday, 25 June 2026",
            "work": "Engineered the page budget enforcement subsystem. Formulated mathematical caps (maximum 4 bullets per role, 3 projects, 4 key achievements, 6 coursework entries) to preserve single-page layout integrity.",
            "tools": "Constraint Satisfaction Algorithms, Slicing Operations, Resource Budgeting.",
            "learning": "Automated budget truncation prevents layout overflow and eliminates the common student error of submitting multi-page resumes."
        },
        {
            "day": 15, "date": "Friday, 26 June 2026",
            "work": "Conducted extensive edge-case testing on the filter engine. Tested scenarios including empty experience sections, missing tags, single-item lists, and special character strings. Reviewed code with Mentor Srishti.",
            "tools": "Manual Edge Testing, Python unittest assertions, Boundary Value Analysis.",
            "learning": "Graceful degradation when handling incomplete candidate records is vital for commercial-grade document generation tools."
        },
        {
            "day": 16, "date": "Monday, 29 June 2026",
            "work": "Explored the ReportLab 5.0 PDF generation architecture. Investigated low-level canvas primitives, coordinate transformation matrices, typographic point calculations, and color model representations.",
            "tools": "ReportLab 5.0, PDF Specification, PostScript Point coordinate systems.",
            "learning": "PDF drawing operates in bottom-left origin coordinate space, requiring strict mathematical tracking of vertical cursor offsets."
        },
        {
            "day": 17, "date": "Tuesday, 30 June 2026",
            "work": "Constructed the typography subsystem within pdf_renderer.py. Configured core Helvetica fonts, computed typographic leading ratios, and defined standardized header, subheader, and body point scales.",
            "tools": "Typography Mathematics, ReportLab ParagraphStyle, Font Metrics.",
            "learning": "Proportional typographic leading prevents character collision and creates harmonious vertical rhythm in dense single-page documents."
        },
        {
            "day": 18, "date": "Wednesday, 1 July 2026",
            "work": "Engineered custom drawing primitives for section divider rules and geometric layout accents. Programmed functions to draw high-precision 0.5pt separating rules and colored category indicator bars.",
            "tools": "ReportLab Canvas Drawing Methods (line, rect, setStrokeColor, setLineWidth).",
            "learning": "Subtle visual lines guide recruiter visual hierarchy without consuming precious vertical document real estate."
        },
        {
            "day": 19, "date": "Thursday, 2 July 2026",
            "work": "Developed the two-column grid mathematics for skills and education layouts. Calculated exact column widths, gutters, and automatic text wrapping routines for multi-word skill tags.",
            "tools": "Geometric Layout Modeling, Word Wrapping Algorithms, ReportLab Table layouts.",
            "learning": "Grid alignment in programmatic PDF compilation requires explicit column width definitions to prevent text truncation across differing screen resolutions."
        },
        {
            "day": 20, "date": "Friday, 3 July 2026",
            "work": "Programmed the dynamic vertical flow controller in pdf_renderer.py. Implemented vertical coordinate tracking to guarantee that compiled output strictly fits within 792 points (standard 11-inch Letter page height).",
            "tools": "Dynamic Height Accumulation, Page Height Constraints, Boundary Verification.",
            "learning": "Deterministic single-page rendering is achieved by combining section-level item budgets with exact vertical coordinate reservations."
        },
        {
            "day": 21, "date": "Monday, 6 July 2026",
            "work": "Integrated PDF metadata injection. Programmed automated insertion of document properties (Title, Author: Darshveer Singh, Subject, Creator, CreationDate) to enhance ATS indexing compatibility.",
            "tools": "PDF Document Information Dictionary, Metadata Standard ISO 32000-1.",
            "learning": "Clean embedded PDF metadata improves document searchability and parsing scores across corporate applicant tracking systems."
        },
        {
            "day": 22, "date": "Tuesday, 7 July 2026",
            "work": "Implemented the automated Git integration module (git_utils.py). Programmed GitPython hooks to automatically stage, commit, and log newly rendered PDF artifacts upon successful compilation.",
            "tools": "GitPython 3.2, Git Plumbing Commands, Automated Change Tracking.",
            "learning": "Automating artifact versioning creates an immutable historical ledger of every generated resume tailored for prospective employers."
        },
        {
            "day": 23, "date": "Wednesday, 8 July 2026",
            "work": "Developed the CLI command-line interface in compile_resume.py. Built argument parsing for role selection (`--target`), target listing (`--list-targets`), and matrix audit reporting (`--targets-report`).",
            "tools": "Python argparse, Command Line Interface (CLI) Design, Terminal UX.",
            "learning": "Providing informative command-line summaries and inspection reports simplifies batch resume production for technical users."
        },
        {
            "day": 24, "date": "Thursday, 9 July 2026",
            "work": "Investigated and resolved a critical Windows console Unicode encoding bug. Fixed `UnicodeEncodeError: 'charmap'` when printing arrow and bullet characters by reconfiguring sys.stdout and sys.stderr to UTF-8.",
            "tools": "sys.stdout.reconfigure, Python Encoding Subsystem, Windows Code Page 1252.",
            "learning": "Cross-platform Python tools on Windows must explicitly ensure UTF-8 encoding streams to handle international and mathematical characters."
        },
        {
            "day": 25, "date": "Friday, 10 July 2026",
            "work": "Enhanced CLI feedback using Colorama terminal styling. Added colored status banners, compilation step counters ([1/3], [2/3], [3/3]), and itemized bullet summaries. Reviewed progress with Mentor Srishti.",
            "tools": "Colorama 0.4.6, ANSI Escape Sequences, Terminal Status Indicators.",
            "learning": "Clear visual feedback and status indicators drastically enhance developer experience and operational confidence during CLI execution."
        },
        {
            "day": 26, "date": "Monday, 13 July 2026",
            "work": "Commenced development of the local web management interface. Initialized web/app.py using FastAPI, established application lifespan events, and mounted static asset directories for local hosting.",
            "tools": "FastAPI 0.142, Starlette, ASGI Architecture, StaticFiles Mounts.",
            "learning": "FastAPI provides an asynchronous, lightweight foundation for local offline web applications with automatic OpenAPI documentation."
        },
        {
            "day": 27, "date": "Tuesday, 14 July 2026",
            "work": "Constructed the Jinja2 server-side templating engine for the Resume Studio editor. Designed an intuitive split-pane interface with responsive form controls for updating contact details and bullet lists.",
            "tools": "Jinja2 3.1, HTML5 Semantic Forms, CSS Grid and Flexbox Layouts.",
            "learning": "Server-side templating combined with local state enables zero-dependency offline form editing without requiring complex node/npm build chains."
        },
        {
            "day": 28, "date": "Wednesday, 15 July 2026",
            "work": "Engineered the bidirectional data binding pipeline between HTML form posts and the YAML data store. Programmed the POST /save endpoint to validate incoming JSON/form payloads against Pydantic models.",
            "tools": "FastAPI Form Handlers, python-multipart, Pydantic Schema Validation.",
            "learning": "Bidirectional binding ensures that changes made in the web UI immediately persist to disk in clean, human-readable YAML format."
        },
        {
            "day": 29, "date": "Thursday, 16 July 2026",
            "work": "Programmed client-side interactive form behavior in vanilla JavaScript. Implemented dynamic addition and removal of experience bullet points, project cards, and skill chips with real-time DOM updates.",
            "tools": "Vanilla JavaScript (ES6+), DOM Manipulation, Event Delegation, Dynamic Form Arrays.",
            "learning": "Avoiding heavy frontend JavaScript frameworks keeps local utility tools lightning fast, dependency-free, and easy to maintain."
        },
        {
            "day": 30, "date": "Friday, 17 July 2026",
            "work": "Implemented the in-browser resume compilation endpoint (POST /generate). Connected the web controller directly to filter_engine and pdf_renderer to stream compiled PDF binaries directly to the browser.",
            "tools": "FastAPI FileResponse, StreamingResponse, Content-Disposition headers.",
            "learning": "Streaming compiled binaries in-memory allows immediate document preview and download without leaving temporary files on disk."
        },
        {
            "day": 31, "date": "Monday, 20 July 2026",
            "work": "Constructed the convenience web launcher script (run_web.py). Added command-line flags for production-style local serving and `--dev` hot-reload modes using Uvicorn ASGI server.",
            "tools": "Uvicorn 0.54, ASGI Server Lifespan, Localhost Networking (127.0.0.1:8000).",
            "learning": "Providing dedicated runner scripts simplifies application startup for end users without requiring them to memorize complex server commands."
        },
        {
            "day": 32, "date": "Tuesday, 21 July 2026",
            "work": "Conducted comprehensive local security and path validation audits. Verified that all file system read/write operations strictly confine themselves within the repository root, preventing path traversal.",
            "tools": "Path Traversal Security Auditing, pathlib.Path.resolve(), Security Testing.",
            "learning": "Even offline local developer utilities must enforce defensive path checks to ensure data safety and system integrity."
        },
        {
            "day": 33, "date": "Wednesday, 22 July 2026",
            "work": "Special Workshop (Part 1): ATS-Compliant Resume Architecture & Keyword Engineering conducted by Mentor Srishti. Analyzed algorithmic parsing models of modern ATS platforms (Workday, Taleo, Greenhouse). Evaluated font and keyword strategies.",
            "tools": "ATS Parser Simulators, Keyword Extraction Algorithms, Typographic Readability.",
            "learning": "ATS platforms penalize multi-column tables and non-standard symbols; simple linear hierarchies with strong action verbs yield highest scoring."
        },
        {
            "day": 34, "date": "Thursday, 23 July 2026",
            "work": "Special Workshop (Part 2): Role-Targeted Resume Profiling & Technical Interview Preparation. Configured 4 tailored resume profiles (Backend, Frontend, DevOps, Data Science) from a single YAML source; conducted peer resume evaluations.",
            "tools": "Multi-Target Profiling, STAR Method Formulation, Technical Portfolio Presentation.",
            "learning": "Quantifying achievements with specific technical metrics (e.g. latency reductions, test coverage) significantly elevates recruiter engagement."
        },
        {
            "day": 35, "date": "Friday, 24 July 2026",
            "work": "Conducted a rigorous Technical Mock Interview session with Mentor Srishti. Defended system architecture decisions, algorithmic time complexities of filtering routines, and ReportLab memory management under viva conditions.",
            "tools": "Technical Viva Defense, Whiteboard Architecture, Code Walkthrough Protocols.",
            "learning": "Deep understanding of underlying algorithms and design trade-offs is essential for successfully presenting engineering projects."
        },
        {
            "day": 36, "date": "Monday, 27 July 2026",
            "work": "Constructed the automated test suite in tests/test_filter_engine.py. Developed 42 exhaustive unit test cases covering tag matching, priority sorting, section budget capping, and edge cases using Pytest.",
            "tools": "Pytest 9.1, Automated Test Frameworks, Fixtures, Parameterized Testing.",
            "learning": "High unit test coverage provides the ultimate regression safety net, guaranteeing software reliability across diverse data inputs."
        },
        {
            "day": 37, "date": "Tuesday, 28 July 2026",
            "work": "Final project presentation and industrial exit evaluation at Mits Academy. Demonstrated the end-to-end Resume Engine system (CLI compilation, local web studio, and PDF outputs) to Mentor Srishti and the assessment panel.",
            "tools": "Project Demonstration, Evaluation Rubrics, Code Review, Final Documentation Handover.",
            "learning": "Successful software engineering culminates in clear documentation, reproducible testing, and clean delivery to stakeholders."
        }
    ]

    for rec in daily_records:
        t = doc.add_table(rows=4, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t, "A0B0C0", "6")
        
        # Day Header row inside table or title above
        day_p = doc.add_paragraph()
        day_p.paragraph_format.space_before = Pt(6)
        day_p.paragraph_format.space_after = Pt(2)
        run_d = day_p.add_run(f"DAY {rec['day']} : {rec['date'].upper()}")
        run_d.bold = True
        run_d.font.size = Pt(11)
        run_d.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
        
        rows_data = [
            ("Work Done", rec["work"]),
            ("Tools / Concepts", rec["tools"]),
            ("Key Learning", rec["learning"]),
            ("Mentored by", "Mentor Srishti (Technical Lead, Mits Academy)")
        ]
        
        for idx, (label, content) in enumerate(rows_data):
            row = t.rows[idx]
            c0, c1 = row.cells[0], row.cells[1]
            c0.width = Inches(1.8)
            c1.width = Inches(4.4)
            set_cell_background(c0, "F4F6F9" if idx % 2 == 0 else "EAEEF3")
            set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
            set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
            
            p0 = c0.paragraphs[0]
            p0.paragraph_format.line_spacing = 1.15
            p0.paragraph_format.space_after = Pt(0)
            r = p0.add_run(label)
            r.bold = True
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0x1A, 0x2B, 0x4C)
            
            p1 = c1.paragraphs[0]
            p1.paragraph_format.line_spacing = 1.2
            p1.paragraph_format.space_after = Pt(0)
            r = p1.add_run(content)
            r.font.size = Pt(9.5)
            if label == "Mentored by":
                r.bold = True
                r.font.color.rgb = RGBColor(0x00, 0x4D, 0x40)

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Final Declaration Page
    doc.add_page_break()
    dec_title = doc.add_paragraph()
    dec_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    dec_title.paragraph_format.space_before = Pt(30)
    r = dec_title.add_run("STUDENT DECLARATION & VERIFICATION\n")
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
    r.underline = True

    dec_p = doc.add_paragraph()
    dec_p.paragraph_format.line_spacing = 1.5
    dec_p.paragraph_format.space_before = Pt(14)
    dec_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    dec_p.add_run(
        "I hereby solemnly declare that the daily entries, technical summaries, and learning records contained in this Industrial Training Diary represent an authentic and accurate account of the training undertaken by me at Mits Academy from 8 June 2026 to 28 July 2026 under the mentorship of Mentor Srishti. All technical implementations, algorithms, and documentation developed for the Resume Engine project were executed in partial fulfillment of the degree of Bachelor of Technology in Computer Science & Engineering (Artificial Intelligence & Machine Learning) at Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur."
    )

    doc.add_paragraph().paragraph_format.space_before = Pt(20)

    # Signatures Table
    sig_table = doc.add_table(rows=3, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in sig_table.rows:
        r.cells[0].width = Inches(3.1)
        r.cells[1].width = Inches(3.1)
        set_cell_margins(r.cells[0], top=100, bottom=100, left=100, right=100)
        set_cell_margins(r.cells[1], top=100, bottom=100, left=100, right=100)

    p_sig1 = sig_table.rows[0].cells[0].paragraphs[0]
    p_sig1.add_run("Verified and Approved by:\n\n\n\n").font.size = Pt(10)
    r_men = p_sig1.add_run("Mentor Srishti\n")
    r_men.bold = True
    p_sig1.add_run("Technical Lead & Corporate Trainer\nMits Academy")

    p_sig2 = sig_table.rows[0].cells[1].paragraphs[0]
    p_sig2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig2.add_run("Candidate Acknowledgment:\n\n\n\n").font.size = Pt(10)
    r_stu = p_sig2.add_run("Digitally Signed by: Darshveer Singh\n")
    r_stu.bold = True
    p_sig2.add_run("University Roll No: 2449377\nB.Tech CSE (AI & ML)\nRayat Bahra Institute of Engg. & Nano.")

    output_path = "Darshveer_Singh_2449377_Daily_Training_Diary.docx"
    doc.save(output_path)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    build_diary()
