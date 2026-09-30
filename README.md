# Resume Engine

A Git-driven, tag-based resume compilation engine that generates tailored, single-page PDF resumes for specific job roles from a unified YAML source of truth.

Write your professional experience, projects, skills, and honors once in a single structured file. Tag each item with one or more role identifiers, and let the engine filter, rank, and render an ATS-optimized PDF resume deterministically.

Repository: https://github.com/Darsh505/resume-engine

---

## Academic & Industrial Training Metadata

- Student Name: Darshveer Singh
- University Roll Number: 2449377
- Degree & Branch: B.Tech Computer Science & Engineering (Artificial Intelligence & Machine Learning)
- Institution: Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur
- Training Organisation: Mits Academy
- Training Tenure: 8 June 2026 to 28 July 2026 (45 Calendar Days, 37 Working Days)
- Primary Mentor: Mentor Srishti (Technical Lead, Mits Academy)

---

## Core System Architecture

```
+-------------------------------------------------------------------------+
|                        RESUME ENGINE PIPELINE                           |
+-------------------------------------------------------------------------+
|                                                                         |
|   [ data/resume.yaml ]                                                  |
|            |                                                            |
|            v                                                            |
|   +-------------------+                                                 |
|   |  web/data_store   |  --> Fallback: data/resume.example.yaml         |
|   +-------------------+                                                 |
|            |                                                            |
|            v                                                            |
|   +-------------------+                                                 |
|   |   filter_engine   |  --> Matches target tags (backend, devops, etc.)|
|   |                   |  --> Evaluates integer priority scoring         |
|   |                   |  --> Truncates sections to strict page budgets  |
|   +-------------------+                                                 |
|            |                                                            |
|            v                                                            |
|   +-------------------+                                                 |
|   |   pdf_renderer    |  --> ReportLab vector canvas math               |
|   |                   |  --> Computes line heights and font margins     |
|   |                   |  --> Generates 792pt single-page PDF bytecode   |
|   +-------------------+                                                 |
|            |                                                            |
|            v                                                            |
|   +-------------------+                                                 |
|   |     Output &      |  --> Writes to: output/resume_<target>.pdf      |
|   |   Git History     |  --> Auto-commits PDF with timestamp to Git     |
|   +-------------------+                                                 |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## Numbered Algorithmic Pipelines

### Pipeline 1: Tag-Based Extraction and Visibility Score

Each resume item `i` is filtered using the boolean predicate:

```
Include(i, Target) = (Target in Tags(i)) OR ("general" in Tags(i))
```

1. Load master data dictionary from active YAML path.
2. For each experience bullet, evaluate if the current target role tag is present.
3. If true, retain bullet; if false, discard unless marked with the universal `general` tag.
4. Apply the same predicate across technical projects, skill groups, and honors.

### Pipeline 2: Priority Ranking Calculation

Filtered items within a section are sorted deterministically using a descending integer priority weight:

```
SortKey(i) = Priority(i) if defined else 0
RankedList = SortDescending(Items, key=SortKey)
```

1. Read the optional `priority: int` field for each item.
2. High-impact items (e.g. `priority: 50`) bubble to the top of the section.
3. Stable secondary sort preserves chronological order when priorities are identical.

### Pipeline 3: Page Budget Capping Formulation

To guarantee single-page rendering without vertical overflow, section lengths are strictly capped:

```
ExperienceBullets(Job) <= 4
TechnicalProjects      <= 3
KeyAchievements        <= 4
CourseworkEntries      <= 6
TotalPageHeight        <= 792 points (11-inch Letter height)
```

1. Slicing operations truncate collections: `JobBullets = JobBullets[:4]`.
2. Projects section is truncated: `Projects = Projects[:3]`.
3. ReportLab calculates available vertical baseline offset: `y_pos = y_pos - (line_height * line_count)`.
4. If calculated `y_pos < margin_bottom`, font leading and paragraph spacing are dynamically compressed to prevent multi-page spill.

---

## Key Features

- Tag-Based Filtering: Items are dynamically selected based on target role tags (`backend`, `frontend`, `devops`, `data-science`).
- Priority Ranking: Control the vertical position of achievements within sections using explicit integer weights.
- Single-Page Budget Guarantee: Automatic item caps ensure the output fits exactly on one page every time.
- Offline-First ReportLab Renderer: Direct PDF bytecode rendering in under 250 milliseconds with zero cloud dependencies.
- Git Integration: Automatically stages and commits newly rendered PDFs with ISO timestamps.
- Dual Interface: Comprehensive CLI for terminal batch generation plus an interactive local web studio running at `http://127.0.0.1:8000`.
- Automated Test Suite: 42 comprehensive Pytest unit tests verifying filtering, sorting, and budgeting algorithms.

---

## Installation and Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Darsh505/resume-engine.git
cd resume-engine

# 2. Create and activate a Python virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Command Line Interface (CLI)

```bash
# List all role tags available in the YAML data
python compile_resume.py --list-targets

# View an audit matrix of items matching each target role
python compile_resume.py --targets-report

# Compile a resume for a specific target role
python compile_resume.py --target backend
python compile_resume.py --target devops
python compile_resume.py --target frontend
python compile_resume.py --target data-science

# Compile and automatically open the resulting PDF in system viewer
python compile_resume.py --target backend --preview
```

### 2. Local Web Studio

```bash
# Launch the local web server
python run_web.py

# Or run with auto-reload for development:
python run_web.py --dev
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

- Edit candidate contact information, bullet points, skills, and projects in the live form.
- Click "Save Changes" to validate via Pydantic and update `data/resume.yaml`.
- Select your target role from the dropdown and click "Generate PDF" to compile and stream the tailored PDF directly in the browser.

---

## Automated Testing

Execute the test suite to verify filter logic and budget enforcement:

```bash
pytest
```

Output:
```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: A:\projects\resume-engine
collected 42 items

tests\test_filter_engine.py ..........................................   [100%]

============================== 42 passed in 0.08s ==============================
```

---

## Project Structure

```
resume-engine/
|-- compile_resume.py       # Main CLI compiler with Windows UTF-8 support
|-- filter_engine.py        # Tag matching, priority ranking, and budget capping logic
|-- pdf_renderer.py         # ReportLab canvas drawing and typographic layout engine
|-- git_utils.py            # GitPython staging and automated commit hooks
|-- run_web.py              # Convenience launcher for the local Uvicorn web server
|-- requirements.txt        # Python dependency manifest
|-- data/
|   |-- resume.example.yaml # Pre-populated demo resume data
|   `-- resume.yaml         # Personal resume data (gitignored for privacy)
|-- output/                 # Destination directory for compiled PDF artifacts
|-- templates/              # ReportLab document styling templates
|-- tests/
|   `-- test_filter_engine.py # 42 automated Pytest unit tests
`-- web/
    |-- app.py              # FastAPI application and REST route controllers
    |-- data_store.py       # Centralized file I/O choke-point with demo fallback
    |-- models.py           # Pydantic v2 data models and schema validators
    |-- static/             # CSS stylesheets and vanilla JavaScript assets
    `-- templates/          # Jinja2 HTML templates for the local web editor
```

---

## License

MIT License. Developed by Darshveer Singh as part of the Summer Industrial Training Program at Mits Academy in affiliation with Rayat Bahra Institute of Engineering & Nanotechnology, Hoshiarpur.
