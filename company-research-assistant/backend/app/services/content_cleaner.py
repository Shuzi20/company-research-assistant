def prepare_for_llm(crawled_pages: list[dict], max_chars_per_page: int = 2500) -> str:
    """
    No embeddings, no RAG - just discipline: truncate each page and
    concatenate with a source header so the AI knows where content came from.
    """
    if not crawled_pages:
        return ""

    blocks = []
    for page in crawled_pages:
        url = page.get("url", "unknown page")
        text = page.get("text", "").strip()
        if not text:
            continue
        truncated = text[:max_chars_per_page]
        blocks.append(f"--- Source: {url} ---\n{truncated}")

    combined = "\n\n".join(blocks)

    # Hard ceiling as a final safety net regardless of page count
    overall_limit = 16000
    return combined[:overall_limit]