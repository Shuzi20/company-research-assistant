import asyncio
from app.models.schemas import Competitor
from app.services.serper import domain_exists


async def validate(raw_competitors: list[dict]) -> list[Competitor]:
    if not raw_competitors:
        return []

    checks = await asyncio.gather(
        *[domain_exists(c.get("website", "")) for c in raw_competitors],
        return_exceptions=True,
    )

    validated: list[Competitor] = []
    for competitor, is_valid in zip(raw_competitors, checks):
        if is_valid is True:
            validated.append(
                Competitor(name=competitor.get("name", "Unknown"), website=competitor.get("website"))
            )
        else:
            # Keep the name but drop the unverifiable link rather than showing a dead URL
            validated.append(Competitor(name=competitor.get("name", "Unknown"), website=None))

    return validated