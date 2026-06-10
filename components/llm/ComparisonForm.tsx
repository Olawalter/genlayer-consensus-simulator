"use client";

import { useState } from "react";
import { Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

const PRESETS = [
  "The software contractor delivered a production-ready API with comprehensive test coverage and documentation by the agreed deadline.",
  "This product review is genuine — the reviewer bought and used the product for 30 days before writing their opinion.",
  "The charity event successfully raised funds and all proceeds were transferred to the intended beneficiaries within the stated timeframe.",
  "The AI-generated article is factually accurate, well-sourced, and free from misleading claims.",
];

interface ComparisonFormProps {
  onRun: (claim: string) => void;
  disabled?: boolean;
}

export function ComparisonForm({ onRun, disabled }: ComparisonFormProps) {
  const [claim, setClaim] = useState("");

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-4">
      <div>
        <p className="text-sm font-semibold text-[#1a1a1a] mb-1">Submit a Claim for Comparison</p>
        <p className="text-xs text-[#6b6560] leading-relaxed">
          All five validator LLMs will independently evaluate the claim simultaneously.
          Compare their votes, reasoning styles, confidence levels, latency and cost.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {PRESETS.map((p, i) => (
          <button key={i} onClick={() => setClaim(p)} disabled={disabled}
            className="text-[11px] border border-[#d8d4c8] rounded-full px-3 py-1 bg-white/50 hover:bg-white transition-all text-[#6b6560] hover:text-[#1a1a1a] disabled:opacity-40">
            Preset {i + 1}
          </button>
        ))}
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs">Claim</Label>
        <Textarea value={claim} onChange={(e) => setClaim(e.target.value)} disabled={disabled}
          placeholder="Enter a subjective claim to evaluate across all LLMs…"
          className="min-h-[90px] text-sm" />
      </div>

      <Button className="w-full" onClick={() => onRun(claim.trim())} disabled={disabled || !claim.trim()}>
        <Play className="h-4 w-4 mr-2" /> Run Comparison Across All Models
      </Button>
    </div>
  );
}
