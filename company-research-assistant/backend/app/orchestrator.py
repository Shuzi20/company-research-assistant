"""
Orchestrator: runs the full research pipeline.

Design principle (from the architecture discussion):
Each stage is wrapped in its own try/except. A stage failing appends a
warning and falls back to partial/default data - it never crashes the
whole pipeline. The final response always returns whatever was
successfully gathered.
"""

from typing import List

from app.models.schemas import CompanyData, Competitor, ResearchResponse
from app.services import (
    input_resolver,
    serper,
    crawler,
    content_cleaner,
    prompt_builder,
    openrouter,
    competitor_validator,
    pdf_generator,
)


async def run_research(query: str, model: str) -> ResearchResponse:
    warnings: List[str] = []

    # ---------- Stage 1: resolve input (name vs URL) ----------
    try:
        resolved = input_resolver.resolve(query)
        # resolved = {"type": "url"|"name", "value": str}
    except Exception as e:
        warnings.append(f"Input resolution failed, treating input as raw text: {e}")
        resolved = {"type": "name", "value": query}

    # ---------- Stage 2: find official website (only if name given) ----------
    website_url = None
    if resolved["type"] == "url":
        website_url = resolved["value"]
    else:
        try:
            website_url = await serper.find_official_website(resolved["value"])
        except Exception as e:
            warnings.append(f"Search engine lookup failed: {e}")

    if not website_url:
        warnings.append("Could not determine an official website; crawling skipped.")

    # ---------- Stage 3: crawl website ----------
    crawled_pages = []
    if website_url:
        try:
            crawled_pages = await crawler.crawl_website(website_url, max_pages=8)
        except Exception as e:
            warnings.append(f"Crawling failed or partially failed: {e}")

    # ---------- Stage 4: clean + truncate content before sending to AI ----------
    try:
        cleaned_content = content_cleaner.prepare_for_llm(crawled_pages, max_chars_per_page=2500)
    except Exception as e:
        warnings.append(f"Content cleaning failed, using raw crawl text: {e}")
        cleaned_content = "\n\n".join(p.get("text", "") for p in crawled_pages)[:8000]

    # ---------- Stage 5: extra public info via search (best-effort) ----------
    extra_info = ""
    try:
        extra_info = await serper.gather_public_info(resolved.get("value", query))
    except Exception as e:
        warnings.append(f"Additional public search failed: {e}")

    # ---------- Stage 6: AI analysis (OpenRouter) ----------
    company_name = resolved["value"] if resolved["type"] == "name" else (website_url or query)
    ai_result = None
    try:
        prompt = prompt_builder.build(
            company_name=company_name,
            website=website_url,
            crawled_content=cleaned_content,
            extra_info=extra_info,
        )
        ai_result = await openrouter.generate_insights(prompt, model=model)
    except Exception as e:
        warnings.append(f"AI analysis failed: {e}")

    if not ai_result:
        # Fallback: return whatever raw data we have, no AI-derived fields
        ai_result = {
            "summary": None,
            "products_services": [],
            "pain_points": [],
            "competitors": [],
        }

    # ---------- Stage 7: validate competitors ----------
    validated_competitors: List[Competitor] = []
    try:
        validated_competitors = await competitor_validator.validate(ai_result.get("competitors", []))
    except Exception as e:
        warnings.append(f"Competitor validation failed, showing unverified list: {e}")
        validated_competitors = [
            Competitor(name=c.get("name", "Unknown"), website=c.get("website"))
            for c in ai_result.get("competitors", [])
        ]

    # ---------- Assemble final data ----------
    data = CompanyData(
        company_name=company_name,
        website=website_url,
        phone="Not publicly listed",
        address="Not publicly listed",
        products_services=ai_result.get("products_services", []),
        pain_points=ai_result.get("pain_points", []),
        competitors=validated_competitors,
    )

    # ---------- Stage 8: generate PDF (best-effort, never blocks the response) ----------
    pdf_url = None
    try:
        pdf_url = pdf_generator.generate(data)
    except Exception as e:
        warnings.append(f"PDF generation failed: {e}")

    return ResearchResponse(data=data, warnings=warnings, pdf_url=pdf_url)