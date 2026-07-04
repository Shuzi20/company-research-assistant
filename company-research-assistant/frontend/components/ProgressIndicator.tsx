"use client";

import { useEffect, useState } from "react";

const STAGES = ["Searching", "Crawling website", "Analyzing with AI", "Building report"];

export default function ProgressIndicator() {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-3 max-w-sm mx-auto py-16">
      {STAGES.map((stage, i) => (
        <div key={stage} className="flex items-center gap-3">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              i < activeStage
                ? "bg-success"
                : i === activeStage
                ? "bg-accent animate-pulse"
                : "bg-border"
            }`}
          />
          <span
            className={`text-sm ${
              i <= activeStage ? "text-text" : "text-textMuted"
            }`}
          >
            {stage}
            {i === activeStage ? "..." : ""}
          </span>
        </div>
      ))}
    </div>
  );
}