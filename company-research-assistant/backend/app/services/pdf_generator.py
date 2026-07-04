import base64
from io import BytesIO

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.models.schemas import CompanyData


_UNICODE_TO_ASCII = {
    "\u2010": "-",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2026": "...",
    "\u00a0": " ",
    "\u2022": "-",
}


def _sanitize(text: str | None) -> str:
    if not text:
        return ""

    for unicode_char, ascii_char in _UNICODE_TO_ASCII.items():
        text = text.replace(unicode_char, ascii_char)

    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate(data: CompanyData) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ---------- Header ----------
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(
        0,
        12,
        _sanitize(data.company_name),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(90, 90, 90)

    pdf.cell(
        0,
        8,
        "Relu Consultancy - Company Research Report",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.ln(4)

    # ---------- Helpers ----------

    def section_title(title: str):
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("Helvetica", "B", 14)

        pdf.cell(
            0,
            10,
            _sanitize(title),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

        pdf.set_font("Helvetica", "", 11)

    def kv_line(label: str, value: str):
        if not value:
            return

        pdf.multi_cell(
            0,
            7,
            _sanitize(f"{label}: {value}"),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def paragraph(text: str):
        if not text:
            return

        pdf.multi_cell(
            0,
            7,
            _sanitize(text),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def bullet(text: str):
        pdf.multi_cell(
            0,
            7,
            _sanitize(f"- {text}"),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def bullet_section(title: str, items: list):
        if not items:
            return

        section_title(title)

        for item in items:
            bullet(str(item))

        pdf.ln(2)

    # ---------- Company Information ----------

    section_title("Company Information")

    kv_line("Website", data.website or "")

    if getattr(data, "phone", None):
        kv_line("Phone", data.phone)

    if getattr(data, "address", None):
        kv_line("Address", data.address)

    if getattr(data, "industry", None):
        kv_line("Industry", data.industry)

    pdf.ln(3)

    # ---------- Executive Summary ----------

    if getattr(data, "summary", None):
        section_title("Executive Summary")
        paragraph(data.summary)
        pdf.ln(3)

    # ---------- Business Model ----------

    if getattr(data, "business_model", None):
        section_title("Business Model")
        paragraph(data.business_model)
        pdf.ln(3)

    # ---------- Target Customers ----------

    if getattr(data, "target_customers", None):
        bullet_section(
            "Target Customers",
            data.target_customers,
        )

    # ---------- Products ----------

    if data.products_services:
        bullet_section(
            "Products & Services",
            data.products_services,
        )

    # ---------- SWOT ----------

    bullet_section(
        "Strengths",
        getattr(data, "strengths", []),
    )

    bullet_section(
        "Weaknesses",
        getattr(data, "weaknesses", []),
    )

    bullet_section(
        "Opportunities",
        getattr(data, "opportunities", []),
    )

    bullet_section(
        "Threats",
        getattr(data, "threats", []),
    )

    # ---------- Pain Points ----------

    if data.pain_points:
        bullet_section(
            "AI-Generated Pain Points",
            data.pain_points,
        )

    # ---------- Competitors ----------

    section_title("Competitor Analysis")

    if data.competitors:

        for comp in data.competitors:

            pdf.set_font("Helvetica", "B", 11)

            pdf.multi_cell(
                0,
                7,
                _sanitize(comp.name),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

            pdf.set_font("Helvetica", "", 11)

            if getattr(comp, "website", None):
                paragraph(f"Website: {comp.website}")

            if getattr(comp, "reason", None):
                paragraph(f"Why competitor: {comp.reason}")

            pdf.ln(1)

    else:
        paragraph("No competitors identified.")

    # ---------- Footer ----------

    pdf.ln(5)

    pdf.set_font("Helvetica", "I", 9)

    pdf.multi_cell(
        0,
        6,
        "This report was generated using AI-powered company research and publicly available information.",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    # ---------- Encode PDF ----------

    buffer = BytesIO()
    pdf.output(buffer)

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"data:application/pdf;base64,{encoded}"