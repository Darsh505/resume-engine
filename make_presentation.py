"""
Script to generate Darshveer_Singh_2449377_Viva_Presentation.pptx
Adheres strictly to the user-provided "School days" palette & academic requirements:
- Canvas: Warm Ivory / Cream (#F7F4EC)
- Sage Green: #9FB8A6
- Terracotta / Rust: #D47A5B
- Mustard / Sand: #E5BE6C
- Deep Charcoal / Espresso: #2B2421
- Pure White Cards: #FFFFFF
- 16:9 Widescreen (13.333" x 7.5")
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ─── Color Palette ────────────────────────────────────────────────────────────
C_BG          = RGBColor(247, 244, 236)   # #F7F4EC Warm Ivory
C_SAGE        = RGBColor(159, 184, 166)   # #9FB8A6 Soft Sage Green
C_TERRACOTTA  = RGBColor(212, 122, 91)    # #D47A5B Warm Rust / Terracotta
C_MUSTARD     = RGBColor(229, 190, 108)   # #E5BE6C Sand / Mustard
C_DARK        = RGBColor(43, 36, 33)      # #2B2421 Deep Charcoal / Espresso
C_MUTED       = RGBColor(105, 95, 90)     # Muted text
C_WHITE       = RGBColor(255, 255, 255)   # Clean White

FONT_SERIF = "Georgia"
FONT_SANS  = "Calibri"

def add_run_to_p(p, text, font_name=FONT_SANS, size_pt=10, bold=False, color=C_DARK):
    r = p.add_run()
    r.text = text
    r.font.name = font_name
    r.font.size = Pt(size_pt)
    r.font.bold = bold
    r.font.color.rgb = color
    return r

def add_slide_bg(slide):
    """Fill slide with warm ivory canvas."""
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_BG
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, title_text, category_text="RESUME ENGINE - VIVA DEFENSE"):
    """Standardized academic presentation header with category badge."""
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.04))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_TERRACOTTA
    top_bar.line.fill.background()

    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(8.0), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.name = FONT_SANS
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = C_TERRACOTTA

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.733), Inches(0.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_SERIF
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = C_DARK

def add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_SAGE):
    """Add a structured card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
    else:
        card.line.fill.background()
    return card

