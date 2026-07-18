"""
pdf_renderer.py — ReportLab-based multi-page PDF resume renderer.

Design tokens
─────────────
  Accent color  : #1A3C6E  (deep navy)
  Body text     : #1F2937  (near-black)
  Muted text    : #6B7280  (grey)
  Rule color    : #1A3C6E
  Fonts         : Helvetica family (built-in, no external files needed)
  Page size     : Letter (8.5 × 11 in)
  Margins       : 0.60 in left/right, 0.50 in top/bottom

Multi-page
──────────
Content that overflows a page automatically continues on the next page
via Canvas.showPage().  The renderer never silently truncates — a long
resume produces two pages rather than a silently shorter one.

Overflow is handled by the single ``_check_or_new_page()`` method on
``Renderer``, which replaces the four copy-pasted ``try/except`` blocks
that previously existed in every section method.
"""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

# ─── Design tokens ────────────────────────────────────────────────────────────
ACCENT      = colors.HexColor("#1A3C6E")   # deep navy — name, section titles, accent rule
BODY_COLOR  = colors.HexColor("#1F2937")   # near-black — body text
MUTED_COLOR = colors.HexColor("#6B7280")   # grey — dates, contact info, tech stack
RULE_COLOR  = colors.HexColor("#1A3C6E")   # matches ACCENT

PAGE_W, PAGE_H  = LETTER            # 612 × 792 pts
MARGIN_X        = 0.60 * inch       # left & right          (was 0.55)
MARGIN_Y_TOP    = 0.50 * inch       # top margin            (was 0.45)
MARGIN_Y_BOTTOM = 0.50 * inch       # bottom margin         (was 0.45)

CONTENT_W = PAGE_W - 2 * MARGIN_X
LEFT      = MARGIN_X
RIGHT     = PAGE_W - MARGIN_X
BOTTOM_Y  = MARGIN_Y_BOTTOM         # y below which content must not be drawn

# ── Typography ────────────────────────────────────────────────────────────────
FS_NAME      = 22      # candidate name in header
FS_CONTACT   = 8.5    # contact line beneath name
FS_SECTION   = 11.5   # section titles            (was 10.5 — +1pt for clearer hierarchy)
FS_JOB_TITLE = 10     # company / project name    (was  9.5 — creates a visible tier)
FS_BODY      = 9      # body text, bullets        (was  8.5 — more readable)
FS_BULLET    = 9      # bullet text               (was  8.5 — matches body)
FS_SKILLS    = 9      # skill list                (was  8.5 — matches body)

# ── Spacing ───────────────────────────────────────────────────────────────────
# All values are in ReportLab points (1 pt = 1/72 in).
#
# LEADING          : vertical distance from one text baseline to the next.
#                    1.45× is standard for professional body copy; 1.35× felt cramped.
# SECTION_PRE_GAP  : blank space inserted ABOVE each section header, so sections
#                    breathe away from the preceding content.  This is what creates
#                    the visible inter-section gap.
# RULE_TO_CONTENT  : distance from the section-rule line to the first content row.
#                    Large enough that content ascenders clear the rule.
# ENTRY_GAP        : space appended after each item (job, project, achievement)
#                    within a section.  Was hard-coded as 3 — named and bumped to 5.
# BULLET_INDENT    : horizontal offset of the bullet glyph from LEFT.
# BULLET_HANG      : additional indent for wrapped bullet-continuation lines, creating
#                    a hanging-indent effect.  Was the magic number 6, now named.

LEADING         = FS_BODY * 1.45    # ≈ 13.05 pt   (was FS_BODY * 1.35 ≈ 11.48 pt)
SECTION_PRE_GAP = 10                # pts above section header  (replaces part of SECTION_GAP)
RULE_TO_CONTENT = 10                # pts below rule to content (replaces rest of SECTION_GAP)
ENTRY_GAP       = 5                 # pts between entries       (was hard-coded 3)
BULLET_INDENT   = 12                # pts bullet offset from LEFT  (was 10)
BULLET_HANG     = 8                 # hanging-indent for wrapped bullet lines (was magic 6)
BULLET_CHAR     = "▸ "


