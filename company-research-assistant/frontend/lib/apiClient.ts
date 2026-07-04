import { ResearchResponse, DiscordConfig } from "@/types";

// Set NEXT_PUBLIC_API_BASE_URL in your Vercel project env vars to the deployed
// FastAPI service URL. Falls back to localhost for local dev.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function runResearch(query: string, model: string): Promise<ResearchResponse> {
  const resp = await fetch(`${API_BASE}/api/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, model }),
  });

  if (!resp.ok) {
    const detail = await resp.text().catch(() => "");
    throw new Error(`Research request failed (${resp.status}): ${detail}`);
  }

  return resp.json();
}

export async function sendToDiscord(
  config: DiscordConfig,
  companyName: string,
  companyWebsite: string | null,
  pdfBase64: string
): Promise<void> {
  const resp = await fetch(`${API_BASE}/api/discord/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      bot_token: config.botToken,
      channel_id: config.channelId,
      applicant_name: config.applicantName,
      applicant_email: config.applicantEmail,
      company_name: companyName,
      company_website: companyWebsite,
      pdf_base64: pdfBase64,
    }),
  });

  if (!resp.ok) {
    const detail = await resp.text().catch(() => "");
    throw new Error(`Discord send failed (${resp.status}): ${detail}`);
  }
}

export function downloadPdf(pdfDataUri: string, companyName: string) {
  const link = document.createElement("a");
  link.href = pdfDataUri;
  link.download = `${companyName.replace(/\s+/g, "_").toLowerCase()}-research-report.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}