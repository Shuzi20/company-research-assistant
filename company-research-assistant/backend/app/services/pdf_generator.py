import base64
from io import BytesIO
from fpdf import FPDF

from app.models.schemas import CompanyData


def generate(data: CompanyData) -> str:
    """
    Builds a single-page-ish PDF report and returns it as a base64 data URI.
    No disk writes - keeps this stateless and safe for Vercel's serverless
    filesystem, and avoids needing any storage/database per the assignment
    constraints (no permanent database, no report history required).
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, data.company_name, ln=True)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 8, "Relu Consultancy - Company Research Report", ln=True)
    pdf.ln(4)

    def section_title(title: str):
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Helvetica", "", 11)

    def kv_line(label: str, value: str):
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 7, f"{label}: {value}")

    section_title("Company information")
    kv_line("Website", data.website or "Not found")
    kv_line("Phone", data.phone or "Not publicly listed")
    kv_line("Address", data.address or "Not publicly listed")
    pdf.ln(3)

    section_title("Products & services")
    if data.products_services:
        for item in data.products_services:
            pdf.multi_cell(0, 7, f"- {item}")
    else:
        pdf.multi_cell(0, 7, "Not available")
    pdf.ln(3)

    section_title("AI-generated pain points")
    if data.pain_points:
        for point in data.pain_points:
            pdf.multi_cell(0, 7, f"- {point}")
    else:
        pdf.multi_cell(0, 7, "Not available")
    pdf.ln(3)

    section_title("Competitors")
    if data.competitors:
        for comp in data.competitors:
            website = comp.website or "Website unverified"
            pdf.multi_cell(0, 7, f"{comp.name} - {website}")
    else:
        pdf.multi_cell(0, 7, "Not available")

    buffer = BytesIO()
    pdf.output(buffer)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:application/pdf;base64,{encoded}"