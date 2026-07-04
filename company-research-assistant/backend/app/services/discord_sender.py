import base64
import json
import httpx


def _decode_pdf(pdf_data_uri: str) -> bytes:
    """Accepts a data URI like 'data:application/pdf;base64,...' or a raw base64 string."""
    if "," in pdf_data_uri:
        pdf_data_uri = pdf_data_uri.split(",", 1)[1]
    return base64.b64decode(pdf_data_uri)


async def send_report(
    bot_token: str,
    channel_id: str,
    applicant_name: str,
    applicant_email: str,
    company_name: str,
    company_website: str,
    pdf_base64: str,
) -> None:
    """
    Uploads the generated PDF to the configured Discord channel via the bot API.
    Fire-and-forget by design: called from a BackgroundTask so a Discord failure
    never affects the main /research response the user already received.

    BUG FIX: the Discord multipart "payload_json" field was previously built
    by hand-interpolating strings into a JSON-looking literal and only
    escaping newlines:

        f'{{"content": "{message_content}"}}'.replace("\\n", "\\\\n")

    Any applicant name, company name, or email containing a double quote,
    backslash, or other JSON-special character (e.g. an applicant named
    O'Brien "the closer" Smith) produced invalid JSON, which Discord's API
    rejects outright - so the whole notification silently failed for any
    input that wasn't perfectly plain text. We now build a real dict and
    serialize it with json.dumps, which escapes everything correctly.
    """
    if not bot_token or not channel_id:
        raise ValueError("Discord bot token and channel ID are required.")

    pdf_bytes = _decode_pdf(pdf_base64)
    filename = f"{company_name.replace(' ', '_').lower()}-research-report.pdf"

    message_content = (
        f"**New research report generated**\n"
        f"Applicant: {applicant_name} ({applicant_email})\n"
        f"Company: {company_name}\n"
        f"Website: {company_website or 'N/A'}"
    )

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {bot_token}"}

    payload_json = json.dumps({"content": message_content})

    files = {
        "payload_json": (None, payload_json, "application/json"),
        "file": (filename, pdf_bytes, "application/pdf"),
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, headers=headers, files=files)
        resp.raise_for_status()