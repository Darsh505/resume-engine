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

    Gitignore behaviour
    ───────────────────
    If *output_path* is untracked and covered by a ``.gitignore`` rule,
    this function skips staging and returns False with a yellow notice.

    Important limitation: ``repo.ignored()`` only reports files that git
    considers *untracked*.  If a file is already tracked by git (i.e. it
    appears in ``git ls-files``), git does not consider it ignored even if
    it matches a ``.gitignore`` pattern — and neither does this check.
    Already-tracked files that should be untracked require a separate
    ``git rm --cached <path>`` step to sever tracking first.
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

        # Respect .gitignore: if the file is untracked and covered by an
        # ignore rule, skip rather than staging it.
        #
        # repo.ignored() returns a non-empty list only for files that are
        # *not* already tracked by git.  For already-tracked files it always
        # returns [] regardless of .gitignore contents — those require
        # `git rm --cached` to untrack before this check takes effect.
        if repo.ignored(rel_path):
            print(_yellow(
                f"[GIT] {rel_path} is gitignored — skipping auto-commit.\n"
                f"      To re-enable PDF version history, remove 'output/*.pdf'\n"
                f"      from .gitignore, then run: git rm --cached output/*.pdf"
            ))
            return False

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
