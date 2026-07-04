from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.services import discord_sender

router = APIRouter()


class DiscordSendRequest(BaseModel):
    bot_token: str
    channel_id: str
    applicant_name: str
    applicant_email: str
    company_name: str
    company_website: str | None = None
    pdf_base64: str  # the data URI returned by /api/research


async def _send_safely(payload: DiscordSendRequest):
    """Wrapped so a failure here only logs - it must never crash a background task silently."""
    try:
        await discord_sender.send_report(
            bot_token=payload.bot_token,
            channel_id=payload.channel_id,
            applicant_name=payload.applicant_name,
            applicant_email=payload.applicant_email,
            company_name=payload.company_name,
            company_website=payload.company_website or "",
            pdf_base64=payload.pdf_base64,
        )
    except Exception as e:
        print(f"[discord_sender] failed to send report: {e}")


@router.post("/discord/send")
async def send_to_discord(payload: DiscordSendRequest, background_tasks: BackgroundTasks):
    if not payload.bot_token or not payload.channel_id:
        raise HTTPException(status_code=400, detail="bot_token and channel_id are required.")

    # Fire-and-forget: frontend gets an immediate ack, actual send happens after response.
    background_tasks.add_task(_send_safely, payload)
    return {"status": "queued"}