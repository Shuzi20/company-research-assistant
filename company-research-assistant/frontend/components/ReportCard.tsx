"use client";

import { CompanyData } from "@/types";
import { downloadPdf } from "@/lib/apiClient";

interface ReportCardProps {
  data: CompanyData;
  pdfUrl: string | null;
  warnings: string[];
  discordSent: boolean;
  onSendToDiscord: () => void;
  discordConfigured: boolean;
}

export default function ReportCard({
  data,
  pdfUrl,
  warnings,
  discordSent,
  onSendToDiscord,
  discordConfigured,
}: ReportCardProps) {
  return (
    <div className="max-w-3xl mx-auto w-full">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-medium mb-1">{data.company_name}</h1>
          {data.website && (
            <a
              href={data.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent text-sm hover:underline"
            >
              {data.website}
            </a>
          )}
        </div>
        <span className="text-[11px] font-mono text-success border border-success/40 rounded-full px-3 py-1 tracking-wide">
          RESEARCH COMPLETE
        </span>
      </div>

      {warnings.length > 0 && (
        <div className="mb-6 rounded-lg border border-accentMuted bg-accentMuted/10 px-4 py-3 text-[13px] text-textMuted">
          <span className="text-accent font-medium">Partial data notice: </span>
          {warnings.join(" · ")}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-6">
        <InfoCard label="Phone" value={data.phone || "Not publicly listed"} />
        <InfoCard label="Address" value={data.address || "Not publicly listed"} />
      </div>

      <Section title="Products & services">
        <div className="flex flex-wrap gap-2">
          {data.products_services.length > 0 ? (
            data.products_services.map((item) => (
              <span
                key={item}
                className="text-[13px] bg-surface border border-border rounded-full px-3 py-1"
              >
                {item}
              </span>
            ))
          ) : (
            <span className="text-sm text-textMuted">Not available</span>
          )}
        </div>
      </Section>

      <Section title="AI-generated pain points">
        {data.pain_points.length > 0 ? (
          <ul className="flex flex-col gap-2.5">
            {data.pain_points.map((point, i) => (
              <li key={i} className="flex gap-2.5 text-sm text-text/90">
                <span className="text-accent mt-1">•</span>
                {point}
              </li>
            ))}
          </ul>
        ) : (
          <span className="text-sm text-textMuted">Not available</span>
        )}
      </Section>

      <Section title="Competitors">
        {data.competitors.length > 0 ? (
          <div className="grid grid-cols-2 gap-3">
            {data.competitors.map((c) => (
              <div
                key={c.name}
                className="border border-border rounded-lg px-3.5 py-3 bg-surface"
              >
                <div className="text-sm font-medium">{c.name}</div>
                {c.website ? (
                  <a
                    href={c.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[13px] text-accent hover:underline break-all"
                  >
                    {c.website}
                  </a>
                ) : (
                  <span className="text-[13px] text-textMuted">Website unverified</span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <span className="text-sm text-textMuted">Not available</span>
        )}
      </Section>

      <div className="flex items-center gap-3 mt-8">
        <button
          disabled={!pdfUrl}
          onClick={() => pdfUrl && downloadPdf(pdfUrl, data.company_name)}
          className="flex items-center gap-2 bg-accent text-bg font-medium text-sm rounded-lg px-4 py-2.5 disabled:opacity-40 hover:opacity-90 transition-opacity"
        >
          <i className="ti ti-download" aria-hidden="true" />
          Download PDF report
        </button>

        {discordConfigured && (
          <button
            onClick={onSendToDiscord}
            disabled={discordSent || !pdfUrl}
            className="flex items-center gap-2 border border-success/40 text-success text-sm rounded-lg px-4 py-2.5 disabled:opacity-60 hover:bg-success/10 transition-colors"
          >
            <i className={`ti ${discordSent ? "ti-check" : "ti-brand-discord"}`} aria-hidden="true" />
            {discordSent ? "Sent to Discord" : "Send to Discord"}
          </button>
        )}
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-border rounded-lg px-4 py-3 bg-surface">
      <div className="text-[11px] font-mono text-textMuted tracking-wide mb-1">
        {label.toUpperCase()}
      </div>
      <div className="text-sm">{value}</div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <div className="text-[11px] font-mono text-accent tracking-wide mb-3">
        {title.toUpperCase()}
      </div>
      {children}
    </div>
  );
}