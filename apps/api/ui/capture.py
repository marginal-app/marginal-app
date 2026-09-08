"""Clip the 360px `.silhouette` panel. Review attach uses this; CI does not compare goldens yet."""

from __future__ import annotations

from pathlib import Path

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
SILHOUETTE_SELECTOR = ".silhouette"
VIEWPORT = {"width": 420, "height": 900}


def silhouette_url(base_url: str, slug: str) -> str:
    return f"{base_url.rstrip('/')}/citry/preview/{slug}/"


def dest_path(out_dir: Path, slug: str) -> Path:
    return out_dir / f"{slug}.png"


def capture_silhouette(
    slug: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    out_dir: Path,
) -> Path:
    """Open the raw silhouette URL and write a PNG of `.silhouette` only."""
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    out_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_path(out_dir, slug)
    url = silhouette_url(base_url, slug)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            page = browser.new_page(viewport=VIEWPORT)
            page.goto(url, wait_until="networkidle")
            panel = page.locator(SILHOUETTE_SELECTOR)
            panel.wait_for(state="visible")
            panel.screenshot(path=str(dest), animations="disabled")
            browser.close()
    except PlaywrightError as exc:
        hint = ""
        if "Executable doesn't exist" in str(exc):
            hint = "\nInstall the browser with: uv run playwright install chromium"
        raise SystemExit(f"Failed to capture {url} -> {dest}{hint}\n{exc}") from exc
    if not dest.is_file():
        raise SystemExit(f"Failed to capture {url} -> {dest}")
    return dest
