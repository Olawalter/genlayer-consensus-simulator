"use client";

import { Slider } from "@/components/ui/slider";
import { cn } from "@/lib/utils";
import type { VoteInput } from "@/lib/equivalence/scorer";

const VALIDATOR_COLORS: Record<string, string> = {
  Atlas:  "#6366f1",
  Nova:   "#ec4899",
  Orion:  "#ef4444",
  Lyra:   "#22c55e",
  Zephyr: "#f59e0b",
};

interface VoteInputPanelProps {
  votes: VoteInput[];
  onChange: (votes: VoteInput[]) => void;
}

export function VoteInputPanel({ votes, onChange }: VoteInputPanelProps) {
  function handleChange(index: number, value: number) {
    const next = votes.map((v, i) => (i === index ? { ...v, value } : v));
    onChange(next);
  }

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-4">
      <p className="text-sm font-semibold text-[#1a1a1a]">Validator Confidence Scores</p>
      <p className="text-xs text-[#6b6560] leading-relaxed">
        Drag each slider to simulate a validator&apos;s confidence score (0 = strong reject, 1 = strong accept).
        Watch the equivalence map and result update in real time.
      </p>
      <div className="space-y-4">
        {votes.map((v, i) => {
          const color = VALIDATOR_COLORS[v.label] ?? "#2d2a26";
          const pct   = Math.round(v.value * 100);
          const label = pct >= 70 ? "ACCEPT" : pct <= 40 ? "REJECT" : "UNCERTAIN";
          const labelColor = pct >= 70 ? "text-green-600" : pct <= 40 ? "text-red-600" : "text-amber-600";
          return (
            <div key={v.label}>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: color }} />
                  <span className="text-xs font-medium text-[#1a1a1a]">{v.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn("text-[10px] font-semibold", labelColor)}>{label}</span>
                  <span className="text-xs font-semibold text-[#2d2a26] tabular-nums w-8 text-right">{pct}%</span>
                </div>
              </div>
              <Slider
                min={0} max={1} step={0.01}
                value={[v.value]}
                onValueChange={([val]) => handleChange(i, val)}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