def add_organic_accents(slide):
    """Add subtle organic shapes inspired by the 'School days' theme."""
    pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(11.8), Inches(-0.5), Inches(2.2), Inches(2.2))
    pill.fill.solid()
    pill.fill.fore_color.rgb = C_SAGE
    pill.line.fill.background()

    accent = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(12.3), Inches(6.3), Inches(1.5), Inches(1.5))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_MUSTARD
    accent.line.fill.background()

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s1)

    # Decorative organic shapes on the right (inspired by user screenshot)
    wave_panel = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(0), Inches(4.333), Inches(7.5))
    wave_panel.fill.solid()
    wave_panel.fill.fore_color.rgb = C_SAGE
    wave_panel.line.fill.background()

    star = s1.shapes.add_shape(MSO_SHAPE.STAR_8_POINT, Inches(9.8), Inches(1.2), Inches(2.2), Inches(2.2))
    star.fill.solid()
    star.fill.fore_color.rgb = C_TERRACOTTA
    star.line.fill.background()

    pebble = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.2), Inches(4.2), Inches(2.2), Inches(2.4))
    pebble.fill.solid()
    pebble.fill.fore_color.rgb = C_MUSTARD
    pebble.line.fill.background()

    pill_t = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(3.8), Inches(0.35))
    pill_t.fill.solid()
    pill_t.fill.fore_color.rgb = C_TERRACOTTA
    pill_t.line.fill.background()
    p_run = pill_t.text_frame.paragraphs[0]
    p_run.text = "SIX WEEKS INDUSTRIAL TRAINING DEFENSE"
    p_run.font.name = FONT_SANS
    p_run.font.size = Pt(9.5)
    p_run.font.bold = True
    p_run.font.color.rgb = C_WHITE
    p_run.alignment = PP_ALIGN.CENTER

    tbox = s1.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(8.0), Inches(2.6))
    tf = tbox.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Resume Engine"
    p1.font.name = FONT_SERIF
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = C_DARK

    p2 = tf.add_paragraph()
    p2.text = "Git-Driven Tag-Based Resume Compilation & Local Management System"
    p2.font.name = FONT_SERIF
    p2.font.size = Pt(17)
    p2.font.color.rgb = C_TERRACOTTA

    add_card(s1, 0.8, 4.2, 7.8, 2.5, bg_color=C_WHITE, border_color=C_SAGE)
    mbox = s1.shapes.add_textbox(Inches(1.0), Inches(4.3), Inches(7.4), Inches(2.3))
    mtf = mbox.text_frame
    mtf.word_wrap = True

    lines = [
        ("Candidate Name:", "Darshveer Singh"),
        ("University Roll No:", "2449377"),
        ("Degree & Branch:", "B.Tech Computer Science & Engineering (AI & ML)"),
        ("Institution:", "Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur"),
        ("Training Organisation:", "Mits Academy | Mentor: Srishti (Technical Lead)"),
        ("Technical Domain:", "Systems Programming, Document Automation & Offline Local Web")
    ]
    for i, (k, v) in enumerate(lines):
        p = mtf.paragraphs[0] if i == 0 else mtf.add_paragraph()
        p.space_after = Pt(3)
        add_run_to_p(p, f"{k} ", FONT_SANS, 10, bold=True, color=C_DARK)
        add_run_to_p(p, v, FONT_SANS, 10, bold=False, color=C_MUTED)

    # =========================================================================
    # SLIDE 2: Industrial Training Overview
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s2)
    add_organic_accents(s2)
    add_header(s2, "Industrial Training Overview & Institutional Context")

    cards_data_s2 = [
        ("Mits Academy", "Corporate Training Environment", [
            "Organization: Mits Academy",
            "Duration: 8 June 2026 to 28 July 2026",
            "Tenure: 45 Calendar Days (37 Working Days)",
            "Primary Mentor: Srishti (Technical Lead)",
            "Focus: Production Python, Document Automation & ATS Optimization"
        ], C_SAGE),
        ("Academic Alignment", "Rayat Bahra Institute (RBIENT)", [
            "Candidate: Darshveer Singh (Roll No: 2449377)",
            "Branch: B.Tech CSE (AI & ML)",
            "Semester: 4th Semester Industrial Training",
            "Curriculum: Hands-on Software Engineering",
            "Outcome: Independent Production-Grade Artifact"
        ], C_TERRACOTTA),
        ("Core Competencies", "Key Technical Areas Mastered", [
            "Modern Python 3.14 with strict type annotations",
            "ReportLab 5.0 canvas math and PDF bytecode",
            "Asynchronous web engineering with FastAPI",
            "Automated testing with Pytest (42 test suite)",
            "Git version control and automated commit hooks"
        ], C_MUSTARD)
    ]
    for idx, (title, sub, bullets, border_col) in enumerate(cards_data_s2):
        left = 0.8 + idx * 4.0
        add_card(s2, left, 1.8, 3.733, 5.0, C_WHITE, border_col)
        cbox = s2.shapes.add_textbox(Inches(left + 0.2), Inches(2.0), Inches(3.333), Inches(4.6))
        ctf = cbox.text_frame
        ctf.word_wrap = True
        
        p = ctf.paragraphs[0]
        p.text = title
        p.font.name = FONT_SERIF
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = C_DARK

        p_sub = ctf.add_paragraph()
        p_sub.text = sub
        p_sub.font.name = FONT_SANS
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = border_col
        p_sub.space_after = Pt(14)

        for b in bullets:
            pb = ctf.add_paragraph()
            pb.space_after = Pt(6)
            add_run_to_p(pb, f"- {b}", FONT_SANS, 10.5, color=C_DARK)

    # =========================================================================
    # SLIDE 3: Problem Statement
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s3)
    add_organic_accents(s3)
    add_header(s3, "Problem Statement: Challenges in Modern Resume Tailoring")

    add_card(s3, 0.8, 1.8, 5.7, 5.0, C_WHITE, C_TERRACOTTA)
    lbox = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    ltf = lbox.text_frame
    ltf.word_wrap = True
    
    p = ltf.paragraphs[0]
    p.text = "Key Industry Challenges"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TERRACOTTA
    p.space_after = Pt(12)

    problems = [
        ("1. Resume Drift Across Disconnected Files", "Job seekers create separate Word/PDF documents for backend, devops, and data science roles. Updates in one file fail to sync, causing date and credential mismatches."),
        ("2. ATS Rejection & Keyword Mismatch", "Applicant Tracking Systems scan for specific role keywords. Generic resumes fail threshold scores, while manual tailoring takes 30-45 minutes per job application."),
        ("3. Accidental Page Overflow", "Manual edits push single-page resumes onto an awkward second page with just 2-3 lines, violating the gold-standard 1-page recruiting guideline.")
    ]
    for title, desc in problems:
        pt = ltf.add_paragraph()
        add_run_to_p(pt, title, FONT_SANS, 11, bold=True, color=C_DARK)
        pd = ltf.add_paragraph()
        pd.space_after = Pt(8)
        add_run_to_p(pd, desc, FONT_SANS, 10, color=C_MUTED)

    add_card(s3, 6.8, 1.8, 5.7, 5.0, C_WHITE, C_SAGE)
    rbox = s3.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    rtf = rbox.text_frame
    rtf.word_wrap = True

    p = rtf.paragraphs[0]
    p.text = "Operational Inefficiencies"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_SAGE
    p.space_after = Pt(12)

    stats = [
        ("75% of Resumes", "Discarded automatically by enterprise ATS algorithms before reaching human recruiters due to layout and keyword issues."),
        ("30+ Minutes Wasted", "Average time spent manually formatting, deleting bullets, and re-exporting PDFs for each distinct job submission."),
        ("Version Sprawl", "Candidates typically accumulate 10-15 disjointed files (e.g. 'Resume_v2_final_final.pdf') with zero version tracking.")
    ]
    for stat, explanation in stats:
        pt = rtf.add_paragraph()
        add_run_to_p(pt, stat, FONT_SANS, 12, bold=True, color=C_DARK)
        pe = rtf.add_paragraph()
        pe.space_after = Pt(10)
        add_run_to_p(pe, explanation, FONT_SANS, 10, color=C_MUTED)

    # =========================================================================
    # SLIDE 4: Proposed Solution
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s4)
    add_organic_accents(s4)
    add_header(s4, "Proposed Solution: The Resume Engine Paradigm")

    cards_data_s4 = [
        ("Single Source of Truth", "Centralized YAML", [
            "Store all experiences, projects, skills, and honors in one structured YAML file (data/resume.yaml).",
            "Eliminate multi-file divergence and copy-paste errors completely."
        ], C_SAGE),
        ("Tag-Based Filtering", "Dynamic Extraction", [
            "Tag any bullet point, project, or skill with role identifiers (backend, devops, frontend, data-science).",
            "Engine selectively extracts only the items relevant to the requested role."
        ], C_TERRACOTTA),
        ("Deterministic Budget Caps", "Guaranteed 1-Page", [
            "Mathematical constraints enforce exact section budgets (max 4 bullets/job, 3 projects, 4 achievements).",
            "Output is guaranteed to fit exactly on a single page."
        ], C_MUSTARD),
        ("Local Dual Interface", "Fast CLI + Local Web", [
            "CLI tool for rapid terminal batch compilation with automated Git commits.",
            "FastAPI local web studio at http://127.0.0.1:8000 for visual editing."
        ], C_DARK)
    ]
    for idx, (title, sub, bullets, col) in enumerate(cards_data_s4):
        left = 0.8 + idx * 2.98
        add_card(s4, left, 1.8, 2.8, 5.0, C_WHITE, col)
        box = s4.shapes.add_textbox(Inches(left + 0.15), Inches(2.0), Inches(2.5), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_SERIF
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col

        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.name = FONT_SANS
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = C_MUTED
        p_sub.space_after = Pt(10)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.space_after = Pt(8)
            add_run_to_p(pb, f"- {b}", FONT_SANS, 10, color=C_DARK)

    # =========================================================================
    # SLIDE 5: Architecture & Data Flow
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s5)
    add_organic_accents(s5)
    add_header(s5, "System Architecture: Decoupled Multi-Layer Pipeline")

    layers = [
        ("Layer 1: Data Storage", "web/data_store.py", "Safely reads data/resume.yaml. Automatically falls back to data/resume.example.yaml. Single choke-point for all disk operations.", C_SAGE),
        ("Layer 2: Filter Engine", "filter_engine.py", "Pure Python logic. Matches role tags, calculates priority scores, and enforces mathematical budget limits without touching UI code.", C_TERRACOTTA),
        ("Layer 3: PDF Renderer", "pdf_renderer.py", "ReportLab 5.0 canvas engine. Computes typography, leading, dividers, and coordinates within strict 792pt vertical page boundaries.", C_MUSTARD),
        ("Layer 4: Dual Interface", "CLI & FastAPI Web", "CLI (compile_resume.py) with Colorama & Git integration + Local Web Studio (web/app.py) running on http://127.0.0.1:8000.", C_DARK)
    ]
    for idx, (title, file_name, desc, col) in enumerate(layers):
        top = 1.8 + idx * 1.25
        add_card(s5, 0.8, top, 11.733, 1.1, C_WHITE, col)
        
        box = s5.shapes.add_textbox(Inches(1.0), Inches(top + 0.1), Inches(11.3), Inches(0.9))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        add_run_to_p(p, f"{title} ", FONT_SERIF, 14, bold=True, color=col)
        add_run_to_p(p, f"[{file_name}]\n", FONT_SANS, 10, bold=True, color=C_MUTED)
        add_run_to_p(p, desc, FONT_SANS, 10.5, color=C_DARK)

    # =========================================================================
    # SLIDE 6: Tag Matching & Priority Scoring
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s6)
    add_organic_accents(s6)
    add_header(s6, "Core Filter Engine: Tag Matching & Priority Scoring")

    add_card(s6, 0.8, 1.8, 5.7, 5.0, C_WHITE, C_SAGE)
    lbox = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    ltf = lbox.text_frame
    ltf.word_wrap = True
    
    p = ltf.paragraphs[0]
    p.text = "Tag Filtering Logic"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_SAGE
    p.space_after = Pt(10)

    t_bullets = [
        "Explicit Role Tagging: Items carry tags such as 'backend', 'frontend', 'devops', 'data-science'.",
        "Universal 'general' Tag: Universal items carry the 'general' tag, ensuring they appear across all target resumes.",
        "Role Isolation: Role-specific accomplishments are excluded from unrelated targets, maximizing ATS relevance score.",
        "Zero Content Mutation: All operations occur on in-memory dictionary clones, preserving the master YAML file."
    ]
    for b in t_bullets:
        pb = ltf.add_paragraph()
        pb.space_after = Pt(8)
        add_run_to_p(pb, f"- {b}", FONT_SANS, 10.5, color=C_DARK)

    add_card(s6, 6.8, 1.8, 5.7, 5.0, C_WHITE, C_TERRACOTTA)
    rbox = s6.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    rtf = rbox.text_frame
    rtf.word_wrap = True

    p = rtf.paragraphs[0]
    p.text = "Priority Ranking Engine"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TERRACOTTA
    p.space_after = Pt(10)

    p_bullets = [
        "Integer Priority Field: Any bullet or project can have an optional 'priority: int' attribute (e.g. 10, 20, 50).",
        "Stable Sorting: Items are ordered descending by priority, bubbling high-impact achievements to the top.",
        "Deterministic Tie-Breaking: When priority values are equal, chronological and original document order is preserved.",
        "Dynamic Relevance: Allows repositioning of high-value metrics based on current recruitment campaign focus."
    ]
    for b in p_bullets:
        pb = rtf.add_paragraph()
        pb.space_after = Pt(8)
        add_run_to_p(pb, f"- {b}", FONT_SANS, 10.5, color=C_DARK)

    # =========================================================================
    # SLIDE 7: Page Budget Algorithm
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s7)
    add_organic_accents(s7)
    add_header(s7, "Page Budget Enforcement: Mathematical 1-Page Guarantee")

    budgets = [
        ("Experience Bullets", "Max 4 Bullets / Role", "Prevents lengthy bullet sprawl for older positions. Focuses recruiter attention on key quantifiable achievements.", C_SAGE),
        ("Technical Projects", "Max 3 Top Projects", "Limits projects section to the three most relevant implementations matching the target role.", C_TERRACOTTA),
        ("Key Achievements", "Max 4 Honors", "Extracts top 4 competition awards, scholarships, or leadership honors based on priority score.", C_MUSTARD),
        ("Relevant Coursework", "Max 6 Course Items", "Caps university coursework entries in education to preserve vertical breathing room.", C_DARK)
    ]
    for idx, (sec_title, limit_str, rationale, col) in enumerate(budgets):
        left = 0.8 + idx * 2.98
        add_card(s7, left, 1.8, 2.8, 5.0, C_WHITE, col)
        box = s7.shapes.add_textbox(Inches(left + 0.15), Inches(2.0), Inches(2.5), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = sec_title
        p.font.name = FONT_SERIF
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col

        p_lim = tf.add_paragraph()
        p_lim.text = limit_str
        p_lim.font.name = FONT_SANS
        p_lim.font.size = Pt(11)
        p_lim.font.bold = True
        p_lim.font.color.rgb = C_TERRACOTTA
        p_lim.space_after = Pt(12)

        p_rat = tf.add_paragraph()
        add_run_to_p(p_rat, rationale, FONT_SANS, 10.5, color=C_DARK)

    # =========================================================================
    # SLIDE 8: ReportLab PDF Compilation Pipeline
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s8)
    add_organic_accents(s8)
    add_header(s8, "ReportLab Typesetting Engine: Canvas Primitives & Math")

    add_card(s8, 0.8, 1.8, 5.7, 5.0, C_WHITE, C_SAGE)
    lbox = s8.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    ltf = lbox.text_frame
    ltf.word_wrap = True
    
    p = ltf.paragraphs[0]
    p.text = "Vector Rendering Pipeline"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_SAGE
    p.space_after = Pt(10)

    rl_features = [
        "Native PDF Bytecode: Direct vector rendering without browser overhead, chromium processes, or Node.js dependencies.",
        "Execution Latency < 250ms: Extremely lightweight rendering cycle suitable for instant web preview and high-throughput compilation.",
        "Standardized Coordinate Geometry: Base canvas height of 792 points (11-inch Letter) with 36pt margins (0.5 inch).",
        "Embedded ISO 32000-1 Metadata: Automated document title, author (Darshveer Singh), and creation timestamp for ATS readers."
    ]
    for f in rl_features:
        pb = ltf.add_paragraph()
        pb.space_after = Pt(8)
        add_run_to_p(pb, f"- {f}", FONT_SANS, 10.5, color=C_DARK)

    add_card(s8, 6.8, 1.8, 5.7, 5.0, C_WHITE, C_MUSTARD)
    rbox = s8.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    rtf = rbox.text_frame
    rtf.word_wrap = True

    p = rtf.paragraphs[0]
    p.text = "Typographic Architecture"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_DARK
    p.space_after = Pt(10)

    typo_features = [
        "Font Hierarchy: Standardized Helvetica and Helvetica-Bold scale (Header: 16pt, Subhead: 11pt, Body: 9.5pt).",
        "Dynamic Leading Calculation: Proportional vertical spacing prevents line collisions while maximizing density.",
        "Custom Section Dividers: Precise 0.5pt vector separator lines with custom RGB palette accents.",
        "Two-Column Skill Grids: Automatic layout computation for skill categories and coursework entries."
    ]
    for f in typo_features:
        pb = rtf.add_paragraph()
        pb.space_after = Pt(8)
        add_run_to_p(pb, f"- {f}", FONT_SANS, 10.5, color=C_DARK)

    # =========================================================================
    # SLIDE 9: Local Web Management Studio
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s9)
    add_organic_accents(s9)
    add_header(s9, "Local Web Studio: Interactive Browser-Based Management")

    web_cards = [
        ("FastAPI Backend", "Asynchronous HTTP", [
            "Mounted at http://127.0.0.1:8000 on local loopback interface.",
            "Complete data privacy with zero external transmission.",
            "REST endpoints for loading, validating, and saving data."
        ], C_SAGE),
        ("Jinja2 Form Editor", "Server-Side Templates", [
            "Structured forms for editing experience, projects, and skills.",
            "Dynamic client-side addition and removal of bullet items.",
            "Live validation feedback directly in the browser window."
        ], C_TERRACOTTA),
        ("One-Click PDF Generator", "Streaming Response", [
            "Role dropdown allows selecting target role (backend, frontend, etc.).",
            "Streams compiled PDF binary directly to the browser for instant preview and download.",
            "Zero temporary file accumulation on disk."
        ], C_MUSTARD)
    ]
    for idx, (title, sub, bullets, col) in enumerate(web_cards):
        left = 0.8 + idx * 4.0
        add_card(s9, left, 1.8, 3.733, 5.0, C_WHITE, col)
        box = s9.shapes.add_textbox(Inches(left + 0.2), Inches(2.0), Inches(3.333), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_SERIF
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col

        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.name = FONT_SANS
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = C_MUTED
        p_sub.space_after = Pt(12)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.space_after = Pt(8)
            add_run_to_p(pb, f"- {b}", FONT_SANS, 10.5, color=C_DARK)

    # =========================================================================
    # SLIDE 10: Automated Testing & Validation
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s10)
    add_organic_accents(s10)
    add_header(s10, "Quality Assurance: 42 Automated Pytest Unit Tests")

    add_card(s10, 0.8, 1.8, 5.7, 5.0, C_WHITE, C_SAGE)
    lbox = s10.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    ltf = lbox.text_frame
    ltf.word_wrap = True
    
    p = ltf.paragraphs[0]
    p.text = "Pytest Execution Results"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_SAGE
    p.space_after = Pt(10)

    test_bullets = [
        "100% Test Pass Rate: All 42 automated test cases pass in under 0.10s.",
        "Filter Engine Suite: Tests tag matching, role isolation, and universal fallback rules.",
        "Budget Cap Suite: Verifies truncation logic for experience bullets, projects, and honors.",
        "Priority Sorting Suite: Confirms integer priority ranking and stable secondary sorting.",
        "Edge Case Verification: Validates handling of missing fields, empty arrays, and special characters."
    ]
    for b in test_bullets:
        pb = ltf.add_paragraph()
        pb.space_after = Pt(8)
        add_run_to_p(pb, f"- {b}", FONT_SANS, 10.5, color=C_DARK)

    add_card(s10, 6.8, 1.8, 5.7, 5.0, C_WHITE, C_DARK)
    rbox = s10.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    rtf = rbox.text_frame
    rtf.word_wrap = True

    p = rtf.paragraphs[0]
    p.text = "Terminal Test Verification"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_MUSTARD
    p.space_after = Pt(10)

    p_cmd = rtf.add_paragraph()
    add_run_to_p(p_cmd, "$ pytest tests/test_filter_engine.py\n\n", "Consolas", 10, color=C_WHITE)

    r_out = rtf.add_paragraph()
    out_txt = (
        "platform win32 -- Python 3.14.7, pytest-9.1.1\n"
        "rootdir: A:\\projects\\resume-engine\n"
        "collected 42 items\n\n"
        "tests/test_filter_engine.py ......................... [100%]\n\n"
        "================ 42 passed in 0.08s ================\n"
    )
    add_run_to_p(r_out, out_txt, "Consolas", 9.5, color=RGBColor(160, 230, 160))

    # =========================================================================
    # SLIDE 11: Local Verification Workflow
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s11)
    add_organic_accents(s11)
    add_header(s11, "Local Execution Profile: Offline-First Operation")

    add_card(s11, 0.8, 1.8, 11.733, 5.0, C_WHITE, C_TERRACOTTA)
    box = s11.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.6))
    tf = box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Operational Workflow Summary"
    p.font.name = FONT_SERIF
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TERRACOTTA
    p.space_after = Pt(12)

    exec_steps = [
        ("1. CLI Compilation", "python compile_resume.py --target backend", "Extracts backend items, renders output/resume_backend.pdf, and auto-commits to Git in 150ms."),
        ("2. Role Audit Matrix", "python compile_resume.py --targets-report", "Prints a comprehensive terminal matrix showing bullet counts and skill allocations per target role."),
        ("3. Local Web Server", "python run_web.py", "Starts the Uvicorn web server at http://127.0.0.1:8000 for browser-based interactive editing."),
        ("4. Automated Unit Testing", "pytest", "Executes the 42 unit test cases to verify logic integrity before committing new features.")
    ]
    for step, cmd, desc in exec_steps:
        pb = tf.add_paragraph()
        add_run_to_p(pb, f"{step}: ", FONT_SANS, 11, bold=True, color=C_DARK)
        add_run_to_p(pb, f"`{cmd}`\n", "Consolas", 10.5, color=C_TERRACOTTA)
        add_run_to_p(pb, f"   {desc}\n", FONT_SANS, 10, color=C_MUTED)

    # =========================================================================
    # SLIDE 12: Engineering Challenges
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s12)
    add_organic_accents(s12)
    add_header(s12, "Engineering Challenges & Resolved Technical Issues")

    challenges = [
        ("Windows Console UTF-8 Encoding", "UnicodeEncodeError: 'charmap'", "Windows command prompts default to cp1252, causing crashes when printing arrows and status symbols.", "Reconfigured sys.stdout and sys.stderr with UTF-8 encoding streams in compile_resume.py.", C_TERRACOTTA),
        ("ReportLab Canvas Boundary Limits", "Accidental Multi-Page Overflow", "Unchecked paragraph expansions pushed text across the 792pt page height boundary.", "Implemented mathematical section budgets and strict line height reservation algorithms.", C_SAGE),
        ("Data Store Seam Architecture", "Hardcoded File Path Coupling", "Scattered open() calls would make future database transitions difficult.", "Created web/data_store.py as a centralized choke-point with graceful fallback to demo data.", C_MUSTARD)
    ]
    for idx, (title, symptom, root_cause, solution, col) in enumerate(challenges):
        left = 0.8 + idx * 4.0
        add_card(s12, left, 1.8, 3.733, 5.0, C_WHITE, col)
        box = s12.shapes.add_textbox(Inches(left + 0.2), Inches(2.0), Inches(3.333), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_SERIF
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(8)

        items = [
            ("Symptom", symptom),
            ("Root Cause", root_cause),
            ("Resolved By", solution)
        ]
        for label, val in items:
            p_lbl = tf.add_paragraph()
            add_run_to_p(p_lbl, f"{label}:", FONT_SANS, 10, bold=True, color=C_DARK)
            p_val = tf.add_paragraph()
            p_val.space_after = Pt(6)
            add_run_to_p(p_val, val, FONT_SANS, 9.5, color=C_MUTED)

    # =========================================================================
    # SLIDE 13: Learning Outcomes
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s13)
    add_organic_accents(s13)
    add_header(s13, "Learning Outcomes & Industrial Competencies Acquired")

    outcomes = [
        ("Production Python Engineering", "Mastered PEP 484 type annotations, Pydantic v2 schemas, and pathlib file operations.", C_SAGE),
        ("Document Automation & PDF Math", "Gained deep expertise in ReportLab PostScript coordinates, typographic leading, and PDF bytecode.", C_TERRACOTTA),
        ("Asynchronous Web Development", "Developed and deployed local FastAPI/Uvicorn applications with server-side Jinja2 form integration.", C_MUSTARD),
        ("Automated Quality Assurance", "Wrote comprehensive Pytest test suites achieving 100% test pass rate across all system modules.", C_DARK),
        ("ATS Recruitment Architecture", "Understood enterprise resume filtering algorithms, keyword density strategies, and recruiter heuristics.", C_SAGE)
    ]
    for idx, (title, desc, col) in enumerate(outcomes):
        top = 1.8 + idx * 1.0
        add_card(s13, 0.8, top, 11.733, 0.88, C_WHITE, col)
        
        box = s13.shapes.add_textbox(Inches(1.0), Inches(top + 0.08), Inches(11.3), Inches(0.72))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        add_run_to_p(p, f"{title}: ", FONT_SERIF, 13, bold=True, color=col)
        add_run_to_p(p, desc, FONT_SANS, 10.5, color=C_DARK)

    # =========================================================================
    # SLIDE 14: Conclusion & Thank You
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_slide_bg(s14)

    wave_panel14 = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(0), Inches(4.333), Inches(7.5))
    wave_panel14.fill.solid()
    wave_panel14.fill.fore_color.rgb = C_SAGE
    wave_panel14.line.fill.background()

    star14 = s14.shapes.add_shape(MSO_SHAPE.STAR_8_POINT, Inches(9.8), Inches(1.2), Inches(2.2), Inches(2.2))
    star14.fill.solid()
    star14.fill.fore_color.rgb = C_TERRACOTTA
    star14.line.fill.background()

    pebble14 = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.2), Inches(4.2), Inches(2.2), Inches(2.4))
    pebble14.fill.solid()
    pebble14.fill.fore_color.rgb = C_MUSTARD
    pebble14.line.fill.background()

    box14 = s14.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(8.0), Inches(2.0))
    tf14 = box14.text_frame
    tf14.word_wrap = True
    
    p = tf14.paragraphs[0]
    p.text = "Thank You"
    p.font.name = FONT_SERIF
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = C_DARK

    p_sub = tf14.add_paragraph()
    p_sub.text = "Resume Engine Project Defense | Questions & Answers"
    p_sub.font.name = FONT_SERIF
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = C_TERRACOTTA

    add_card(s14, 0.8, 3.6, 7.8, 3.2, C_WHITE, C_SAGE)
    mbox14 = s14.shapes.add_textbox(Inches(1.0), Inches(3.8), Inches(7.4), Inches(2.8))
    mtf14 = mbox14.text_frame
    mtf14.word_wrap = True

    cand_lines = [
        ("Candidate Name:", "Darshveer Singh"),
        ("University Roll Number:", "2449377"),
        ("Degree & Branch:", "B.Tech Computer Science & Engineering (AI & ML)"),
        ("Institution:", "Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur"),
        ("Training Organisation:", "Mits Academy | Mentor: Srishti"),
        ("GitHub Repository:", "https://github.com/Darsh505/resume-engine"),
        ("Local Host Endpoint:", "http://127.0.0.1:8000 (Offline-First Architecture)")
    ]
    for i, (k, v) in enumerate(cand_lines):
        p = mtf14.paragraphs[0] if i == 0 else mtf14.add_paragraph()
        p.space_after = Pt(4)
        add_run_to_p(p, f"{k} ", FONT_SANS, 10, bold=True, color=C_DARK)
        add_run_to_p(p, v, FONT_SANS, 10, bold=False, color=C_TERRACOTTA if "http" in v else C_MUTED)

    out_file = "Darshveer_Singh_2449377_Viva_Presentation.pptx"
    prs.save(out_file)
    print(f"Successfully generated {out_file}")

if __name__ == "__main__":
    build_presentation()
