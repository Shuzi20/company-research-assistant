"use client";

import { ApiKeys, DiscordConfig } from "@/types";

interface SidebarProps {
  activeTab: "api" | "discord";
  setActiveTab: (tab: "api" | "discord") => void;
  apiKeys: ApiKeys;
  setApiKeys: (keys: ApiKeys) => void;
  discordConfig: DiscordConfig;
  setDiscordConfig: (config: DiscordConfig) => void;
  onNewResearch: () => void;
  saved: boolean;
  onSave: () => void;
}

const MODELS = [
  { label: "Claude Sonnet 4.5", value: "anthropic/claude-3.5-sonnet" },
  { label: "GPT-4o mini", value: "openai/gpt-4o-mini" },
  { label: "Llama 3.1 70B", value: "meta-llama/llama-3.1-70b-instruct" },
];

export default function Sidebar({
  activeTab,
  setActiveTab,
  apiKeys,
  setApiKeys,
  discordConfig,
  setDiscordConfig,
  onNewResearch,
  saved,
  onSave,
}: SidebarProps) {
  return (
    <aside className="w-full max-w-85 shrink-0 border-r border-border bg-bg px-6 py-6 flex flex-col h-full overflow-y-auto">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center text-bg font-bold">
          R
        </div>
        <div>
          <div className="text-[15px] font-medium leading-tight">Relu Consultancy</div>
          <div className="text-[11px] font-mono text-textMuted tracking-wide">
            COMPANY INTELLIGENCE
          </div>
        </div>
      </div>

      <button
        onClick={onNewResearch}
        className="w-full border border-border rounded-lg py-2.5 text-sm mb-4 hover:border-borderStrong transition-colors flex items-center justify-center gap-2"
      >
        <i className="ti ti-plus" aria-hidden="true" />
        New research
      </button>

      <div className="flex border border-border rounded-lg overflow-hidden mb-5 text-sm font-mono">
        <button
          onClick={() => setActiveTab("api")}
          className={`flex-1 py-2 tracking-wide ${
            activeTab === "api" ? "bg-surface text-text" : "text-textMuted"
          }`}
        >
          API
        </button>
        <button
          onClick={() => setActiveTab("discord")}
          className={`flex-1 py-2 tracking-wide ${
            activeTab === "discord" ? "bg-surface text-text" : "text-textMuted"
          }`}
        >
          DISCORD
        </button>
      </div>

      {activeTab === "api" && (
        <div className="flex flex-col gap-4">
          <Field label="OpenRouter API key">
            <input
              type="password"
              placeholder="sk-or-v1-..."
              value={apiKeys.openrouterKey}
              onChange={(e) => setApiKeys({ ...apiKeys, openrouterKey: e.target.value })}
              className={inputClass}
            />
          </Field>
          <Field label="Serper.dev API key">
            <input
              type="password"
              placeholder="Your Serper key..."
              value={apiKeys.serperKey}
              onChange={(e) => setApiKeys({ ...apiKeys, serperKey: e.target.value })}
              className={inputClass}
            />
          </Field>
          <Field label="AI model">
            <select
              value={apiKeys.model}
              onChange={(e) => setApiKeys({ ...apiKeys, model: e.target.value })}
              className={inputClass}
            >
              {MODELS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </Field>
        </div>
      )}

      {activeTab === "discord" && (
        <div className="flex flex-col gap-4">
          <div className="rounded-lg border border-accentMuted bg-accentMuted/20 p-3 text-[13px] text-textMuted">
            <div className="text-accent font-medium mb-1">Discord bot integration</div>
            After research completes, the report auto-sends to your configured channel.
          </div>
          <Field label="Bot token">
            <input
              type="password"
              placeholder="Bot token..."
              value={discordConfig.botToken}
              onChange={(e) => setDiscordConfig({ ...discordConfig, botToken: e.target.value })}
              className={inputClass}
            />
          </Field>
          <Field label="Channel ID">
            <input
              type="text"
              placeholder="000000000000000000"
              value={discordConfig.channelId}
              onChange={(e) => setDiscordConfig({ ...discordConfig, channelId: e.target.value })}
              className={inputClass}
            />
          </Field>
          <div className="border-t border-border pt-4 mt-1">
            <div className="text-[13px] text-textMuted mb-3">Applicant details</div>
            <div className="flex flex-col gap-3">
              <Field label="Full name">
                <input
                  type="text"
                  placeholder="Your full name"
                  value={discordConfig.applicantName}
                  onChange={(e) =>
                    setDiscordConfig({ ...discordConfig, applicantName: e.target.value })
                  }
                  className={inputClass}
                />
              </Field>
              <Field label="Email address">
                <input
                  type="email"
                  placeholder="email@example.com"
                  value={discordConfig.applicantEmail}
                  onChange={(e) =>
                    setDiscordConfig({ ...discordConfig, applicantEmail: e.target.value })
                  }
                  className={inputClass}
                />
              </Field>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={onSave}
        className="mt-5 w-full rounded-lg py-2.5 text-sm font-medium bg-accent text-bg hover:opacity-90 transition-opacity"
      >
        {saved ? "Saved" : activeTab === "discord" ? "Save Discord config" : "Save configuration"}
      </button>

      <div className="border-t border-border mt-6 pt-5">
        <div className="text-[11px] font-mono text-textMuted tracking-wide mb-3">
          HOW IT WORKS
        </div>
        <ol className="flex flex-col gap-3 text-[13px] text-textMuted">
          {[
            "Enter a company name or URL",
            "Serper.dev searches and crawls it",
            "OpenRouter AI generates insights",
            "Download a professional PDF report",
          ].map((step, i) => (
            <li key={i} className="flex items-start gap-2.5">
              <span className="w-5 h-5 shrink-0 rounded bg-surface border border-border flex items-center justify-center text-[11px] font-mono text-accent">
                {i + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>
      </div>

      <div className="mt-auto pt-6 text-[11px] font-mono text-textMuted tracking-wide">
        OPENROUTER · SERPER · JSPDF
      </div>
    </aside>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[13px] text-textMuted">{label}</span>
      {children}
    </label>
  );
}

const inputClass =
  "w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text placeholder:text-textMuted/60 focus:border-accent transition-colors";