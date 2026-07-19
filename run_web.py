#!/usr/bin/env python3
"""
run_web.py — Convenience script to start the Resume Engine web server.

Usage (from the project root):
    python run_web.py          # production-like, port 8000
    python run_web.py --dev    # hot-reload, verbose logs

Or run uvicorn directly:
    uvicorn web.app:app --reload --port 8000
"""
from __future__ import annotations

import sys
import uvicorn


def main() -> None:
    dev = "--dev" in sys.argv
    uvicorn.run(
        "web.app:app",
        host="127.0.0.1",
        port=8000,
        reload=dev,
        log_level="debug" if dev else "info",
    )


if __name__ == "__main__":
    main()
