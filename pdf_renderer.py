"""
pdf_renderer.py — ReportLab-based single-page PDF resume renderer.

Design tokens
─────────────
  Accent color  : #1A3C6E  (deep navy)
  Body text     : #1F2937  (near-black)
  Muted text    : #6B7280  (grey)
  Rule color    : #1A3C6E
  Fonts         : Helvetica family (built-in, no external files needed)
  Page size     : Letter (8.5 × 11 in)
  Margins       : 0.55 in left/right, 0.45 in top/bottom
"""

from __future__ import annotations

import sys
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

# ─── Design tokens ────────────────────────────────────────────────────────────
ACCENT        = colors.HexColor("#1A3C6E")
BODY_COLOR    = colors.HexColor("#1F2937")
MUTED_COLOR   = colors.HexColor("#6B7280")
RULE_COLOR    = colors.HexColor("#1A3C6E")
BG_COLOR      = colors.white

PAGE_W, PAGE_H = LETTER   # 612 × 792 pts
MARGIN_X  = 0.55 * inch   # left & right
MARGIN_Y_TOP    = 0.45 * inch
MARGIN_Y_BOTTOM = 0.45 * inch

CONTENT_W = PAGE_W - 2 * MARGIN_X
LEFT      = MARGIN_X
RIGHT     = PAGE_W - MARGIN_X
BOTTOM_Y  = MARGIN_Y_BOTTOM   # minimum Y before overflow warning

# Font sizes
FS_NAME      = 22
FS_CONTACT   = 8.5
FS_SECTION   = 10.5
FS_JOB_TITLE = 9.5
FS_BODY      = 8.5
FS_BULLET    = 8.5
FS_SKILLS    = 8.5

LEADING      = FS_BODY * 1.35   # line height for body text
SECTION_GAP  = 7                # pts between sections
BULLET_INDENT = 10              # pts bullet indent from left
BULLET_CHAR  = "▸ "


# ─── Overflow guard ───────────────────────────────────────────────────────────
class _OverflowWarning(Exception):
    """Raised (and caught) when content would exceed the page bottom."""


def _warn(msg: str) -> None:
    """Print a yellow warning to stderr."""
    # colorama-style ANSI fallback if colorama not available
    try:
        from colorama import Fore, Style
        print(f"{Fore.YELLOW}[WARNING] {msg}{Style.RESET_ALL}", file=sys.stderr)
    except ImportError:
        print(f"[WARNING] {msg}", file=sys.stderr)


# ─── Text wrapping helpers ────────────────────────────────────────────────────

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


def _text_height(lines: int, leading: float) -> float:
    return lines * leading


# ─── Drawing primitives ───────────────────────────────────────────────────────

