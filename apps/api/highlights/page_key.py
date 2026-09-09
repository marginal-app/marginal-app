from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class PageIdentity:
    origin: str
    path: str
    query: str
    page_key: str


def page_key_from_href(href: str) -> str | None:
    parsed = urlparse(href)
    if not parsed.scheme or not parsed.netloc:
        return None
    origin = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path if parsed.path else "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{origin}{path}{query}"


def canonicalize_page_key(page_key: str) -> str:
    return page_key_from_href(page_key) or page_key


def page_identity_from_page_key(page_key: str) -> PageIdentity:
    canonical = canonicalize_page_key(page_key)
    parsed = urlparse(canonical)
    if not parsed.scheme or not parsed.netloc:
        return PageIdentity(origin="", path=canonical, query="", page_key=canonical)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path if parsed.path else "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return PageIdentity(origin=origin, path=path, query=query, page_key=f"{origin}{path}{query}")
