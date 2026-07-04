from typing import List, Optional
from pydantic import BaseModel


class ResearchRequest(BaseModel):
    query: str  # company name OR website URL
    model: Optional[str] = "anthropic/claude-3.5-sonnet"


class Competitor(BaseModel):
    name: str
    website: Optional[str] = None


class CompanyData(BaseModel):
    company_name: str
    website: Optional[str] = None
    phone: Optional[str] = "Not publicly listed"
    address: Optional[str] = "Not publicly listed"
    products_services: List[str] = []
    pain_points: List[str] = []
    competitors: List[Competitor] = []


class ResearchResponse(BaseModel):
    data: CompanyData
    warnings: List[str] = []   # non-fatal issues encountered per stage
    pdf_url: Optional[str] = None