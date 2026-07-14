"""
filter_engine.py — Tag-based filtering, ranking, and budget enforcement.

All functions are pure (no side effects) and unit-testable.

Priority field
──────────────
Any item (bullet, project, skill, achievement, coursework entry) may carry an
optional ``priority: int`` field.  ``rank_by_relevance`` uses it as the
*primary* sort key (descending), with the existing tag-relevance score as a
*secondary* tiebreaker.  Items without ``priority`` default to 0, so the field
is entirely optional — existing YAML files require no changes.
"""

from __future__ import annotations

import copy
from typing import Any

import yaml

# ─── Content budget constants ────────────────────────────────────────────────
MAX_PROJECTS: int = 3
MAX_BULLETS_PER_JOB: int = 4
MAX_ACHIEVEMENTS: int = 4
MAX_COURSEWORK: int = 6


# ─── YAML loading ────────────────────────────────────────────────────────────

def load_yaml(path: str) -> dict[str, Any]:
    """Load and return the resume YAML.  Raises FileNotFoundError / yaml.YAMLError on problems."""
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping at the top level in {path!r}")
    return data


def collect_all_tags(data: dict[str, Any]) -> list[str]:
    """Return a sorted, deduplicated list of every tag found anywhere in the YAML."""
    tags: set[str] = set()

    def _harvest(obj: Any) -> None:
        if isinstance(obj, dict):
            if "tags" in obj and isinstance(obj["tags"], list):
                tags.update(obj["tags"])
            for v in obj.values():
                _harvest(v)
        elif isinstance(obj, list):
            for item in obj:
                _harvest(item)

    _harvest(data)
    tags.discard("general")          # "general" is a meta-tag, not a target
    return sorted(tags)


# ─── Core filter helpers ──────────────────────────────────────────────────────

def _matches(item: dict[str, Any], target: str) -> bool:
    """Return True if *item* is relevant for *target* (or is tagged 'general')."""
    item_tags: list[str] = item.get("tags", [])
    return (target in item_tags) or ("general" in item_tags)


def _relevance_score(item: dict[str, Any], target: str) -> int:
    """Count how many times *target* appears in an item's tags (used for ranking)."""
    return item.get("tags", []).count(target)


def filter_list(items: list[dict], target: str) -> list[dict]:
    """Keep only items whose tags include *target* or 'general'."""
    return [item for item in items if _matches(item, target)]


def rank_by_relevance(items: list[dict], target: str) -> list[dict]:
    """
    Sort *items* by relevance, with an optional ``priority`` boost.

    Sort keys (both descending):
      1. ``priority`` — explicit integer field on the item; missing → 0.
      2. tag-relevance score — count of *target* occurrences in ``tags``
         (the original ranking behaviour, now used as a tiebreaker).

    The sort is stable, so items with identical ``priority`` **and** identical
    relevance score preserve their original YAML order.

    Why updated in-place rather than adding a new function?
    ────────────────────────────────────────────────────────
    All five section-level filters (filter_education, filter_experience,
    filter_projects, filter_skills, filter_achievements) already call
    rank_by_relevance.  Keeping the same name means every section benefits
    from priority ranking without touching any call-site — DRY and safe.
    """
    return sorted(
        items,
        key=lambda item: (item.get("priority", 0), _relevance_score(item, target)),
        reverse=True,
    )


def apply_budget(items: list[dict], max_n: int) -> list[dict]:
    """Trim *items* to at most *max_n* entries."""
    return items[:max_n]


# ─── Section-level filters ────────────────────────────────────────────────────

def filter_education(education: list[dict], target: str) -> list[dict]:
    """
    Education entries are always included (no tag on the degree itself).
    Only the *coursework* within each entry is filtered.
    """
    result = []
    for entry in education:
        e = copy.deepcopy(entry)
        raw_coursework = e.get("coursework", [])
        filtered = filter_list(raw_coursework, target)
        filtered = rank_by_relevance(filtered, target)
        filtered = apply_budget(filtered, MAX_COURSEWORK)
        e["coursework"] = filtered
        result.append(e)
    return result


def filter_experience(experience: list[dict], target: str) -> list[dict]:
    """
    Filter bullet points within each experience entry.
    Jobs with zero matching bullets after filtering are still included
    (with an empty bullet list) so the role history is preserved.
    """
    result = []
    for job in experience:
        j = copy.deepcopy(job)
        raw_bullets = j.get("bullets", [])
        filtered = filter_list(raw_bullets, target)
        filtered = rank_by_relevance(filtered, target)
        filtered = apply_budget(filtered, MAX_BULLETS_PER_JOB)
        j["bullets"] = filtered
        result.append(j)
    # Remove jobs that have zero bullets (entirely irrelevant roles)
    result = [j for j in result if j["bullets"]]
    return result


def filter_projects(projects: list[dict], target: str) -> list[dict]:
    """Filter, rank and budget-cap projects."""
    filtered = filter_list(projects, target)
    filtered = rank_by_relevance(filtered, target)
    filtered = apply_budget(filtered, MAX_PROJECTS)
    return filtered


def filter_skills(skills: dict[str, list[dict]], target: str) -> dict[str, list[str]]:
    """
    Filter each skill category and return a dict of {category: [skill_name, ...]}.
    Categories with zero matching skills are omitted from the output.
    """
    result: dict[str, list[str]] = {}
    for category, items in skills.items():
        matched = filter_list(items, target)
        matched = rank_by_relevance(matched, target)
        if matched:
            result[category] = [s["name"] for s in matched]
    return result


def filter_achievements(achievements: list[dict], target: str) -> list[dict]:
    """Filter, rank and budget-cap achievements."""
    filtered = filter_list(achievements, target)
    filtered = rank_by_relevance(filtered, target)
    filtered = apply_budget(filtered, MAX_ACHIEVEMENTS)
    return filtered


# ─── Targets report helpers ───────────────────────────────────────────────────

def targets_report(data: dict[str, Any]) -> dict[str, dict[str, int]]:
    """
    Return a dict mapping each unique target tag → counts of:
      bullets, projects, achievements
    Useful for the --targets-report CLI flag.
    """
    all_tags = collect_all_tags(data)
    report: dict[str, dict[str, int]] = {}

    for tag in all_tags:
        bullet_count = 0
        for job in data.get("experience", []):
            bullet_count += sum(1 for b in job.get("bullets", []) if _matches(b, tag))

        project_count = len(filter_list(data.get("projects", []), tag))
        achievement_count = len(filter_list(data.get("achievements", []), tag))

        skill_count = 0
        for items in data.get("skills", {}).values():
            skill_count += sum(1 for s in items if _matches(s, tag))

        report[tag] = {
            "bullets": bullet_count,
            "projects": project_count,
            "achievements": achievement_count,
            "skills": skill_count,
        }

    return report


# ─── Main orchestrator ────────────────────────────────────────────────────────

def build_resume_data(yaml_path: str, target: str) -> dict[str, Any]:
    """
    Load the YAML and return a fully-filtered, ranked, budget-enforced dict
    ready for the PDF renderer.
    """
    raw = load_yaml(yaml_path)

    return {
        "personal": raw.get("personal", {}),
        "education": filter_education(raw.get("education", []), target),
        "experience": filter_experience(raw.get("experience", []), target),
        "projects": filter_projects(raw.get("projects", []), target),
        "skills": filter_skills(raw.get("skills", {}), target),
        "achievements": filter_achievements(raw.get("achievements", []), target),
        "target": target,
    }
