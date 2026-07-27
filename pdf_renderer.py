"""
pdf_renderer.py — Single-page A4 PDF resume renderer with Adaptive Layout Engine.

Design tokens
─────────────
  Accent color  : #1A3C6E  (deep navy)
  Body text     : #1F2937  (near-black)
  Muted text    : #6B7280  (grey)
  Rule color    : #D1D5DB  (light grey — subtle dividers)
  Fonts         : Helvetica family (built-in, no external files needed)
  Page size     : A4 (8.27 × 11.69 in)
  Margins       : 0.45 in left/right, 0.38 in top, 0.32 in bottom

Adaptive Layout Engine
──────────────────────
Two-pass rendering:
  Pass 1 (dry run): Simulate drawing to measure total content height.
  Pass 2 (real):    If content fits, render normally.  If it overflows,
                    progressively tighten spacing through up to 4 compression
                    levels until everything fits, then render for real.

Single-page guarantee
─────────────────────
The renderer NEVER calls Canvas.showPage().  Content that cannot fit even
at maximum compression is clamped at the bottom margin rather than spilling
onto a second page.  The adaptive engine is designed so that typical
resume content always fits at some compression level.

Public API (unchanged)
──────────────────────
  render_pdf(resume_data: dict, output_path: str) -> None
"""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

# ─── Design tokens ────────────────────────────────────────────────────────────
ACCENT      = colors.HexColor("#1A3C6E")   # deep navy — name, section titles
BODY_COLOR  = colors.HexColor("#1F2937")   # near-black — all body text
MUTED_COLOR = colors.HexColor("#6B7280")   # grey — dates, contact, tech stack
RULE_COLOR  = colors.HexColor("#CBD5E1")   # light slate — section dividers
HEADER_RULE = colors.HexColor("#1A3C6E")   # accent — header underline

PAGE_W, PAGE_H = A4                        # 595.28 × 841.89 pts

# ─── Compression levels ───────────────────────────────────────────────────────
# Each level defines the complete set of spacing parameters.
# Level 0 = default comfortable spacing.
# Level 3 = most compact; still professionally readable.

_LEVELS = [
    # level 0 — comfortable
    dict(
        margin_x       = 0.45 * inch,
        margin_top     = 0.38 * inch,
        margin_bottom  = 0.32 * inch,
        fs_name        = 17,
        fs_contact     = 8.5,
        fs_section     = 10.5,
        fs_company     = 9.5,
        fs_role        = 9.0,
        fs_body        = 8.75,
        fs_skills      = 8.75,
        leading_factor = 1.32,
        section_pre    = 7.0,   # pts above each section header
        rule_gap       = 5.5,   # pts below section rule before first content
        entry_gap      = 4.0,   # pts between entries within a section
        bullet_indent  = 10,    # pts from left margin to bullet glyph
        bullet_hang    = 7,     # hanging-indent for wrapped bullet lines
    ),
    # level 1 — slightly tighter
    dict(
        margin_x       = 0.45 * inch,
        margin_top     = 0.35 * inch,
        margin_bottom  = 0.30 * inch,
        fs_name        = 17,
        fs_contact     = 8.5,
        fs_section     = 10.5,
        fs_company     = 9.5,
        fs_role        = 9.0,
        fs_body        = 8.75,
        fs_skills      = 8.75,
        leading_factor = 1.26,
        section_pre    = 5.5,
        rule_gap       = 4.5,
        entry_gap      = 3.0,
        bullet_indent  = 10,
        bullet_hang    = 7,
    ),
    # level 2 — compact
    dict(
        margin_x       = 0.43 * inch,
        margin_top     = 0.32 * inch,
        margin_bottom  = 0.28 * inch,
        fs_name        = 16,
        fs_contact     = 8.5,
        fs_section     = 10.5,
        fs_company     = 9.5,
        fs_role        = 9.0,
        fs_body        = 8.5,
        fs_skills      = 8.5,
        leading_factor = 1.22,
        section_pre    = 4.5,
        rule_gap       = 3.5,
        entry_gap      = 2.5,
        bullet_indent  = 9,
        bullet_hang    = 6,
    ),
    # level 3 — minimal (8.5pt body floor, tight leading)
    dict(
        margin_x       = 0.40 * inch,
        margin_top     = 0.28 * inch,
        margin_bottom  = 0.25 * inch,
        fs_name        = 16,
        fs_contact     = 8.5,
        fs_section     = 10.5,
        fs_company     = 9.5,
        fs_role        = 8.75,
        fs_body        = 8.5,
        fs_skills      = 8.5,
        leading_factor = 1.18,
        section_pre    = 3.5,
        rule_gap       = 3.0,
        entry_gap      = 2.0,
        bullet_indent  = 8,
        bullet_hang    = 5,
    ),
]

