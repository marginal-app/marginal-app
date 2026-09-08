#!/usr/bin/env python3
"""Capture raw silhouette PNGs into apps/api/.silhouettes/ (gitignored).

Playwright clips the `.silhouette` panel. Requires `manage.py runserver`
and a Chromium install (`uv run playwright install chromium`).

    uv run python scripts/capture_silhouette.py empty-state
    uv run python scripts/capture_silhouette.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parent.parent
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


def repo_api_dir() -> Path:
    return API_DIR


def _slugs_from_catalog() -> list[str]:
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()
    from citry_preview.previews import PREVIEWS

    return [preview.slug for preview in PREVIEWS]


def main() -> int:
    from citry_preview.capture import DEFAULT_BASE_URL, capture_silhouette

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "slugs",
        nargs="*",
        help="Preview slugs from the gallery catalog",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Capture every discovered example. Does not compare goldens.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=repo_api_dir() / ".silhouettes",
    )
    args = parser.parse_args()
    slugs = list(args.slugs)
    if args.all:
        slugs.extend(_slugs_from_catalog())
    if not slugs:
        parser.error("provide slugs or --all")
    for slug in slugs:
        dest = capture_silhouette(slug, base_url=args.base_url, out_dir=args.out_dir)
        print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
