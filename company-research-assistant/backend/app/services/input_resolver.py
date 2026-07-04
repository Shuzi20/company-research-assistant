import re
from urllib.parse import urlparse


def resolve(query: str) -> dict:
    """
    Returns {"type": "url", "value": normalized_url} or
            {"type": "name", "value": company_name}
    """
    query = query.strip()

    # Looks like it already has a scheme
    if re.match(r"^https?://", query, re.IGNORECASE):
        parsed = urlparse(query)
        if parsed.netloc:
            return {"type": "url", "value": query.rstrip("/")}

    # Looks like a bare domain, e.g. "stripe.com" or "www.tesla.com"
    domain_pattern = r"^(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/.*)?$"
    if re.match(domain_pattern, query):
        return {"type": "url", "value": f"https://{query.rstrip('/')}"}

    # Otherwise treat as a company name
    return {"type": "name", "value": query}