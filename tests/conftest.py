"""
conftest.py — Shared pytest fixtures for the Resume Engine test suite.

Design principle: the ``sample_data`` fixture is a plain Python dict that
mirrors the schema of a real resume YAML.  Adding support for a new target
tag later only requires adding items with that tag to the fixture dict; no
test functions need to be rewritten.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Core fixture: small, in-memory resume dataset
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_data() -> dict:
    """
    A small, self-contained resume dataset that exercises every section
    and tag combination used in the test suite.

    Tags used: backend, frontend, data-science, devops, general
    (plus a fictional ``mobile`` tag to test unknown-target edge cases)
    """
    return {
        "personal": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1 (555) 000-0001",
            "linkedin": "linkedin.com/in/janedoe",
            "github": "github.com/janedoe",
            "website": "janedoe.dev",
        },
        "education": [
            {
                "institution": "State University",
                "degree": "B.S. Computer Science",
                "dates": "2018–2022",
                "gpa": "3.9",
                "coursework": [
                    {"name": "Data Structures", "tags": ["general"]},
                    {"name": "Database Systems", "tags": ["backend", "data-science"]},
                    {"name": "Machine Learning", "tags": ["data-science"]},
                    {"name": "Web Technologies", "tags": ["frontend"]},
                    {"name": "Operating Systems", "tags": ["backend", "devops"]},
                    {"name": "Computer Networks", "tags": ["backend", "devops"]},
                ],
            }
        ],
        "experience": [
            {
                "company": "Acme Corp",
                "role": "Backend Engineer",
                "dates": "2022–Present",
                "location": "Remote",
                "bullets": [
                    {"text": "Built a REST API.", "tags": ["backend", "general"]},
                    {"text": "Wrote SQL queries.", "tags": ["backend", "data-science"]},
                    {"text": "Set up CI/CD pipelines.", "tags": ["devops"]},
                    {"text": "Mentored juniors.", "tags": ["general"]},
                ],
            },
            {
                "company": "Old Startup",
                "role": "Frontend Intern",
                "dates": "2021–2022",
                "location": "NYC",
                "bullets": [
                    {"text": "Built React components.", "tags": ["frontend"]},
                    {"text": "Wrote CSS.", "tags": ["frontend"]},
                ],
            },
            {
                "company": "Irrelevant Co",
                "role": "Data Entry Clerk",
                "dates": "2020–2021",
                "location": "Remote",
                "bullets": [
                    # No backend/general tags — should be dropped for backend target
                    {"text": "Typed things.", "tags": ["frontend"]},
                ],
            },
        ],
        "projects": [
            {
                "name": "BackendApp",
                "description": "A backend service.",
                "tech": ["Python", "Postgres"],
                "tags": ["backend", "backend"],  # double tag → higher relevance score
            },
            {
                "name": "DataApp",
                "description": "A data pipeline.",
                "tech": ["Python", "Spark"],
                "tags": ["data-science"],
            },
            {
                "name": "FrontendApp",
                "description": "A React dashboard.",
                "tech": ["React"],
                "tags": ["frontend"],
            },
            {
                "name": "GeneralApp",
                "description": "A general utility.",
                "tech": ["Python"],
                "tags": ["general"],
            },
        ],
        "skills": {
            "languages": [
                {"name": "Python", "tags": ["backend", "data-science", "general"]},
                {"name": "TypeScript", "tags": ["frontend"]},
                {"name": "SQL", "tags": ["backend", "data-science", "general"]},
                {"name": "Go", "tags": ["backend", "devops"]},
            ],
            "frameworks": [
                {"name": "FastAPI", "tags": ["backend"]},
                {"name": "React", "tags": ["frontend"]},
                {"name": "PyTorch", "tags": ["data-science"]},
            ],
            "devops_tools": [
                # Category with no backend tags — should be dropped for backend
                # (unless we add backend tag; for devops target, this shows)
                {"name": "Figma", "tags": ["frontend"]},
                {"name": "Sketch", "tags": ["frontend"]},
            ],
        },
        "achievements": [
            {
                "title": "AWS Certified Developer",
                "issuer": "Amazon",
                "date": "2023",
                "tags": ["backend", "devops"],
            },
            {
                "title": "Hackathon Winner",
                "issuer": "MIT",
                "date": "2022",
                "tags": ["general"],
            },
            {
                "title": "Data Science Award",
                "issuer": "KDD",
                "date": "2022",
                "tags": ["data-science"],
            },
            {
                "title": "Frontend Prize",
                "issuer": "CSS Conf",
                "date": "2021",
                "tags": ["frontend"],
            },
        ],
    }


# ---------------------------------------------------------------------------
# Factory fixture: write sample_data (or a custom dict) to a tmp YAML file
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_yaml(tmp_path, sample_data):
    """
    Write ``sample_data`` to a temporary YAML file and return the path string.

    Usage in tests::

        def test_something(tmp_yaml):
            data = load_yaml(tmp_yaml)
            ...
    """
    import yaml  # only needed at fixture-call time

    yaml_file = tmp_path / "resume.yaml"
    yaml_file.write_text(yaml.dump(sample_data, allow_unicode=True), encoding="utf-8")
    return str(yaml_file)
