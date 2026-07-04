import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app.config import (
    MAX_PAGES_TO_CRAWL,
    CRAWL_TIMEOUT_SECONDS,
    PRIORITY_PATH_KEYWORDS,
    IGNORED_PATH_KEYWORDS,
)


def _normalize_url(url: str) -> str:
    """Remove query params, fragments and trailing slash."""
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    return normalized.lower()


def _normalize_domain(netloc: str) -> str:
    """Treat example.com and www.example.com as same."""
    return netloc.lower().removeprefix("www.")


def _is_ignored(url: str) -> bool:
    lowered = url.lower()

    if any(kw in lowered for kw in IGNORED_PATH_KEYWORDS):
        return True

    blocked_extensions = (
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".zip",
        ".rar",
        ".mp4",
        ".mp3",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    )

    if lowered.endswith(blocked_extensions):
        return True

    if lowered.startswith("mailto:"):
        return True

    if lowered.startswith("tel:"):
        return True

    if lowered.startswith("javascript:"):
        return True

    return False


def _is_priority(url: str) -> bool:
    lowered = url.lower()
    return any(keyword in lowered for keyword in PRIORITY_PATH_KEYWORDS)


async def _fetch_page(client: httpx.AsyncClient, url: str) -> dict | None:
    """
    Fetch a page safely.
    Never throws exceptions.
    """

    try:
        response = await client.get(
            url,
            timeout=CRAWL_TIMEOUT_SECONDS,
            follow_redirects=True,
        )

        content_type = response.headers.get("content-type", "")

        if response.status_code >= 400:
            return None

        if "text/html" not in content_type:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "noscript",
            "svg",
            "iframe",
            "form",
            "header",
        ]):
            tag.decompose()

        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        text = soup.get_text(separator=" ", strip=True)

        # Remove excessive whitespace
        text = " ".join(text.split())

        # Limit content size
        text = text[:8000]

        final_url = str(response.url)

        links = [
            urljoin(final_url, a.get("href"))
            for a in soup.find_all("a", href=True)
        ]

        return {
            "url": final_url,
            "title": title,
            "text": text,
            "links": links,
        }

    except Exception:
        return None


async def crawl_website(
    start_url: str,
    max_pages: int = MAX_PAGES_TO_CRAWL,
) -> list[dict]:
    """
    Crawl homepage + important internal pages.

    Returns:
    [
        {
            "url": "...",
            "title": "...",
            "text": "...",
            "links": [...]
        }
    ]
    """

    visited: set[str] = set()
    results: list[dict] = []

    async with httpx.AsyncClient(
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; CompanyResearchBot/1.0)"
            )
        }
    ) as client:

        homepage = await _fetch_page(client, start_url)

        if not homepage:
            return results

        domain = _normalize_domain(
            urlparse(homepage["url"]).netloc
        )

        visited.add(_normalize_url(homepage["url"]))
        results.append(homepage)

        candidate_links = []

        for link in homepage["links"]:

            if _is_ignored(link):
                continue

            parsed = urlparse(link)

            if _normalize_domain(parsed.netloc) != domain:
                continue

            normalized = _normalize_url(link)

            if normalized in visited:
                continue

            candidate_links.append(link)

        # Priority pages first
        candidate_links.sort(
            key=lambda url: (
                not _is_priority(url),
                url,
            )
        )

        remaining_slots = max_pages - 1

        to_fetch = []
        seen_urls = set(visited)

        for link in candidate_links:

            normalized = _normalize_url(link)

            if normalized in seen_urls:
                continue

            seen_urls.add(normalized)

            to_fetch.append(link)

            if len(to_fetch) >= remaining_slots:
                break

        fetched_pages = await asyncio.gather(
            *[_fetch_page(client, url) for url in to_fetch],
            return_exceptions=True,
        )

        for page in fetched_pages:

            if isinstance(page, Exception):
                continue

            if page:
                results.append(page)

    return results