import json
import re
import httpx

from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL


def _log(message: str) -> None:
    print(f"[openrouter] {message}")

FALLBACK_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-20b:free",
    "qwen/qwen-2.5-7b-instruct:free",
]


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
        "max_tokens": 2048,
    }

    async with httpx.AsyncClient(timeout=45) as client:
        resp = await client.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def generate_insights(prompt: str, model: str) -> dict:
    """
    Tries the user-selected model first, then walks through a chain of free
    fallback models. A single model being rate-limited or unavailable never
    fails the whole request - it just moves to the next candidate.
    """
    candidates = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_error = None

    for attempt_model in candidates:
        try:
            raw = await _call_openrouter(prompt, attempt_model)
            return _extract_json(raw)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            _log(f"model={attempt_model} returned malformed JSON ({e}); retrying with stricter prompt")
            try:
                strict_prompt = prompt + "\n\nReturn ONLY the JSON object, nothing else."
                raw = await _call_openrouter(strict_prompt, attempt_model)
                return _extract_json(raw)
            except Exception as e2:
                last_error = e2
                _log(f"model={attempt_model} retry also failed: {e2}")
                continue
        except httpx.HTTPStatusError as e:
            last_error = e
            _log(f"model={attempt_model} HTTP {e.response.status_code}: {e.response.text}")
            continue
        except Exception as e:
            last_error = e
            _log(f"model={attempt_model} failed: {type(e).__name__}: {e}")
            continue

    raise RuntimeError(f"All OpenRouter attempts failed across {len(candidates)} models. Last error: {last_error}")