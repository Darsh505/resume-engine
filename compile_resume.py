#!/usr/bin/env python3
"""
compile_resume.py — Main CLI entrypoint for the Git-Driven Resume Engine.

Usage examples
──────────────
  python compile_resume.py --target backend --output ./output/resume_backend.pdf
  python compile_resume.py --target data-science --output ./output/resume_ds.pdf
  python compile_resume.py --list-targets
  python compile_resume.py --targets-report
  python compile_resume.py --target backend --push
  python compile_resume.py --target backend --preview
"""

from __future__ import annotations

import argparse
import os
import sys

# ─── Colorama bootstrap ───────────────────────────────────────────────────────
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)

    def _green(s: str)  -> str: return f"{Fore.GREEN}{s}{Style.RESET_ALL}"
    def _yellow(s: str) -> str: return f"{Fore.YELLOW}{s}{Style.RESET_ALL}"
    def _red(s: str)    -> str: return f"{Fore.RED}{s}{Style.RESET_ALL}"
    def _bold(s: str)   -> str: return f"{Style.BRIGHT}{s}{Style.RESET_ALL}"
    def _cyan(s: str)   -> str: return f"{Fore.CYAN}{s}{Style.RESET_ALL}"
except ImportError:
    def _green(s):  return s
    def _yellow(s): return s
    def _red(s):    return s
    def _bold(s):   return s
    def _cyan(s):   return s

# ─── Paths ────────────────────────────────────────────────────────────────────
_HERE      = os.path.dirname(os.path.abspath(__file__))
YAML_PATH  = os.path.join(_HERE, "resume_data.yaml")
OUTPUT_DIR = os.path.join(_HERE, "output")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _default_output(target: str) -> str:
    safe = target.replace(" ", "-").lower()
    return os.path.join(OUTPUT_DIR, f"resume_{safe}.pdf")


def _open_pdf(path: str) -> None:
    """Cross-platform PDF open."""
    import subprocess, platform
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", path])
        elif system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", path])
        print(_green(f"[PREVIEW] Opened {path}"))
    except Exception as exc:
        print(_yellow(f"[PREVIEW] Could not open PDF automatically: {exc}"))


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_list_targets() -> None:
    """Print all unique (non-general) tags found in the YAML."""
    from filter_engine import load_yaml, collect_all_tags
    try:
        data = load_yaml(YAML_PATH)
    except Exception as exc:
        print(_red(f"[ERROR] Failed to load YAML: {exc}"))
        sys.exit(1)

    tags = collect_all_tags(data)
    print(_bold("\nAvailable targets:"))
    for tag in tags:
        print(f"  {_cyan('•')} {tag}")
    print()


def cmd_targets_report() -> None:
    """Print a table of bullet/project/achievement/skill counts per target."""
    from filter_engine import load_yaml, targets_report
    try:
        data = load_yaml(YAML_PATH)
    except Exception as exc:
        print(_red(f"[ERROR] Failed to load YAML: {exc}"))
        sys.exit(1)

    report = targets_report(data)

    # Header
    col_w = [14, 9, 10, 14, 8]
    headers = ["Target", "Bullets", "Projects", "Achievements", "Skills"]
    print()
    print(_bold("  " + "  ".join(h.ljust(col_w[i]) for i, h in enumerate(headers))))
    print("  " + "  ".join("─" * w for w in col_w))

    for tag, counts in sorted(report.items()):
        row = [
            tag,
            str(counts["bullets"]),
            str(counts["projects"]),
            str(counts["achievements"]),
            str(counts["skills"]),
        ]
        print("  " + "  ".join(v.ljust(col_w[i]) for i, v in enumerate(row)))
    print()


def cmd_compile(args: argparse.Namespace) -> None:
    """Filter, render, and optionally commit/push/preview a resume PDF."""
    from filter_engine import build_resume_data
    from pdf_renderer import render_pdf
    import git_utils

    target = args.target
    output = args.output or _default_output(target)
    _ensure_output_dir()

    # 1. Filter & rank
    print(_bold(f"\n[1/3] Filtering resume data for target: {_cyan(target)}"))
    try:
        resume_data = build_resume_data(YAML_PATH, target)
    except FileNotFoundError:
        print(_red(f"[ERROR] resume_data.yaml not found at: {YAML_PATH}"))
        sys.exit(1)
    except Exception as exc:
        print(_red(f"[ERROR] Failed to load/filter YAML: {exc}"))
        sys.exit(1)

    _summarize_filtered(resume_data)

    # 2. Render PDF
    print(_bold(f"\n[2/3] Rendering PDF → {output}"))
    try:
        render_pdf(resume_data, output)
    except Exception as exc:
        print(_red(f"[ERROR] PDF rendering failed: {exc}"))
        sys.exit(1)
    print(_green(f"[SUCCESS] PDF written to: {output}"))

    # 3. Git commit
    print(_bold("\n[3/3] Git integration"))
    git_utils.git_commit(output, target)
    if args.push:
        git_utils.git_push(repo_path=_HERE)

    # 4. Preview (optional)
    if args.preview:
        _open_pdf(output)

    print(_green(f"\n✓ Done! Resume for '{target}' → {output}\n"))


def _summarize_filtered(data: dict) -> None:
    """Print a short summary of what survived filtering."""
    jobs     = len(data.get("experience", []))
    bullets  = sum(len(j.get("bullets", [])) for j in data.get("experience", []))
    projects = len(data.get("projects", []))
    skills   = sum(len(v) for v in data.get("skills", {}).values())
    achievements = len(data.get("achievements", []))
    print(f"  {_cyan('Jobs')}: {jobs}  |  {_cyan('Bullets')}: {bullets}  |  "
          f"{_cyan('Projects')}: {projects}  |  {_cyan('Skills')}: {skills}  |  "
          f"{_cyan('Achievements')}: {achievements}")


# ─── Argument parser ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compile_resume",
        description="Git-Driven Dynamic CV/Resume Compilation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compile_resume.py --target backend
  python compile_resume.py --target data-science --output ./output/resume_ds.pdf
  python compile_resume.py --target frontend --push --preview
  python compile_resume.py --list-targets
  python compile_resume.py --targets-report
""",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--target", "-t",
        metavar="ROLE",
        help="Target role to compile resume for (e.g. backend, data-science, frontend)",
    )
    group.add_argument(
        "--list-targets",
        action="store_true",
        help="List all unique tags found in resume_data.yaml and exit",
    )
    group.add_argument(
        "--targets-report",
        action="store_true",
        help="Print a table of content counts per target and exit",
    )

    parser.add_argument(
        "--output", "-o",
        metavar="PATH",
        default=None,
        help="Output PDF path (default: ./output/resume_<target>.pdf)",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        default=False,
        help="Push to remote after auto-commit (requires Git remote configured)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        default=False,
        help="Open the generated PDF immediately after creation",
    )

    return parser


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if args.list_targets:
        cmd_list_targets()
    elif args.targets_report:
        cmd_targets_report()
    else:
        cmd_compile(args)


if __name__ == "__main__":
    main()