BULLET_CHAR = "\u2022 "   # clean round bullet (U+2022), more ATS-friendly than ▸


# ─── Text wrapping ────────────────────────────────────────────────────────────

def _wrap_text(
    text: str,
    canvas: Canvas,
    font: str,
    size: float,
    max_w: float,
) -> list[str]:
    """Word-wrap *text* to fit within *max_w* points. Returns list of lines."""
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
    return lines or [""]


# ─── Renderer ─────────────────────────────────────────────────────────────────

class Renderer:
    """
    Stateful, single-page A4 renderer.

    Coordinate system (ReportLab convention)
    ─────────────────────────────────────────
    Origin (0, 0) is the bottom-left of the page.
    self.y starts near the top and decreases as content is drawn.
    _move(dy) advances the cursor DOWN by dy points.

    Dry-run mode
    ────────────
    When self._dry is True the renderer simulates drawing but writes nothing
    to the canvas.  self.y still moves exactly as in a real render, so the
    final self.y value reflects how much vertical space was consumed.
    """

    def __init__(self, canvas: Canvas, params: dict, dry: bool = False) -> None:
        self.c   = canvas
        self.p   = params
        self._dry = dry

        mx = params["margin_x"]
        mt = params["margin_top"]
        mb = params["margin_bottom"]

        self.LEFT     = mx
        self.RIGHT    = PAGE_W - mx
        self.CONTENT_W = PAGE_W - 2 * mx
        self.BOTTOM_Y  = mb

        self.y = PAGE_H - mt
        self._page_num = 1

    # ── helpers ───────────────────────────────────────────────────────────────

    def _move(self, dy: float) -> None:
        self.y -= dy

    def _leading(self, fs: float | None = None) -> float:
        """Compute leading for a given font size (default: fs_body)."""
        s = fs if fs is not None else self.p["fs_body"]
        return s * self.p["leading_factor"]

    def _draw_string(self, x: float, y: float, text: str) -> None:
        if not self._dry:
            self.c.drawString(x, y, text)

    def _draw_right_string(self, x: float, y: float, text: str) -> None:
        if not self._dry:
            self.c.drawRightString(x, y, text)

    def _draw_centred_string(self, x: float, y: float, text: str) -> None:
        if not self._dry:
            self.c.drawCentredString(x, y, text)

    def _line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        if not self._dry:
            self.c.line(x1, y1, x2, y2)

    def _set_font(self, font: str, size: float) -> None:
        # Always set font even in dry mode so stringWidth works correctly.
        self.c.setFont(font, size)

    def _set_fill(self, color: colors.Color) -> None:
        if not self._dry:
            self.c.setFillColor(color)

    def _set_stroke(self, color: colors.Color) -> None:
        if not self._dry:
            self.c.setStrokeColor(color)

    def _set_line_width(self, w: float) -> None:
        if not self._dry:
            self.c.setLineWidth(w)

    # ── page guard ────────────────────────────────────────────────────────────

    def _will_overflow(self, needed: float) -> bool:
        """Return True if drawing *needed* pts from current y would hit bottom."""
        return self.y - needed < self.BOTTOM_Y

    # ── name / contact header ─────────────────────────────────────────────────

    def name_block(self, personal: dict[str, Any]) -> None:
        """Draw the modern centered header: name, headline, contacts, links."""
        p = self.p
        name     = personal.get("name", "")
        email    = personal.get("email", "")
        phone    = personal.get("phone", "")
        linkedin = personal.get("linkedin", "")
        github   = personal.get("github", "")
        website  = personal.get("website", "")
        headline = personal.get("headline", "")   # optional title line

        # ── Name ──────────────────────────────────────────────────────────────
        self._set_font("Helvetica-Bold", p["fs_name"])
        self._set_fill(BODY_COLOR)
        self._draw_centred_string(PAGE_W / 2, self.y, name)
        self._move(p["fs_name"] + 3)

        # ── Headline / title (optional) ────────────────────────────────────────
        if headline:
            self._set_font("Helvetica", p["fs_contact"])
            self._set_fill(MUTED_COLOR)
            self._draw_centred_string(PAGE_W / 2, self.y, headline)
            self._move(p["fs_contact"] + 2)

        # ── Contact line: email • phone ─────────────────────────────────────
        contact_parts = [p for p in [email, phone] if p]
        if contact_parts:
            sep = "  \u2022  "
            contact_line = sep.join(contact_parts)
            self._set_font("Helvetica", p["fs_contact"])
            self._set_fill(MUTED_COLOR)
            self._draw_centred_string(PAGE_W / 2, self.y, contact_line)
            self._move(p["fs_contact"] + 2)

        # ── Links line: linkedin • github • website ─────────────────────────
        link_parts = [lk for lk in [linkedin, github, website] if lk]
        if link_parts:
            sep = "  \u2022  "
            link_line = sep.join(link_parts)
            self._set_font("Helvetica", p["fs_contact"])
            self._set_fill(MUTED_COLOR)
            self._draw_centred_string(PAGE_W / 2, self.y, link_line)
            self._move(p["fs_contact"] + 3)

        # ── Header rule ─────────────────────────────────────────────────────
        self._set_stroke(HEADER_RULE)
        self._set_line_width(1.0)
        self._line(self.LEFT, self.y, self.RIGHT, self.y)
        self._move(4)

    # ── section header ────────────────────────────────────────────────────────

    def section_header(self, title: str) -> None:
        """Draw an uppercase section title with a full-width light rule beneath."""
        p = self.p
        fs = p["fs_section"]

        self._move(p["section_pre"])

        self._set_font("Helvetica-Bold", fs)
        self._set_fill(ACCENT)
        self._draw_string(self.LEFT, self.y, title.upper())
        self._move(fs + 1.5)

        # Thin light rule beneath title
        self._set_stroke(RULE_COLOR)
        self._set_line_width(0.5)
        self._line(self.LEFT, self.y, self.RIGHT, self.y)
        self._move(p["rule_gap"])

    # ── education ─────────────────────────────────────────────────────────────

    def education_section(self, entries: list[dict]) -> None:
        """Draw the Education section."""
        if not entries:
            return
        self.section_header("Education")
        p = self.p
        ld = self._leading()

        for entry in entries:
            institution = entry.get("institution", "")
            degree      = entry.get("degree", "")
            dates       = entry.get("dates", "")
            gpa         = entry.get("gpa", "")
            coursework  = entry.get("coursework", [])

            if self._will_overflow(p["fs_company"] + ld + 2):
                break

            # Institution bold left + date muted right
            self._set_font("Helvetica-Bold", p["fs_company"])
            self._set_fill(BODY_COLOR)
            self._draw_string(self.LEFT, self.y, institution)
            self._set_font("Helvetica", p["fs_body"])
            self._set_fill(MUTED_COLOR)
            self._draw_right_string(self.RIGHT, self.y, dates)
            self._move(p["fs_company"] + 1.5)

            # Degree italic + GPA inline
            deg_text = degree + (f"  —  GPA: {gpa}" if gpa else "")
            self._set_font("Helvetica-Oblique", p["fs_body"])
            self._set_fill(BODY_COLOR)
            self._draw_string(self.LEFT, self.y, deg_text)
            self._move(ld)

            # Coursework — compact single line if space allows
            if coursework:
                names = " • ".join(c["name"] for c in coursework)
                course_line = f"Relevant Coursework:  {names}"
                cw_lines = _wrap_text(
                    course_line, self.c, "Helvetica", p["fs_body"] - 0.25,
                    self.CONTENT_W,
                )
                if not self._will_overflow(len(cw_lines) * ld):
                    self._set_font("Helvetica", p["fs_body"] - 0.25)
                    self._set_fill(MUTED_COLOR)
                    for line in cw_lines:
                        self._draw_string(self.LEFT, self.y, line)
                        self._move(ld)

            self._move(p["entry_gap"])

    # ── experience ────────────────────────────────────────────────────────────

    def experience_section(self, jobs: list[dict]) -> None:
        """Draw the Experience section."""
        if not jobs:
            return
        self.section_header("Experience")
        p = self.p
        ld = self._leading()

        for job in jobs:
            company  = job.get("company", "")
            role     = job.get("role", "")
            dates    = job.get("dates", "")
            location = job.get("location", "")
            bullets  = job.get("bullets", [])

            if self._will_overflow(p["fs_company"] + ld * 2):
                break

            # Company bold left + dates muted right
            self._set_font("Helvetica-Bold", p["fs_company"])
            self._set_fill(BODY_COLOR)
            self._draw_string(self.LEFT, self.y, company)
            self._set_font("Helvetica", p["fs_body"])
            self._set_fill(MUTED_COLOR)
            self._draw_right_string(self.RIGHT, self.y, dates)
            self._move(p["fs_company"] + 1.5)

            # Role italic + location (compact, same line)
            role_loc = role + (f"  \u00b7  {location}" if location else "")
            self._set_font("Helvetica-Oblique", p["fs_role"])
            self._set_fill(BODY_COLOR)
            self._draw_string(self.LEFT, self.y, role_loc)
            self._move(p["fs_role"] + 2.5)

            # Bullets
            bx = self.LEFT + p["bullet_indent"]
            bw = self.CONTENT_W - p["bullet_indent"]
            for bullet in bullets:
                text = bullet.get("text", "") if isinstance(bullet, dict) else str(bullet)
                lines = _wrap_text(BULLET_CHAR + text, self.c, "Helvetica", p["fs_body"], bw)
                if self._will_overflow(len(lines) * ld):
                    break
                self._set_font("Helvetica", p["fs_body"])
                self._set_fill(BODY_COLOR)
                first = True
                for line in lines:
                    x = bx if first else bx + p["bullet_hang"]
                    self._draw_string(x, self.y, line)
                    self._move(ld)
                    first = False

            self._move(p["entry_gap"])

    # ── projects ──────────────────────────────────────────────────────────────

    def projects_section(self, projects: list[dict]) -> None:
        """Draw the Projects section."""
        if not projects:
            return
        self.section_header("Projects")
        p = self.p
        ld = self._leading()

        for proj in projects:
            name   = proj.get("name", "")
            desc   = proj.get("description", "")
            tech   = proj.get("tech", [])
            github = proj.get("github", "")

            if self._will_overflow(p["fs_company"] + ld * 2):
                break

            # Project name (bold, accent) + GitHub URL right-aligned
            self._set_font("Helvetica-Bold", p["fs_company"])
            self._set_fill(ACCENT)
            self._draw_string(self.LEFT, self.y, name)
            if github:
                self._set_font("Helvetica", p["fs_body"] - 0.5)
                self._set_fill(MUTED_COLOR)
                self._draw_right_string(self.RIGHT, self.y, github)
            self._move(p["fs_company"] + 1.5)

            # Tech stack — compact, bullet-separated
            if tech:
                tech_str = "Tech: " + " \u2022 ".join(tech)
                self._set_font("Helvetica-Oblique", p["fs_body"] - 0.25)
                self._set_fill(MUTED_COLOR)
                self._draw_string(self.LEFT, self.y, tech_str)
                self._move(ld)

            # Description — word-wrapped prose
            if desc:
                lines = _wrap_text(desc, self.c, "Helvetica", p["fs_body"], self.CONTENT_W)
                if not self._will_overflow(len(lines) * ld):
                    self._set_font("Helvetica", p["fs_body"])
                    self._set_fill(BODY_COLOR)
                    for line in lines:
                        self._draw_string(self.LEFT, self.y, line)
                        self._move(ld)

            self._move(p["entry_gap"])

    # ── skills ────────────────────────────────────────────────────────────────

    def skills_section(self, skills: dict[str, list[str]]) -> None:
        """
        Draw the Skills section in a compact horizontal format.

        Each category is rendered as one run:
          Languages:  Python  •  Go  •  TypeScript  •  SQL

        The category label is bold; the skills are regular weight, separated by •.
        """
        if not skills:
            return
        self.section_header("Skills")
        p = self.p
        ld = self._leading(p["fs_skills"])

        for category, names in skills.items():
            label    = f"{category.capitalize()}: "
            skill_str = "  \u2022  ".join(names)
            full_line = label + skill_str

            lines = _wrap_text(full_line, self.c, "Helvetica", p["fs_skills"], self.CONTENT_W)
            if self._will_overflow(len(lines) * ld):
                break

            for i, line in enumerate(lines):
                if i == 0:
                    colon_idx = line.find(":")
                    if colon_idx != -1:
                        lbl  = line[: colon_idx + 1]
                        rest = line[colon_idx + 1 :]
                        lbl_w = self.c.stringWidth(lbl, "Helvetica-Bold", p["fs_skills"])
                        self._set_font("Helvetica-Bold", p["fs_skills"])
                        self._set_fill(BODY_COLOR)
                        self._draw_string(self.LEFT, self.y, lbl)
                        self._set_font("Helvetica", p["fs_skills"])
                        self._draw_string(self.LEFT + lbl_w, self.y, rest)
                    else:
                        self._set_font("Helvetica", p["fs_skills"])
                        self._set_fill(BODY_COLOR)
                        self._draw_string(self.LEFT, self.y, line)
                else:
                    # Continuation wrap: indent past the label
                    self._set_font("Helvetica", p["fs_skills"])
                    self._set_fill(BODY_COLOR)
                    self._draw_string(self.LEFT + 4, self.y, line)
                self._move(ld)

        self._move(p["entry_gap"])

    # ── achievements ──────────────────────────────────────────────────────────

    def achievements_section(self, achievements: list[dict]) -> None:
        """Draw the Achievements & Certifications section."""
        if not achievements:
            return
        self.section_header("Achievements & Certifications")
        p = self.p
        ld = self._leading()

        for ach in achievements:
            title  = ach.get("title", "")
            issuer = ach.get("issuer", "")
            date   = ach.get("date", "")

            lines = _wrap_text(
                BULLET_CHAR + title,
                self.c, "Helvetica", p["fs_body"],
                self.CONTENT_W - p["bullet_indent"],
            )
            if self._will_overflow(len(lines) * ld):
                break

            self._set_font("Helvetica", p["fs_body"])
            self._set_fill(BODY_COLOR)
            for i, line in enumerate(lines):
                x = self.LEFT + p["bullet_indent"] if i == 0 else self.LEFT + p["bullet_indent"] + p["bullet_hang"]
                self._draw_string(x, self.y, line)
                self._move(ld)

            if issuer or date:
                meta = "  ".join(filter(None, [issuer, date]))
                self._set_font("Helvetica-Oblique", p["fs_body"] - 0.5)
                self._set_fill(MUTED_COLOR)
                self._draw_string(
                    self.LEFT + p["bullet_indent"] + p["bullet_hang"],
                    self.y, meta,
                )
                self._move(ld)

    # ── full render ───────────────────────────────────────────────────────────

    def render_all(self, resume_data: dict[str, Any]) -> None:
        """Draw all resume sections in the canonical order."""
        self.name_block(resume_data.get("personal", {}))
        self.education_section(resume_data.get("education", []))
        self.experience_section(resume_data.get("experience", []))
        self.projects_section(resume_data.get("projects", []))
        self.skills_section(resume_data.get("skills", {}))
        self.achievements_section(resume_data.get("achievements", []))

    # ── measure ───────────────────────────────────────────────────────────────

    def height_used(self) -> float:
        """Return how many points of vertical space have been consumed."""
        return (PAGE_H - self.p["margin_top"]) - self.y


