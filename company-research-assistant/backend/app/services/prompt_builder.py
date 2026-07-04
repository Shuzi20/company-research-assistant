def build(company_name: str, website: str | None, crawled_content: str, extra_info: str) -> str:
    return f"""You are a business research analyst. Analyze the information below about
"{company_name}" ({website or "website unknown"}) and return ONLY valid JSON,
no preamble, no markdown fences, matching exactly this shape:

{{
  "summary": "2-3 sentence company summary",
  "products_services": ["short item", "short item"],
  "pain_points": ["specific pain point 1", "specific pain point 2", "specific pain point 3"],
  "competitors": [{{"name": "Competitor Name", "website": "https://example.com"}}]
}}

Rules:
- pain_points should be specific and business-relevant, not generic.
- competitors must be real companies in the same industry/country, with plausible websites.
- If information is missing, use reasonable inference but do not fabricate specific numbers.
- Return ONLY the JSON object.

WEBSITE CONTENT:
{crawled_content}

ADDITIONAL PUBLIC INFO:
{extra_info}
"""