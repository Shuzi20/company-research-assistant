import json
import re
import httpx

from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

FALLBACK_MODEL = "anthropic/claude-3.5-sonnet"


def _extract_json(text: str) -> dict:
    """Handles cases where the model wraps JSON in markdown fences or adds preamble."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # If there's still leading/trailing junk, grab the outermost {...}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)


async def _call_openrouter(prompt: str, model: str) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=45) as client:
        resp = await client.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def generate_insights(prompt: str, model: str) -> dict:
    """
    Tries the user-selected model first. On any failure (bad model id, malformed
    JSON, timeout) falls back once to a known-stable model before giving up.
    """
    for attempt_model in [model, FALLBACK_MODEL]:
        try:
            raw = await _call_openrouter(prompt, attempt_model)
            return _extract_json(raw)
        except (json.JSONDecodeError, KeyError, IndexError):
            # Malformed response - try again with a stricter reminder, same model
            try:
                strict_prompt = prompt + "\n\nReturn ONLY the JSON object, nothing else."
                raw = await _call_openrouter(strict_prompt, attempt_model)
                return _extract_json(raw)
            except Exception:
                continue
        except Exception:
            continue

    raise RuntimeError("All OpenRouter attempts failed (primary and fallback model).")