"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { EXPLORER_SCENARIOS, type ExplorerScenario } from "@/lib/equivalence/scorer";

const CATEGORY_LABELS: Record<string, { label: string; variant: "accept" | "reject" | "uncertain" | "appealed" | "default" }> = {
  unanimous:      { label: "Unanimous",       variant: "accept" },
  majority:       { label: "Majority",        variant: "accept" },
  split:          { label: "Split",           variant: "appealed" },
  non_comparative:{ label: "Non-Comparative", variant: "secondary" as never },
  edge:           { label: "Edge Case",       variant: "uncertain" },
};

interface ScenarioSelectorProps {
  activeId: string;
  onSelect: (s: ExplorerScenario) => void;
}

export function ScenarioSelector({ activeId, onSelect }: ScenarioSelectorProps) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-3">Scenarios</p>
      {EXPLORER_SCENARIOS.map((s) => {
        const cat = CATEGORY_LABELS[s.category] ?? { label: s.category, variant: "default" as const };
        return (
          <button
            key={s.id}
            onClick={() => onSelect(s)}
            className={cn(
              "w-full text-left rounded-xl border-2 p-3.5 transition-all",
              activeId === s.id
                ? "border-[#2d2a26] bg-white/80 shadow-sm"
                : "border-[#d8d4c8] bg-white/40 hover:border-[#b8b4a8]"
            )}
          >
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-semibold text-[#1a1a1a]">{s.title}</p>
              <Badge variant={cat.variant as never} className="text-[9px] px-1.5 py-0">{cat.label}</Badge>
            </div>
            <p className="text-[11px] text-[#6b6560] leading-relaxed line-clamp-2">{s.description}</p>
          </button>
        );
      })}
    </div>
  );
}