# ─── Text wrapping ────────────────────────────────────────────────────────────

def _wrap_text(text: str, canvas: Canvas, font: str, size: float, max_w: float) -> list[str]:
    """Word-wrap *text* to fit within *max_w* points.  Returns list of lines."""
    canvas.setFont(font, size)
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if canvas.stringWidth(test, font, size) <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ─── Renderer ─────────────────────────────────────────────────────────────────

class Renderer:
    """
    Stateful renderer that tracks the Y cursor across one or more pages.

    Coordinate system (ReportLab convention)
    ─────────────────────────────────────────
    • Origin (0, 0) is the bottom-left of the page.
    • ``y`` increases upward; ``PAGE_H`` is the top of the page.
    • ``self.y`` starts near the top and *decreases* as content is drawn.
    • ``_move(dy)`` advances the cursor *down* by ``dy`` points.

    Multi-page
    ──────────
    ``_check_or_new_page(needed)`` is the single, canonical overflow gate.
    Every section method calls it before drawing a block; if there is not
    enough vertical room, it calls ``_new_page()`` which invokes
    ``Canvas.showPage()`` and resets the cursor to the top of the fresh page.
    No content is ever silently dropped.
    """

    def __init__(self, canvas: Canvas) -> None:
        self.c = canvas
        self.y = PAGE_H - MARGIN_Y_TOP
        self._page_num: int = 1

    # ── page helpers ──────────────────────────────────────────────────────────

    def _move(self, dy: float) -> None:
        """Advance the cursor *down* by *dy* points."""
        self.y -= dy

    def _new_page(self) -> None:
        """
        Finalize the current page and begin a fresh one.

        After this call ``self.y`` is reset to the top of the new page, so
        all subsequent drawing calls work identically to page 1 — no caller
        needs to detect or react to the page boundary.

        A subtle page-number label ("Page N") is drawn in the top-right
        corner of continuation pages (page 2 onward), using the top-margin
        area so it does not consume any content space.
        """
        self.c.showPage()
        self._page_num += 1
        self.y = PAGE_H - MARGIN_Y_TOP

        # Draw page number in the top margin of continuation pages only.
        # Drawn AFTER self.y is reset, using the top-margin area above self.y.
        self.c.setFont("Helvetica", 7)
        self.c.setFillColor(MUTED_COLOR)
        self.c.drawRightString(RIGHT, PAGE_H - MARGIN_Y_TOP / 2, f"Page {self._page_num}")

    def _check_or_new_page(self, needed: float) -> None:
        """
        Ensure *needed* vertical points are available below the cursor.

        This is the single replacement for the four copy-pasted
        ``try/except _OverflowWarning`` blocks that previously existed in
        every section method.  Instead of raising an exception and silently
        aborting the section, we simply start a new page and continue.

        Args:
            needed: height in points of the block about to be drawn.
        """
        if self.y - needed < BOTTOM_Y:
            self._new_page()

    # ── section header ────────────────────────────────────────────────────────

    def section_header(self, title: str) -> None:
        """
        Draw a bold all-caps section title with a full-width rule beneath it.

        Layout (top to bottom):
          SECTION_PRE_GAP   — blank breathing space above (inter-section gap)
          title text        — Helvetica-Bold, FS_SECTION, in ACCENT colour
          FS_SECTION + 2 pts gap to rule
          rule line         — 0.75 pt stroke in RULE_COLOR
          RULE_TO_CONTENT   — space before first content row
        """
        # Total height consumed before any content is drawn.
        # +2 for the gap between title baseline and rule; +1 for rule thickness.
        needed = SECTION_PRE_GAP + FS_SECTION + 2 + 1 + RULE_TO_CONTENT
        self._check_or_new_page(needed)

        self._move(SECTION_PRE_GAP)

        self.c.setFont("Helvetica-Bold", FS_SECTION)
        self.c.setFillColor(ACCENT)
        self.c.drawString(LEFT, self.y, title.upper())
        # Move cursor from the title baseline to just below the text so the rule
        # sits snugly beneath the letters.  FS_SECTION accounts for the full
        # cap-height; +2 adds a small clearance below the baseline.
        # (The original code used FS_SECTION + 1, placing the rule one full
        # text-height below the baseline, which left an unnecessarily large gap.)
        self._move(FS_SECTION + 2)

        self.c.setStrokeColor(RULE_COLOR)
        self.c.setLineWidth(0.75)   # was 1 pt — slightly lighter for a refined look
        self.c.line(LEFT, self.y, RIGHT, self.y)
        self._move(RULE_TO_CONTENT)

    # ── name / contact header ─────────────────────────────────────────────────

    def name_block(self, personal: dict[str, Any]) -> None:
        """Draw the candidate name, contact line, and header divider."""
        name     = personal.get("name", "")
        email    = personal.get("email", "")
        phone    = personal.get("phone", "")
        linkedin = personal.get("linkedin", "")
        github   = personal.get("github", "")
        website  = personal.get("website", "")

        # Name — large, centred, accent colour
        self.c.setFont("Helvetica-Bold", FS_NAME)
        self.c.setFillColor(ACCENT)
        self.c.drawCentredString(PAGE_W / 2, self.y, name)
        self._move(FS_NAME + 4)

        # Contact line — all parts joined by bullets, centred, muted
        separator    = "  •  "
        parts        = [p for p in [email, phone, linkedin, github, website] if p]
        contact_line = separator.join(parts)
        self.c.setFont("Helvetica", FS_CONTACT)
        self.c.setFillColor(MUTED_COLOR)
        self.c.drawCentredString(PAGE_W / 2, self.y, contact_line)
        self._move(FS_CONTACT + 7)

        # Divider — heavier accent stroke marking end of the header block
        self.c.setStrokeColor(ACCENT)
        self.c.setLineWidth(1.5)
        self.c.line(LEFT, self.y, RIGHT, self.y)
        self._move(4)

    # ── education ─────────────────────────────────────────────────────────────

    def education_section(self, entries: list[dict]) -> None:
        """
        Draw the Education section.

        Degree entries are always included (the filter_engine guarantees this).
        Only the coursework list within each entry is filtered/budgeted.
        """
        if not entries:
            return
        self.section_header("Education")

        for entry in entries:
            institution = entry.get("institution", "")
            degree      = entry.get("degree", "")
            dates       = entry.get("dates", "")
            gpa         = entry.get("gpa", "")
            coursework  = entry.get("coursework", [])

            self._check_or_new_page(FS_JOB_TITLE + LEADING + 2)

            # Institution (bold, left) + dates (muted, right) on the same baseline
            self.c.setFont("Helvetica-Bold", FS_JOB_TITLE)
            self.c.setFillColor(BODY_COLOR)
            self.c.drawString(LEFT, self.y, institution)
            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(MUTED_COLOR)
            self.c.drawRightString(RIGHT, self.y, dates)
            self._move(FS_JOB_TITLE + 2)

            # Degree (italic) with optional GPA
            self.c.setFont("Helvetica-Oblique", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            deg_gpa = degree + (f"  —  GPA: {gpa}" if gpa else "")
            self.c.drawString(LEFT, self.y, deg_gpa)
            self._move(LEADING)

            # Relevant coursework — word-wrapped, muted colour
            if coursework:
                course_names = ", ".join(c["name"] for c in coursework)
                course_line  = f"Relevant Coursework: {course_names}"
                lines = _wrap_text(course_line, self.c, "Helvetica", FS_BODY, CONTENT_W)
                self._check_or_new_page(len(lines) * LEADING)
                self.c.setFont("Helvetica", FS_BODY)
                self.c.setFillColor(MUTED_COLOR)
                for line in lines:
                    self.c.drawString(LEFT, self.y, line)
                    self._move(LEADING)

            self._move(ENTRY_GAP)

    # ── experience ────────────────────────────────────────────────────────────

    def experience_section(self, jobs: list[dict]) -> None:
        """
        Draw the Experience section.

        Each job entry renders its header (company + dates, role + location)
        followed by indented bullet points.  The company header and at least
        one line of content are kept together on the same page.
        """
        if not jobs:
            return
        self.section_header("Experience")

        for job in jobs:
            company  = job.get("company", "")
            role     = job.get("role", "")
            dates    = job.get("dates", "")
            location = job.get("location", "")
            bullets  = job.get("bullets", [])

            # Require room for the header row plus at least one content line so
            # we never produce an orphaned company name at the bottom of a page.
            self._check_or_new_page(FS_JOB_TITLE + LEADING * 2)

            # Company (bold, left) + dates (muted, right) on the same baseline
            self.c.setFont("Helvetica-Bold", FS_JOB_TITLE)
            self.c.setFillColor(BODY_COLOR)
            self.c.drawString(LEFT, self.y, company)
            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(MUTED_COLOR)
            self.c.drawRightString(RIGHT, self.y, dates)
            self._move(FS_JOB_TITLE + 2)

            # Role (italic, body colour) + optional location (same line)
            self.c.setFont("Helvetica-Oblique", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            role_loc = role + (f"  ·  {location}" if location else "")
            self.c.drawString(LEFT, self.y, role_loc)
            self._move(LEADING + 2)

            # Bullet points — hanging indent on wrapped lines
            bullet_x = LEFT + BULLET_INDENT
            bullet_w = CONTENT_W - BULLET_INDENT
            for bullet in bullets:
                text  = bullet.get("text", "") if isinstance(bullet, dict) else str(bullet)
                lines = _wrap_text(BULLET_CHAR + text, self.c, "Helvetica", FS_BULLET, bullet_w)
                self._check_or_new_page(len(lines) * LEADING)
                self.c.setFont("Helvetica", FS_BULLET)
                self.c.setFillColor(BODY_COLOR)
                first = True
                for line in lines:
                    # First line: full BULLET_INDENT from LEFT.
                    # Continuation lines: further indented by BULLET_HANG to
                    # create a hanging-indent that aligns text past the bullet glyph.
                    x = bullet_x if first else bullet_x + BULLET_HANG
                    self.c.drawString(x, self.y, line)
                    self._move(LEADING)
                    first = False

            self._move(ENTRY_GAP)

    # ── projects ─────────────────────────────────────────────────────────────

    def projects_section(self, projects: list[dict]) -> None:
        """Draw the Projects section."""
        if not projects:
            return
        self.section_header("Projects")

        for proj in projects:
            name   = proj.get("name", "")
            desc   = proj.get("description", "")
            tech   = proj.get("tech", [])
            github = proj.get("github", "")

            self._check_or_new_page(FS_JOB_TITLE + LEADING * 2)

            # Project name (bold, accent colour) + optional GitHub URL (muted, right)
            self.c.setFont("Helvetica-Bold", FS_JOB_TITLE)
            self.c.setFillColor(ACCENT)
            self.c.drawString(LEFT, self.y, name)
            if github:
                self.c.setFont("Helvetica", FS_BODY - 0.5)
                self.c.setFillColor(MUTED_COLOR)
                self.c.drawRightString(RIGHT, self.y, github)
            self._move(FS_JOB_TITLE + 2)

            # Tech stack (italic, muted, slightly smaller than body)
            if tech:
                tech_str = "Tech: " + ", ".join(tech)
                self.c.setFont("Helvetica-Oblique", FS_BODY - 0.5)
                self.c.setFillColor(MUTED_COLOR)
                self.c.drawString(LEFT, self.y, tech_str)
                self._move(LEADING)

            # Description — word-wrapped body text
            lines = _wrap_text(desc, self.c, "Helvetica", FS_BODY, CONTENT_W)
            self._check_or_new_page(len(lines) * LEADING)
            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            for line in lines:
                self.c.drawString(LEFT, self.y, line)
                self._move(LEADING)

            self._move(ENTRY_GAP)

    # ── skills ────────────────────────────────────────────────────────────────

    def skills_section(self, skills: dict[str, list[str]]) -> None:
        """
        Draw the Skills section.

        Each category renders as a single run:
          **Category:** skill1, skill2, skill3, …

        The category label is bold; the skill list is regular weight.
        Long lines wrap; continuation lines are indented 4 pts.
        """
        if not skills:
            return
        self.section_header("Skills")

        for category, names in skills.items():
            line_text = f"{category.capitalize()}: " + ", ".join(names)
            lines = _wrap_text(line_text, self.c, "Helvetica", FS_SKILLS, CONTENT_W)
            self._check_or_new_page(len(lines) * LEADING)

            for i, line in enumerate(lines):
                if i == 0:
                    # First line: bold label through ":", then regular text for skills.
                    # This is a two-pass draw: measure bold label width, draw it, then
                    # draw the rest starting immediately after.
                    colon_idx = line.find(":")
                    if colon_idx != -1:
                        label   = line[: colon_idx + 1]
                        rest    = line[colon_idx + 1 :]
                        label_w = self.c.stringWidth(label, "Helvetica-Bold", FS_SKILLS)
                        self.c.setFont("Helvetica-Bold", FS_SKILLS)
                        self.c.setFillColor(BODY_COLOR)
                        self.c.drawString(LEFT, self.y, label)
                        self.c.setFont("Helvetica", FS_SKILLS)
                        self.c.drawString(LEFT + label_w, self.y, rest)
                    else:
                        self.c.setFont("Helvetica", FS_SKILLS)
                        self.c.setFillColor(BODY_COLOR)
                        self.c.drawString(LEFT, self.y, line)
                else:
                    # Continuation lines — slight indent
                    self.c.setFont("Helvetica", FS_SKILLS)
                    self.c.setFillColor(BODY_COLOR)
                    self.c.drawString(LEFT + 4, self.y, line)
                self._move(LEADING)

        self._move(ENTRY_GAP)

    # ── achievements ──────────────────────────────────────────────────────────

    def achievements_section(self, achievements: list[dict]) -> None:
        """Draw the Achievements & Certifications section."""
        if not achievements:
            return
        self.section_header("Achievements & Certifications")

        for ach in achievements:
            title  = ach.get("title", "")
            issuer = ach.get("issuer", "")
            date   = ach.get("date", "")

            lines = _wrap_text(
                f"{BULLET_CHAR}{title}",
                self.c, "Helvetica", FS_BODY,
                CONTENT_W - BULLET_INDENT,
            )
            self._check_or_new_page(len(lines) * LEADING)

            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            for i, line in enumerate(lines):
                x = LEFT + BULLET_INDENT if i == 0 else LEFT + BULLET_INDENT + BULLET_HANG
                self.c.drawString(x, self.y, line)
                self._move(LEADING)

            if issuer or date:
                meta = "  ".join(filter(None, [issuer, date]))
                self.c.setFont("Helvetica-Oblique", FS_BODY - 0.5)
                self.c.setFillColor(MUTED_COLOR)
                self.c.drawString(LEFT + BULLET_INDENT + BULLET_HANG, self.y, meta)
                self._move(LEADING)


# ─── Public entry point ───────────────────────────────────────────────────────

def render_pdf(resume_data: dict[str, Any], output_path: str) -> None:
    """
    Render a PDF resume from *resume_data* and write it to *output_path*.

    Content that does not fit on a single Letter page automatically
    continues on subsequent pages — the renderer never silently truncates.

    *resume_data* is expected to come from ``filter_engine.build_resume_data()``.
    The ``render_pdf`` signature is unchanged from the previous version.
    """
    import os
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    c = Canvas(output_path, pagesize=LETTER)
    c.setTitle(f"Resume — {resume_data.get('personal', {}).get('name', 'Unknown')}")

    r = Renderer(c)
    r.name_block(resume_data.get("personal", {}))
    r.education_section(resume_data.get("education", []))
    r.experience_section(resume_data.get("experience", []))
    r.projects_section(resume_data.get("projects", []))
    r.skills_section(resume_data.get("skills", {}))
    r.achievements_section(resume_data.get("achievements", []))

    c.save()
