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
    <div className="max-w-4xl mx-auto w-full">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-medium mb-1">
            {data.company_name}
          </h1>

          {data.website && (
            <a
              href={data.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent text-sm hover:underline break-all"
            >
              {data.website}
            </a>
          )}

          {data.industry && (
            <div className="mt-2 text-sm text-textMuted">
              Industry: {data.industry}
            </div>
          )}
        </div>

        <span className="text-[11px] font-mono text-success border border-success/40 rounded-full px-3 py-1 tracking-wide">
          RESEARCH COMPLETE
        </span>
      </div>

      {warnings.length > 0 && (
        <div className="mb-6 rounded-lg border border-accentMuted bg-accentMuted/10 px-4 py-3 text-[13px] text-textMuted">
          <span className="text-accent font-medium">
            Partial data notice:
          </span>{" "}
          {warnings.join(" · ")}
        </div>
      )}

      {/* Company Information */}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {data.phone && (
          <InfoCard
            label="Phone"
            value={data.phone}
          />
        )}

        {data.address && (
          <InfoCard
            label="Address"
            value={data.address}
          />
        )}
      </div>

      {/* Executive Summary */}

      {data.summary && (
        <Section title="Executive Summary">
          <p className="text-sm leading-7 text-text/90">
            {data.summary}
          </p>
        </Section>
      )}

      {/* Business Model */}

      {data.business_model && (
        <Section title="Business Model">
          <p className="text-sm leading-7 text-text/90">
            {data.business_model}
          </p>
        </Section>
      )}

      {/* Target Customers */}

      <BulletSection
        title="Target Customers"
        items={data.target_customers || []}
      />

      {/* Products */}

      <Section title="Products & Services">
        <div className="flex flex-wrap gap-2">
          {data.products_services?.length > 0 ? (
            data.products_services.map((item) => (
              <span
                key={item}
                className="text-[13px] bg-surface border border-border rounded-full px-3 py-1"
              >
                {item}
              </span>
            ))
          ) : (
            <span className="text-sm text-textMuted">
              Not available
            </span>
          )}
        </div>
      </Section>

      {/* SWOT */}

      <BulletSection
        title="Strengths"
        items={data.strengths || []}
      />

      <BulletSection
        title="Weaknesses"
        items={data.weaknesses || []}
      />

      <BulletSection
        title="Opportunities"
        items={data.opportunities || []}
      />

      <BulletSection
        title="Threats"
        items={data.threats || []}
      />

      {/* Pain Points */}

      <BulletSection
        title="AI-Generated Pain Points"
        items={data.pain_points || []}
      />

      {/* Competitors */}

      <Section title="Competitor Analysis">
        {data.competitors?.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-3">
            {data.competitors.map((c) => (
              <div
                key={c.name}
                className="border border-border rounded-lg px-4 py-3 bg-surface"
              >
                <div className="text-sm font-medium mb-1">
                  {c.name}
                </div>

                {c.website && (
                  <a
                    href={c.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[13px] text-accent hover:underline break-all block"
                  >
                    {c.website}
                  </a>
                )}

                {"reason" in c &&
                  c.reason && (
                    <div className="text-[13px] text-textMuted mt-2 leading-6">
                      {c.reason}
                    </div>
                  )}
              </div>
            ))}
          </div>
        ) : (
          <span className="text-sm text-textMuted">
            No competitors identified
          </span>
        )}
      </Section>

      {/* Buttons */}

      <div className="flex flex-wrap items-center gap-3 mt-8">
        <button
          disabled={!pdfUrl}
          onClick={() =>
            pdfUrl &&
            downloadPdf(
              pdfUrl,
              data.company_name
            )
          }
          className="flex items-center gap-2 bg-accent text-bg font-medium text-sm rounded-lg px-4 py-2.5 disabled:opacity-40 hover:opacity-90 transition-opacity"
        >
          <i
            className="ti ti-download"
            aria-hidden="true"
          />
          Download PDF Report
        </button>

        {discordConfigured && (
          <button
            onClick={onSendToDiscord}
            disabled={discordSent || !pdfUrl}
            className="flex items-center gap-2 border border-success/40 text-success text-sm rounded-lg px-4 py-2.5 disabled:opacity-60 hover:bg-success/10 transition-colors"
          >
            <i
              className={`ti ${
                discordSent
                  ? "ti-check"
                  : "ti-brand-discord"
              }`}
              aria-hidden="true"
            />
            {discordSent
              ? "Sent to Discord"
              : "Send to Discord"}
          </button>
        )}
      </div>
    </div>
  );
}

function InfoCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border border-border rounded-lg px-4 py-3 bg-surface">
      <div className="text-[11px] font-mono text-textMuted tracking-wide mb-1">
        {label.toUpperCase()}
      </div>
      <div className="text-sm">
        {value}
      </div>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-6">
      <div className="text-[11px] font-mono text-accent tracking-wide mb-3">
        {title.toUpperCase()}
      </div>

      {children}
    </div>
  );
}

function BulletSection({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <Section title={title}>
      <ul className="flex flex-col gap-2">
        {items.map((item, index) => (
          <li
            key={index}
            className="flex gap-2 text-sm text-text/90"
          >
            <span className="text-accent">
              •
            </span>

            <span>{item}</span>
          </li>
        ))}
      </ul>
    </Section>
  );
}