"""
web/data_store.py — Single choke-point for all resume data I/O.

All file-system reads and writes go through the two public functions here:

    load_resume_data()     → raw dict (same structure filter_engine expects)
    save_resume_data(data) → writes to data/resume.yaml

Light seam: if this project ever becomes a hosted SaaS with a database,
you change these two functions only.  No route handler touches a file path.

The file-path fallback mirrors compile_resume.py's behaviour exactly:
  data/resume.yaml     → used if it exists  (real personal data, gitignored)
  data/resume.example.yaml → fallback        (fictional demo data)
"""

from __future__ import annotations

from pathlib import Path

import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).parent.parent       # web/ → project root
DATA_DIR     = REPO_ROOT / "data"
YAML_PRIMARY = DATA_DIR / "resume.yaml"           # real data — gitignored
YAML_EXAMPLE = DATA_DIR / "resume.example.yaml"   # demo data — committed
OUTPUT_DIR   = REPO_ROOT / "output"


def active_yaml_path() -> Path:
    """Return whichever YAML file is currently in use."""
    return YAML_PRIMARY if YAML_PRIMARY.exists() else YAML_EXAMPLE


def is_using_example() -> bool:
    """True when the editor is showing demo data (no real resume.yaml yet)."""
    return not YAML_PRIMARY.exists()


def load_resume_data() -> dict:
    """
    Load and return the active resume YAML as a raw Python dict.

    Returns an empty dict on any parse error rather than raising, so a
    corrupted file doesn't crash the editor — the user can fix it in-form.
    """
    path = active_yaml_path()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_resume_data(data: dict) -> None:
    """
    Write *data* to data/resume.yaml.

    Always writes to the primary file, never to resume.example.yaml.
    Creates data/ if it doesn't exist yet (first-time setup).
    """
    DATA_DIR.mkdir(exist_ok=True)
    with open(YAML_PRIMARY, "w", encoding="utf-8") as fh:
        yaml.dump(
            data, fh,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
