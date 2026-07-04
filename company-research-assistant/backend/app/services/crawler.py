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
    """Strip fragment/query/trailing slash so we don't re-crawl the same page twice."""
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    return normalized.lower()


def _is_ignored(url: str) -> bool:
    lowered = url.lower()
    return any(kw in lowered for kw in IGNORED_PATH_KEYWORDS)


def _is_priority(url: str) -> bool:
    lowered = url.lower()
    return any(kw in lowered for kw in PRIORITY_PATH_KEYWORDS)


async def _fetch_page(client: httpx.AsyncClient, url: str) -> dict | None:
    """Fetch a single page. Returns None on any failure - never raises."""
    try:
        resp = await client.get(url, timeout=CRAWL_TIMEOUT_SECONDS, follow_redirects=True)
        content_type = resp.headers.get("content-type", "")
        if resp.status_code >= 400 or "text/html" not in content_type:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        links = [urljoin(url, a.get("href")) for a in soup.find_all("a", href=True)]

        return {"url": url, "text": text, "links": links}
    except Exception:
        return None


async def crawl_website(start_url: str, max_pages: int = MAX_PAGES_TO_CRAWL) -> list[dict]:
    """
    Discovers and crawls up to `max_pages` relevant pages on the same domain.
    Uses asyncio.gather with return_exceptions so one bad page never kills the crawl.
    """
    domain = urlparse(start_url).netloc
    visited: set[str] = set()
    results: list[dict] = []

    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}) as client:
        # First fetch the homepage to discover internal links
        home = await _fetch_page(client, start_url)
        if not home:
            return results

        visited.add(_normalize_url(start_url))
        results.append(home)

        # Rank discovered links: priority pages first, then everything else, skip ignored
        candidate_links = []
        for link in home["links"]:
            parsed = urlparse(link)
            if parsed.netloc != domain:
                continue
            norm = _normalize_url(link)
            if norm in visited or _is_ignored(link):
                continue
            candidate_links.append(link)

        candidate_links.sort(key=lambda l: (not _is_priority(l), l))
        remaining_slots = max_pages - 1
        to_fetch = []
        seen_norm = set(visited)
        for link in candidate_links:
            norm = _normalize_url(link)
            if norm in seen_norm:
                continue
            seen_norm.add(norm)
            to_fetch.append(link)
            if len(to_fetch) >= remaining_slots:
                break

        # Fetch remaining pages concurrently; failures return None and are filtered out
        fetched = await asyncio.gather(*[_fetch_page(client, link) for link in to_fetch])
        for page in fetched:
            if page:
                results.append(page)

    return results