# ─── Adaptive Layout Engine ───────────────────────────────────────────────────

def _select_params(canvas: Canvas, resume_data: dict[str, Any]) -> dict:
    """
    Try each compression level (0 → 3).  Return the first level whose params
    allow all content to fit within the available page height.

    If even level 3 overflows (extremely long resume), level 3 is still used
    — the renderer will simply stop drawing at the bottom margin rather than
    creating a second page.
    """
    for level, params in enumerate(_LEVELS):
        available = PAGE_H - params["margin_top"] - params["margin_bottom"]
        dry = Renderer(canvas, params, dry=True)
        dry.render_all(resume_data)
        used = dry.height_used()
        if used <= available:
            return params   # ← this level fits

    # Nothing fits — use the tightest level anyway (content will be clamped).
    return _LEVELS[-1]


# ─── Public entry point ───────────────────────────────────────────────────────

def render_pdf(resume_data: dict[str, Any], output_path: str) -> None:
    """
    Render a single-page A4 PDF resume from *resume_data*.

    The Adaptive Layout Engine selects the most comfortable spacing that
    still keeps all content on one page.  The renderer never calls
    showPage() — a second page is never created.

    *resume_data* is expected to come from ``filter_engine.build_resume_data()``.
    The ``render_pdf`` signature is unchanged from the previous version.
    """
    import os
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    c = Canvas(output_path, pagesize=A4)
    c.setTitle(f"Resume — {resume_data.get('personal', {}).get('name', 'Unknown')}")

    # Pass 1: dry-run to choose optimal spacing level
    params = _select_params(c, resume_data)

    # Pass 2: real render with chosen params
    r = Renderer(c, params, dry=False)
    r.render_all(resume_data)

    c.save()
