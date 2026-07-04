import httpx
from app.config import SERPER_API_KEY, SERPER_BASE_URL


async def _serper_search(query: str, num: int = 5) -> dict:
    if not SERPER_API_KEY:
        raise RuntimeError("SERPER_API_KEY is not configured.")

    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num}

    async with httpx.AsyncClient(timeout=8) as client:
        resp = await client.post(f"{SERPER_BASE_URL}/search", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


async def find_official_website(company_name: str) -> str | None:
    """Search for the company and return the most likely official domain."""
    data = await _serper_search(f"{company_name} official website")
    organic = data.get("organic", [])
    if not organic:
        return None

    # Naive but effective heuristic: first organic result is usually the official site.
    # Could be improved by filtering out known aggregator domains (linkedin, crunchbase, wikipedia).
    blocked_domains = ["linkedin.com", "wikipedia.org", "crunchbase.com", "glassdoor.com"]
    for result in organic:
        link = result.get("link", "")
        if link and not any(b in link for b in blocked_domains):
            return link
    return organic[0].get("link")


async def gather_public_info(company_name: str) -> str:
    """Best-effort extra context: knowledge graph snippet + top organic snippets."""
    data = await _serper_search(f"{company_name} company")
    pieces = []

    kg = data.get("knowledgeGraph")
    if kg:
        desc = kg.get("description")
        if desc:
            pieces.append(desc)

    for result in data.get("organic", [])[:3]:
        snippet = result.get("snippet")
        if snippet:
            pieces.append(snippet)

    return "\n".join(pieces)


async def domain_exists(url: str) -> bool:
    """Lightweight check used by competitor_validator - confirms a URL resolves."""
    try:
        async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
            resp = await client.head(url)
            return resp.status_code < 400
    except Exception:
        return False