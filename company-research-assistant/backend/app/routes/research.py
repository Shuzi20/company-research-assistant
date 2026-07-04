from fastapi import APIRouter, HTTPException

from app.models.schemas import ResearchRequest, ResearchResponse
from app.orchestrator import run_research

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
async def research_company(payload: ResearchRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query (company name or URL) is required.")

    result = await run_research(query=query, model=payload.model)
    return result