class Renderer:
    """Stateful renderer that tracks the current Y cursor and raises on overflow."""

    def __init__(self, canvas: Canvas) -> None:
        self.c = canvas
        self.y = PAGE_H - MARGIN_Y_TOP   # start at top
        self._overflow_triggered = False

    # ── cursor helpers ────────────────────────────────────────────────────────

    def _check(self, needed: float) -> None:
        """Raise _OverflowWarning if there isn't enough vertical room."""
        if self.y - needed < BOTTOM_Y:
            raise _OverflowWarning(f"Need {needed:.1f}pt, only {self.y - BOTTOM_Y:.1f}pt left")

    def _move(self, dy: float) -> None:
        self.y -= dy

    # ── section header ────────────────────────────────────────────────────────

    def section_header(self, title: str) -> None:
        """Draws a bold section title + a full-width colored rule below it."""
        needed = FS_SECTION + 4 + SECTION_GAP
        self._check(needed)

        self.c.setFont("Helvetica-Bold", FS_SECTION)
        self.c.setFillColor(ACCENT)
        self.c.drawString(LEFT, self.y, title.upper())
        self._move(FS_SECTION + 1)

        # Rule
        self.c.setStrokeColor(RULE_COLOR)
        self.c.setLineWidth(1)
        self.c.line(LEFT, self.y, RIGHT, self.y)
        self._move(SECTION_GAP - 1)

    # ── name / contact header ─────────────────────────────────────────────────

    def name_block(self, personal: dict[str, Any]) -> None:
        name    = personal.get("name", "")
        email   = personal.get("email", "")
        phone   = personal.get("phone", "")
        linkedin = personal.get("linkedin", "")
        github  = personal.get("github", "")
        website = personal.get("website", "")

        # Name
        self.c.setFont("Helvetica-Bold", FS_NAME)
        self.c.setFillColor(ACCENT)
        self.c.drawCentredString(PAGE_W / 2, self.y, name)
        self._move(FS_NAME + 3)

        # Contact line
        separator = "  •  "
        parts = [p for p in [email, phone, linkedin, github, website] if p]
        contact_line = separator.join(parts)
        self.c.setFont("Helvetica", FS_CONTACT)
        self.c.setFillColor(MUTED_COLOR)
        self.c.drawCentredString(PAGE_W / 2, self.y, contact_line)
        self._move(FS_CONTACT + 8)

        # Divider
        self.c.setStrokeColor(ACCENT)
        self.c.setLineWidth(1.5)
        self.c.line(LEFT, self.y, RIGHT, self.y)
        self._move(9)

    # ── education ─────────────────────────────────────────────────────────────

    def education_section(self, entries: list[dict]) -> None:
        if not entries:
            return
        self.section_header("Education")

        for entry in entries:
            institution = entry.get("institution", "")
            degree      = entry.get("degree", "")
            dates       = entry.get("dates", "")
            gpa         = entry.get("gpa", "")
            coursework  = entry.get("coursework", [])

            # Institution (bold) + dates (right-aligned)
            needed = FS_JOB_TITLE + LEADING + 2
            self._check(needed)

            self.c.setFont("Helvetica-Bold", FS_JOB_TITLE)
            self.c.setFillColor(BODY_COLOR)
            self.c.drawString(LEFT, self.y, institution)
            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(MUTED_COLOR)
            self.c.drawRightString(RIGHT, self.y, dates)
            self._move(FS_JOB_TITLE + 1)

            # Degree + GPA
            self.c.setFont("Helvetica-Oblique", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            deg_gpa = f"{degree}" + (f"  —  GPA: {gpa}" if gpa else "")
            self.c.drawString(LEFT, self.y, deg_gpa)
            self._move(LEADING)

            # Relevant coursework
            if coursework:
                course_names = ", ".join(c["name"] for c in coursework)
                course_line = f"Relevant Coursework: {course_names}"
                lines = _wrap_text(course_line, self.c, "Helvetica", FS_BODY, CONTENT_W)
                self._check(len(lines) * LEADING)
                self.c.setFont("Helvetica", FS_BODY)
                self.c.setFillColor(MUTED_COLOR)
                for line in lines:
                    self.c.drawString(LEFT, self.y, line)
                    self._move(LEADING)

            self._move(3)

    # ── experience ────────────────────────────────────────────────────────────

    def experience_section(self, jobs: list[dict]) -> None:
        if not jobs:
            return
        self.section_header("Experience")

        for job in jobs:
            company  = job.get("company", "")
            role     = job.get("role", "")
            dates    = job.get("dates", "")
            location = job.get("location", "")
            bullets  = job.get("bullets", [])

            needed = FS_JOB_TITLE + LEADING + 2
            self._check(needed)

            # Company (bold) + dates (right)
            self.c.setFont("Helvetica-Bold", FS_JOB_TITLE)
            self.c.setFillColor(BODY_COLOR)
            self.c.drawString(LEFT, self.y, company)
            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(MUTED_COLOR)
            self.c.drawRightString(RIGHT, self.y, dates)
            self._move(FS_JOB_TITLE + 1)

            # Role + location
            self.c.setFont("Helvetica-Oblique", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            role_loc = f"{role}" + (f"  ·  {location}" if location else "")
            self.c.drawString(LEFT, self.y, role_loc)
            self._move(LEADING + 1)

            # Bullets
            bullet_x = LEFT + BULLET_INDENT
            bullet_w = CONTENT_W - BULLET_INDENT
            for bullet in bullets:
                text = bullet.get("text", "") if isinstance(bullet, dict) else str(bullet)
                lines = _wrap_text(BULLET_CHAR + text, self.c, "Helvetica", FS_BULLET, bullet_w)
                try:
                    self._check(len(lines) * LEADING)
                except _OverflowWarning:
                    if not self._overflow_triggered:
                        _warn("Content truncated to fit one page.")
                        self._overflow_triggered = True
                    return
                self.c.setFont("Helvetica", FS_BULLET)
                self.c.setFillColor(BODY_COLOR)
                first = True
                for line in lines:
                    x = bullet_x if first else bullet_x + 6
                    self.c.drawString(x, self.y, line)
                    self._move(LEADING)
                    first = False

            self._move(3)

    # ── projects ─────────────────────────────────────────────────────────────

    def projects_section(self, projects: list[dict]) -> None:
        if not projects:
            return
        self.section_header("Projects")

        for proj in projects:
            name    = proj.get("name", "")
            desc    = proj.get("description", "")
            tech    = proj.get("tech", [])
            github  = proj.get("github", "")

            try:
                self._check(FS_JOB_TITLE + LEADING * 2)
            except _OverflowWarning:
                if not self._overflow_triggered:
                    _warn("Content truncated to fit one page.")
                    self._overflow_triggered = True
                return

            # Name (bold) + github (right)
            self.c.setFont("Helvetica-Bold", FS_JOB_TITLE)
            self.c.setFillColor(ACCENT)
            self.c.drawString(LEFT, self.y, name)
            if github:
                self.c.setFont("Helvetica", FS_BODY - 0.5)
                self.c.setFillColor(MUTED_COLOR)
                self.c.drawRightString(RIGHT, self.y, github)
            self._move(FS_JOB_TITLE + 1)

            # Tech stack (italic)
            if tech:
                tech_str = "Tech: " + ", ".join(tech)
                self.c.setFont("Helvetica-Oblique", FS_BODY - 0.5)
                self.c.setFillColor(MUTED_COLOR)
                self.c.drawString(LEFT, self.y, tech_str)
                self._move(LEADING)

            # Description
            lines = _wrap_text(desc, self.c, "Helvetica", FS_BODY, CONTENT_W)
            try:
                self._check(len(lines) * LEADING)
            except _OverflowWarning:
                if not self._overflow_triggered:
                    _warn("Content truncated to fit one page.")
                    self._overflow_triggered = True
                return
            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            for line in lines:
                self.c.drawString(LEFT, self.y, line)
                self._move(LEADING)

            self._move(3)

    # ── skills ────────────────────────────────────────────────────────────────

    def skills_section(self, skills: dict[str, list[str]]) -> None:
        if not skills:
            return
        self.section_header("Skills")

        for category, names in skills.items():
            line_text = f"{category.capitalize()}: " + ", ".join(names)
            lines = _wrap_text(line_text, self.c, "Helvetica", FS_SKILLS, CONTENT_W)
            try:
                self._check(len(lines) * LEADING)
            except _OverflowWarning:
                if not self._overflow_triggered:
                    _warn("Content truncated to fit one page.")
                    self._overflow_triggered = True
                return

            for i, line in enumerate(lines):
                if i == 0:
                    # Bold the category label
                    colon_idx = line.find(":")
                    if colon_idx != -1:
                        label = line[:colon_idx + 1]
                        rest  = line[colon_idx + 1:]
                        self.c.setFont("Helvetica-Bold", FS_SKILLS)
                        self.c.setFillColor(BODY_COLOR)
                        label_w = self.c.stringWidth(label, "Helvetica-Bold", FS_SKILLS)
                        self.c.drawString(LEFT, self.y, label)
                        self.c.setFont("Helvetica", FS_SKILLS)
                        self.c.setFillColor(BODY_COLOR)
                        self.c.drawString(LEFT + label_w, self.y, rest)
                    else:
                        self.c.setFont("Helvetica", FS_SKILLS)
                        self.c.setFillColor(BODY_COLOR)
                        self.c.drawString(LEFT, self.y, line)
                else:
                    self.c.setFont("Helvetica", FS_SKILLS)
                    self.c.setFillColor(BODY_COLOR)
                    self.c.drawString(LEFT + 4, self.y, line)
                self._move(LEADING)

        self._move(2)

    # ── achievements ──────────────────────────────────────────────────────────

    def achievements_section(self, achievements: list[dict]) -> None:
        if not achievements:
            return
        self.section_header("Achievements & Certifications")

        for ach in achievements:
            title   = ach.get("title", "")
            issuer  = ach.get("issuer", "")
            date    = ach.get("date", "")

            lines = _wrap_text(f"{BULLET_CHAR}{title}", self.c, "Helvetica", FS_BODY, CONTENT_W - BULLET_INDENT)
            try:
                self._check(len(lines) * LEADING)
            except _OverflowWarning:
                if not self._overflow_triggered:
                    _warn("Content truncated to fit one page.")
                    self._overflow_triggered = True
                return

            self.c.setFont("Helvetica", FS_BODY)
            self.c.setFillColor(BODY_COLOR)
            for i, line in enumerate(lines):
                x = LEFT + BULLET_INDENT if i == 0 else LEFT + BULLET_INDENT + 8
                self.c.drawString(x, self.y, line)
                self._move(LEADING)

            if issuer or date:
                meta = "  ".join(filter(None, [issuer, date]))
                self.c.setFont("Helvetica-Oblique", FS_BODY - 0.5)
                self.c.setFillColor(MUTED_COLOR)
                self.c.drawString(LEFT + BULLET_INDENT + 8, self.y, meta)
                self._move(LEADING)


# ─── Public entry point ───────────────────────────────────────────────────────

def render_pdf(resume_data: dict[str, Any], output_path: str) -> None:
    """
    Render a one-page PDF resume from *resume_data* and save it to *output_path*.

    resume_data is expected to come from filter_engine.build_resume_data().
    """
    import os
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    c = Canvas(output_path, pagesize=LETTER)
    c.setTitle(f"Resume — {resume_data.get('personal', {}).get('name', 'Unknown')}")

    r = Renderer(c)

    try:
        r.name_block(resume_data.get("personal", {}))
        r.education_section(resume_data.get("education", []))
        r.experience_section(resume_data.get("experience", []))
        r.projects_section(resume_data.get("projects", []))
        r.skills_section(resume_data.get("skills", {}))
        r.achievements_section(resume_data.get("achievements", []))
    except _OverflowWarning:
        if not r._overflow_triggered:
            _warn("Content truncated to fit one page.")

    c.save()
