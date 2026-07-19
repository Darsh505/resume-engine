"""
web/app.py — FastAPI application for the Resume Engine web frontend.

Start from the project root:

    uvicorn web.app:app --reload --port 8000

Routes
──────
  GET  /              Edit resume data (form pre-filled from YAML)
  POST /save          Validate via Pydantic, write to data/resume.yaml
  GET  /generate      Choose target tag + git options
  POST /generate      filter_engine → pdf_renderer → PDF download
                      Optional commit reported in X-Commit-Status header.
  POST /git/push      Push to remote — separate, explicit action only

Design notes
────────────
• All resume I/O goes through data_store, not scattered file opens.
• filter_engine and pdf_renderer are imported as-is; no logic is re-
  implemented here.
• FastAPI returns 422 automatically if Pydantic validation fails on
  POST /save, with structured detail[] the browser JS can display inline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ── Project root on sys.path so filter_engine etc. resolve ───────────────────
_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import filter_engine   # noqa: E402
import git_utils       # noqa: E402
import pdf_renderer    # noqa: E402

from web.data_store import (  # noqa: E402
    OUTPUT_DIR,
    active_yaml_path,
    is_using_example,
    load_resume_data,
    save_resume_data,
)
from web.models import ResumeData  # noqa: E402

# ── App & static assets ───────────────────────────────────────────────────────
app = FastAPI(title="Resume Engine", docs_url=None, redoc_url=None)

_WEB = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(_WEB / "static")), name="static")
templates = Jinja2Templates(directory=str(_WEB / "templates"))


# ── Template context helper ───────────────────────────────────────────────────

def _base_ctx() -> dict:
    """Return the base template context (no request — passed separately in Starlette 1.x API)."""
    return {"using_example": is_using_example()}


# ── Edit page ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def edit_page(request: Request):
    """
    Render the resume editor pre-filled from the active YAML.

    The raw YAML dict is validated through ResumeData so the form always
    receives a structurally clean object (default values filled in for
    missing fields, unknown keys dropped).  If the YAML is so broken that
    Pydantic can't parse it at all, fall back to the raw dict so the user
    can still see and fix the data.
    """
    raw = load_resume_data()
    try:
        resume = ResumeData.model_validate(raw)
        data = resume.model_dump()
    except Exception:
        data = raw
    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={**_base_ctx(), "resume_json": json.dumps(data, ensure_ascii=False)},
    )


@app.post("/save")
async def save(resume: ResumeData):
    """
    Validate the submitted JSON body via Pydantic and write to resume.yaml.

    FastAPI + Pydantic automatically return HTTP 422 with a structured
    ``detail`` array if validation fails before this handler is reached,
    so the JS can display per-field errors without any extra work here.
    """
    save_resume_data(resume.model_dump())
    return {"ok": True, "message": "Resume saved successfully"}


# ── Generate page ─────────────────────────────────────────────────────────────

@app.get("/generate", response_class=HTMLResponse)
async def generate_page(request: Request):
    """
    Render the generate page.

    Tags come from filter_engine.collect_all_tags() — exactly the same
    population logic as the CLI's --list-targets flag.

    multi_theme is False: pdf_renderer.py currently has one design-token
    profile (module-level constants, no theme registry, no parameter in
    render_pdf).  The UI shows a disabled placeholder.  To enable themes,
    build a theme-registry API in pdf_renderer first, then flip this flag.
    """
    raw = load_resume_data()
    tags = filter_engine.collect_all_tags(raw)
    return templates.TemplateResponse(
        request=request,
        name="generate.html",
        context={**_base_ctx(), "tags": tags, "multi_theme": False},
    )


@app.post("/generate")
async def generate(
    target: Annotated[str, Form()],
    commit: Annotated[str, Form()] = "off",
):
    """
    Run filter_engine → pdf_renderer and return the PDF as a download.

    ``commit`` is a checkbox value; HTML sends "on" when checked, nothing
    when unchecked (FastAPI defaults to "off").  We check for "on" rather
    than casting to bool to avoid HTML form quirkiness.

    Commit outcome is returned in the ``X-Commit-Status`` header
    (values: "skipped" | "success" | "ignored" | "failed") so the
    browser can show a status toast without a second network round-trip.

    Push is intentionally not bundled here — it requires its own explicit
    confirmation via POST /git/push.
    """
    do_commit = commit.lower() in ("on", "1", "true", "yes")
    safe_target = target.replace(" ", "-").lower()

    # ── Filter ──────────────────────────────────────────────────────────────
    yaml_path = str(active_yaml_path())
    try:
        resume_data = filter_engine.build_resume_data(yaml_path, target)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Filter error: {exc}")

    # ── Render ──────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"resume_{safe_target}.pdf"
    try:
        pdf_renderer.render_pdf(resume_data, str(output_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Render error: {exc}")

    # ── Optional git commit ──────────────────────────────────────────────────
    commit_status = "skipped"
    if do_commit:
        ok = git_utils.git_commit(
            str(output_path), target, repo_path=str(_REPO_ROOT)
        )
        commit_status = "success" if ok else "ignored"

    return FileResponse(
        path=str(output_path),
        filename=f"resume_{safe_target}.pdf",
        media_type="application/pdf",
        headers={"X-Commit-Status": commit_status},
    )


# ── Git push ──────────────────────────────────────────────────────────────────

@app.post("/git/push")
async def git_push():
    """
    Push to origin.  Separate, explicit action — never triggered automatically.

    The browser JS shows a confirmation dialog before calling this endpoint,
    satisfying the requirement that push requires its own separate confirmation.
    """
    ok = git_utils.git_push(repo_path=str(_REPO_ROOT))
    return {
        "ok": ok,
        "message": "Pushed to remote successfully." if ok
                   else "Push failed — check the server logs for details.",
    }
