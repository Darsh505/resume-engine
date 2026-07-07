"""
git_utils.py — Automatic Git staging, committing, and pushing after PDF generation.

Uses the 'gitpython' library.  Gracefully skips if the directory is not a Git repo.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone


def _get_repo(repo_path: str):
    """Return a git.Repo object or None if not a Git repo / gitpython missing."""
    try:
        import git
        return git.Repo(repo_path, search_parent_directories=True)
    except Exception:
        return None


def git_commit(output_path: str, target: str, repo_path: str | None = None) -> bool:
    """
    Stage *output_path* and commit with a descriptive message.

    Returns True on success, False if skipped/failed.
    """
    try:
        from colorama import Fore, Style
        _green  = lambda s: f"{Fore.GREEN}{s}{Style.RESET_ALL}"
        _yellow = lambda s: f"{Fore.YELLOW}{s}{Style.RESET_ALL}"
        _red    = lambda s: f"{Fore.RED}{s}{Style.RESET_ALL}"
    except ImportError:
        _green = _yellow = _red = lambda s: s

    search_dir = repo_path or os.path.dirname(os.path.abspath(output_path))
    repo = _get_repo(search_dir)

    if repo is None:
        print(_yellow("[GIT] Directory is not a Git repository — skipping auto-commit."), file=sys.stderr)
        return False

    # Stage the file (path relative to repo root)
    try:
        rel_path = os.path.relpath(os.path.abspath(output_path), repo.working_tree_dir)
        repo.index.add([rel_path])
    except Exception as exc:
        print(_red(f"[GIT] Failed to stage {output_path}: {exc}"), file=sys.stderr)
        return False

    # Commit
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    message   = f"chore: regenerate resume for {target} — {timestamp}"
    try:
        repo.index.commit(message)
        print(_green(f"[GIT] Committed: {message}"))
        return True
    except Exception as exc:
        print(_red(f"[GIT] Commit failed: {exc}"), file=sys.stderr)
        return False


def git_push(repo_path: str | None = None) -> bool:
    """
    Push the current branch to its upstream remote.

    Returns True on success, False if skipped/failed.
    """
    try:
        from colorama import Fore, Style
        _green  = lambda s: f"{Fore.GREEN}{s}{Style.RESET_ALL}"
        _yellow = lambda s: f"{Fore.YELLOW}{s}{Style.RESET_ALL}"
        _red    = lambda s: f"{Fore.RED}{s}{Style.RESET_ALL}"
    except ImportError:
        _green = _yellow = _red = lambda s: s

    search_dir = repo_path or os.getcwd()
    repo = _get_repo(search_dir)

    if repo is None:
        print(_yellow("[GIT] Not a Git repository — skipping push."), file=sys.stderr)
        return False

    try:
        origin = repo.remote(name="origin")
        push_info = origin.push()
        for info in push_info:
            print(_green(f"[GIT] Pushed: {info.summary}"))
        return True
    except Exception as exc:
        print(_red(f"[GIT] Push failed: {exc}"), file=sys.stderr)
        return False
