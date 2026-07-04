"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import ProgressIndicator from "@/components/ProgressIndicator";
import ReportCard from "@/components/ReportCard";
import { runResearch, sendToDiscord } from "@/lib/apiClient";
import { ApiKeys, DiscordConfig, ResearchResponse } from "@/types";

const EXAMPLES = ["stripe.com", "Tesla", "Microsoft", "OpenAI"];

export default function Home() {
  const [activeTab, setActiveTab] = useState<"api" | "discord">("api");
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openrouterKey: "",
    serperKey: "",
    model: "anthropic/claude-3.5-sonnet",
  });
  const [discordConfig, setDiscordConfig] = useState<DiscordConfig>({
    botToken: "",
    channelId: "",
    applicantName: "",
    applicantEmail: "",
  });
  const [configSaved, setConfigSaved] = useState(false);

  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [discordSent, setDiscordSent] = useState(false);

  const discordConfigured = Boolean(discordConfig.botToken && discordConfig.channelId);

  async function handleResearch(q?: string) {
    const finalQuery = (q ?? query).trim();
    if (!finalQuery || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setDiscordSent(false);

    try {
      const response = await runResearch(finalQuery, apiKeys.model);
      setResult(response);

      // If Discord is already configured, auto-send per the assignment's bonus flow.
      if (discordConfigured && response.pdf_url) {
        try {
          await sendToDiscord(
            discordConfig,
            response.data.company_name,
            response.data.website,
            response.pdf_url
          );
          setDiscordSent(true);
        } catch {
          // Discord failure never blocks the visible result - it's already rendered above.
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleManualDiscordSend() {
    if (!result?.pdf_url) return;
    try {
      await sendToDiscord(
        discordConfig,
        result.data.company_name,
        result.data.website,
        result.pdf_url
      );
      setDiscordSent(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Discord send failed.");
    }
  }

  function handleNewResearch() {
    setQuery("");
    setResult(null);
    setError(null);
    setDiscordSent(false);
  }

  return (
    <div className="flex h-screen">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiKeys={apiKeys}
        setApiKeys={setApiKeys}
        discordConfig={discordConfig}
        setDiscordConfig={setDiscordConfig}
        onNewResearch={handleNewResearch}
        saved={configSaved}
        onSave={() => {
          setConfigSaved(true);
          setTimeout(() => setConfigSaved(false), 1800);
        }}
      />

      <main className="flex-1 flex flex-col">
        <header className="flex items-center gap-3 px-8 py-5 border-b border-border">
          <h2 className="text-[15px] font-medium">Company research</h2>
          <span className="flex items-center gap-1.5 text-[11px] font-mono text-success">
            <span className="w-1.5 h-1.5 rounded-full bg-success" />
            LIVE
          </span>
        </header>

        <div className="flex-1 overflow-y-auto px-8 py-10">
          {!result && !loading && (
            <div className="max-w-xl mx-auto text-center pt-16">
              <div className="text-[11px] font-mono text-accent tracking-wide mb-4">
                AI-POWERED INTELLIGENCE
              </div>
              <h1 className="text-4xl font-medium leading-tight mb-4">
                Know any company
                <br />
                in minutes.
              </h1>
              <p className="text-textMuted text-[15px] mb-8">
                Enter a company name or website URL to get AI-powered insights,
                competitor analysis, pain points, and a professional PDF report.
              </p>
              <div className="flex justify-center gap-2 flex-wrap">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    onClick={() => {
                      setQuery(ex);
                      handleResearch(ex);
                    }}
                    className="text-[13px] font-mono border border-border rounded-full px-3.5 py-1.5 text-textMuted hover:border-borderStrong hover:text-text transition-colors"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}

          {loading && <ProgressIndicator />}

          {error && (
            <div className="max-w-xl mx-auto border border-danger/40 bg-danger/10 rounded-lg px-4 py-3 text-sm text-danger">
              {error}
            </div>
          )}

          {result && !loading && (
            <ReportCard
              data={result.data}
              pdfUrl={result.pdf_url}
              warnings={result.warnings}
              discordSent={discordSent}
              onSendToDiscord={handleManualDiscordSend}
              discordConfigured={discordConfigured}
            />
          )}
        </div>

        <div className="border-t border-border px-8 py-4">
          <div className="max-w-3xl mx-auto flex items-end gap-3">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleResearch();
                }
              }}
              placeholder="Enter a company name (e.g. Aurora Labs) or website URL (e.g. https://aurora.dev)..."
              rows={1}
              className="flex-1 resize-none bg-surface border border-border rounded-lg px-4 py-3 text-sm placeholder:text-textMuted/60 focus:border-accent transition-colors"
            />
            <button
              onClick={() => handleResearch()}
              disabled={loading || !query.trim()}
              className="flex items-center gap-2 bg-accent text-bg font-medium text-sm rounded-lg px-4 py-3 disabled:opacity-40 hover:opacity-90 transition-opacity shrink-0"
            >
              Research
              <i className="ti ti-arrow-right" aria-hidden="true" />
            </button>
          </div>
          <div className="max-w-3xl mx-auto text-[11px] font-mono text-textMuted/70 mt-2">
            ENTER TO RESEARCH · SHIFT+ENTER FOR NEW LINE
          </div>
        </div>
      </main>
    </div>
  );
}