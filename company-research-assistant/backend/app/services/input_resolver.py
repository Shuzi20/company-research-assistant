import re
from urllib.parse import urlparse


def resolve(query: str) -> dict:
    """
    Returns {"type": "url", "value": normalized_url} or
            {"type": "name", "value": company_name}

    BUG FIX: the bare-domain regex only allowed a single label before the
    TLD ([a-zA-Z0-9-]+\\.[a-zA-Z]{2,}), so it matched "stripe.com" but not
    "mail.google.com" or "sub.example.co.in" - anything with a subdomain
    or multi-part TLD fell through to "treat as a company name" and never
    got resolved as a URL. The pattern now allows one or more dot-
    separated labels before the final TLD segment.
    """
    query = query.strip()

    # Looks like it already has a scheme
    if re.match(r"^https?://", query, re.IGNORECASE):
        parsed = urlparse(query)
        if parsed.netloc:
            return {"type": "url", "value": query.rstrip("/")}

    # Looks like a bare domain, e.g. "stripe.com", "www.tesla.com",
    # "mail.google.com", or "sub.example.co.in"
    domain_pattern = r"^(www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$"
    if re.match(domain_pattern, query):
        return {"type": "url", "value": f"https://{query.rstrip('/')}"}

    # Otherwise treat as a company name
    return {"type": "name", "value": query}