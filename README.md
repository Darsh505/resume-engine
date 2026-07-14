# Resume Engine

A **Git-driven, tag-based resume compilation engine** that generates a tailored one-page PDF resume for each target role from a single YAML source of truth.

Write your experience, projects, skills, and achievements once — tag each item with one or more role tags — and let the engine filter, rank, and render the most relevant content automatically.

---

## Features

- **Tag-based filtering** — items are included only when they carry the target tag (or `general`)
- **Priority ranking** — add an optional `priority: int` field to any item to control its position within a section
- **Budget enforcement** — sections are automatically capped (4 bullets/job, 3 projects, 4 achievements, 6 coursework entries) so the result always fits one page
- **ReportLab renderer** — fast, dependency-light, no browser or wkhtmltopdf required
- **Git integration** — auto-commits the rendered PDF on every compile (optional `--push`)
- **CI-ready** — GitHub Actions workflow runs tests and smoke-compiles on every push

---

## Install

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/resume-engine.git
cd resume-engine

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install all dependencies (including pytest)
pip install -r requirements.txt
```

---

## Setup: your personal data

Your real resume data lives in `data/resume.yaml` — a file that is **gitignored and never committed**.

```bash
# Copy the fictional example as your starting template
cp data/resume.example.yaml data/resume.yaml

# Edit it with your real information
$EDITOR data/resume.yaml
```

`data/resume.example.yaml` ships with the repository as a realistic template (fictional person "Jordan Rivera"). You can also compile against it for demos or CI without touching your personal data.

---

## Usage

### Compile a resume for a target role

```bash
python compile_resume.py --target backend
python compile_resume.py --target data-science
python compile_resume.py --target frontend
python compile_resume.py --target devops
```

The PDF is written to `output/resume_<target>.pdf` by default.

### All flags

| Flag | Short | Description |
|---|---|---|
| `--target ROLE` | `-t` | Target role to compile for (e.g. `backend`, `data-science`) |
| `--output PATH` | `-o` | Output PDF path (default: `output/resume_<target>.pdf`) |
| `--push` | | Push to remote after auto-commit |
| `--preview` | | Open the generated PDF immediately |
| `--list-targets` | | Print all unique tags found in the YAML and exit |
| `--targets-report` | | Print a table of content counts per target and exit |

### Examples

```bash
# Compile with a custom output path
python compile_resume.py --target backend --output ~/Desktop/resume_backend.pdf

# Compile, auto-commit, and push
python compile_resume.py --target data-science --push

# Compile and open immediately
python compile_resume.py --target frontend --preview

# Discover which tags exist in your YAML
python compile_resume.py --list-targets

# See how many bullets/projects/skills each target would get
python compile_resume.py --targets-report
```

---

## Running Tests

```bash
# Run the full pytest suite (from repo root, venv active)
pytest tests/ -v
```

The suite covers:
- `filter_list` / `_matches` — tag inclusion/exclusion logic
- `rank_by_relevance` — relevance ordering and `priority` field behaviour
- `apply_budget` — trimming and no-op cases
- `filter_experience` — regression test for zero-bullet job removal
- `filter_education` — degree always kept even with zero coursework
- `filter_skills` — empty-category omission
- `collect_all_tags` — `"general"` excluded from the tag list
- `build_resume_data` — full integration test against an in-memory fixture YAML
- Edge cases — empty lists, missing `tags` key, unknown target

---

## How CI Works

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request:

1. **Setup** — checks out the repo, sets up Python 3.12, installs `requirements.txt`
2. **Tests** — runs `pytest tests/ -v`
3. **Smoke tests** — compiles `--target backend`, `--target data-science`, and `--target frontend`

The smoke tests use `data/resume.example.yaml` automatically (because `data/resume.yaml` is gitignored and absent in CI). PDFs are written to `/tmp` so no git operations are triggered.

The workflow **fails** if any test fails or if any compilation raises an exception.

---

## Adding a New Target

1. Add the new tag (e.g. `mobile`) to items in `data/resume.yaml`
2. Compile: `python compile_resume.py --target mobile`
3. Add fixture data for `mobile` to `tests/conftest.py → sample_data` — no test functions need to be rewritten

---

## Priority Field

Any item (bullet, project, skill, achievement, or coursework entry) may carry an optional `priority: int` field:

```yaml
bullets:
  - text: "Most important thing I did."
    tags: [backend]
    priority: 2        # floats to the top

  - text: "Second most important."
    tags: [backend]
    priority: 1

  - text: "Normal item, no priority."
    tags: [backend]   # defaults to priority: 0
```

- **Primary sort key**: `priority` descending (missing → 0)
- **Secondary sort key**: tag-relevance score (existing behaviour)
- **Stable**: equal `priority` + equal relevance preserves YAML order

You don't need to add `priority` to every entry — it's entirely optional.

---

## Project Structure

```
resume-engine/
│
├── data/
│   ├── resume.example.yaml      # Fictional template — commit this
│   └── resume.yaml              # YOUR real data — gitignored, never committed
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared pytest fixtures
│   └── test_filter_engine.py   # Full test suite
│
├── templates/
│   └── resume_template.html    # Jinja2/WeasyPrint template (dormant — see Roadmap)
│
├── output/                      # Generated PDFs (gitignored)
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
│
├── compile_resume.py           # CLI entrypoint
├── filter_engine.py            # Tag filtering, ranking, budget enforcement
├── pdf_renderer.py             # ReportLab renderer
├── git_utils.py                # Auto-commit / push helpers
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## Personal Data & Git History

| File | Committed? |
|---|---|
| `data/resume.example.yaml` | ✅ Yes — fictional, safe to share |
| `data/resume.yaml` | ❌ No — gitignored |
| `output/*.pdf` | ❌ No — gitignored |

> **History note**: If you ever accidentally commit real personal data and later want it removed from git history, that requires `git filter-repo` or BFG Repo-Cleaner — a separate manual step not covered here.

---

## Roadmap

- **WeasyPrint / HTML renderer** — `templates/resume_template.html` is a Jinja2 template already in the repo but not yet wired to the engine. Future work would add a `--renderer html` flag that uses WeasyPrint to produce a browser-faithful PDF, enabling CSS-based design control that ReportLab's canvas API doesn't easily support.
- **Multiple output pages** — currently enforces a one-page budget; two-page support is a natural next step for senior engineers with long histories.
- **YAML schema validation** — add a `validate` command (or pre-render check) using `jsonschema` or `pydantic` to catch malformed YAML before rendering.
- **Interactive target selector** — a TUI (e.g. `rich` + `prompt_toolkit`) for browsing and selecting targets without remembering tag names.
- **Cover letter integration** — a parallel `cover_letter.yaml` + Jinja2 template that uses the same tag system to generate tailored cover letters.
