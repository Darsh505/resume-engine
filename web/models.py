"""
web/models.py — Pydantic models mirroring the resume YAML schema.

These models serve two purposes:
  1. Validate incoming JSON from the browser editor before writing to disk.
  2. Serialise back to YAML-friendly dicts via .model_dump() — the output
     structure is identical to what filter_engine.py expects as input.

All models inherit _Base which silently ignores unknown YAML fields
(extra='ignore'), so hand-crafted YAML with non-standard keys doesn't
break the editor.

Future note: when this becomes an API-backed SaaS, these same models
become the request/response schemas for the REST API with zero changes.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ConfigDict


class _Base(BaseModel):
    """Silently ignore YAML keys not in the model — permissive import."""
    model_config = ConfigDict(extra="ignore")


# ── Personal ──────────────────────────────────────────────────────────────────

class PersonalInfo(_Base):
    name: str
    email: str
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name is required")
        return v

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Email is required")
        return v


# ── Education ─────────────────────────────────────────────────────────────────

class CourseWorkItem(_Base):
    name: str
    tags: list[str] = Field(default_factory=list)


class EducationEntry(_Base):
    institution: str
    degree: str
    dates: str = ""
    gpa: str = ""
    coursework: list[CourseWorkItem] = Field(default_factory=list)

    @field_validator("institution", "degree")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field is required")
        return v


# ── Experience ────────────────────────────────────────────────────────────────

class Bullet(_Base):
    text: str
    tags: list[str] = Field(default_factory=list)
    priority: int = 0

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Bullet text cannot be empty")
        return v


class ExperienceEntry(_Base):
    company: str
    role: str
    dates: str = ""
    location: str = ""
    bullets: list[Bullet] = Field(default_factory=list)

    @field_validator("company", "role")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field is required")
        return v


# ── Projects ──────────────────────────────────────────────────────────────────

class Project(_Base):
    """
    Note: ``tech`` is a flat list[str], not a list of tagged dicts.
    Tech items are not filtered by tag — the entire list is included
    for any target that matches the project.
    """
    name: str
    description: str = ""
    tech: list[str] = Field(default_factory=list)
    github: str = ""
    tags: list[str] = Field(default_factory=list)
    priority: int = 0

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Project name is required")
        return v


# ── Skills ────────────────────────────────────────────────────────────────────

class Skill(_Base):
    """
    A single skill entry inside a category.  The ``tags`` field controls
    which target profiles include this skill (same filtering as bullets/projects).
    """
    name: str
    tags: list[str] = Field(default_factory=list)


# ── Achievements ──────────────────────────────────────────────────────────────

class Achievement(_Base):
    title: str
    issuer: str = ""
    date: str = ""
    tags: list[str] = Field(default_factory=list)
    priority: int = 0

    @field_validator("title")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title is required")
        return v


# ── Root ──────────────────────────────────────────────────────────────────────

class ResumeData(_Base):
    """
    Top-level resume model.  ``model_dump()`` produces a dict that is
    structurally identical to the raw YAML dict filter_engine.py expects,
    so it can be written directly back to data/resume.yaml or passed
    straight to build_resume_data.
    """
    personal: PersonalInfo
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    # dict[category_name, list[Skill]]  — matches YAML structure exactly
    skills: dict[str, list[Skill]] = Field(default_factory=dict)
    achievements: list[Achievement] = Field(default_factory=list)
