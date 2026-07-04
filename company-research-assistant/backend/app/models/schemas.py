from typing import List, Optional
from pydantic import BaseModel


class ResearchRequest(BaseModel):
    query: str
    model: Optional[str] = "anthropic/claude-3.5-sonnet"


class Competitor(BaseModel):
    name: str
    website: Optional[str] = None
    reason: Optional[str] = None


class CompanyData(BaseModel):
    company_name: str

    website: Optional[str] = None
    phone: Optional[str] = "Not publicly listed"
    address: Optional[str] = "Not publicly listed"

    industry: Optional[str] = None
    summary: Optional[str] = None
    business_model: Optional[str] = None

    target_customers: List[str] = []

    products_services: List[str] = []

    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []

    pain_points: List[str] = []

    competitors: List[Competitor] = []


class ResearchResponse(BaseModel):
    data: CompanyData
    warnings: List[str] = []
    pdf_url: Optional[str] = None