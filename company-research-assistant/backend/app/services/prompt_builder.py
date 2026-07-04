def build(company_name: str, website: str | None, crawled_content: str, extra_info: str) -> str:
    return f"""
You are a senior business analyst and competitive intelligence researcher.

Analyze the company below using the website content and public information provided.

Return ONLY valid JSON matching EXACTLY this structure:

{{
  "company_name": "",
  "industry": "",
  "summary": "",
  "business_model": "",
  "target_customers": [],
  "products_services": [],
  "strengths": [],
  "weaknesses": [],
  "opportunities": [],
  "threats": [],
  "pain_points": [],
  "competitors": [
    {{
      "name": "",
      "website": "",
      "reason": ""
    }}
  ]
}}

Rules:

- company_name must be the real business name, never a URL.
- industry should be concise.
- summary should be 3-5 sentences.
- business_model should explain how the company generates revenue.
- target_customers should identify likely customer segments.
- strengths, weaknesses, opportunities and threats should be company-specific.
- pain_points should be based on the company and industry, not generic business advice.
- competitors must be real companies.
- competitor reason must explain why they compete.
- Do NOT invent revenue numbers or employee counts.
- Use website content whenever possible.
- Return ONLY JSON.

WEBSITE CONTENT:
{crawled_content[:25000]}

ADDITIONAL PUBLIC INFO:
{extra_info}
"""