#!/usr/bin/env python3
"""Capture raw silhouette PNGs into apps/api/.silhouettes/ (gitignored).

Requires `manage.py runserver` on BASE_URL (default http://127.0.0.1:8000).

    uv run python scripts/capture_silhouette.py button-default button-small
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

CHROME = "google-chrome"
DEFAULT_BASE = "http://127.0.0.1:8000"
WINDOW = "420,800"


def repo_api_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def capture(slug: str, *, base_url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{slug}.png"
    url = f"{base_url.rstrip('/')}/dev/components/{slug}/"
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-sandbox",
        f"--window-size={WINDOW}",
        f"--screenshot={dest}",
        url,
    ]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0 or not dest.is_file():
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(f"Failed to capture {url} -> {dest}")
    print(dest)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="+", help="Example slugs from the gallery catalog")
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=repo_api_dir() / ".silhouettes",
    )
    args = parser.parse_args()
    for slug in args.slugs:
        capture(slug, base_url=args.base_url, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
