"use client";

import { motion } from "framer-motion";
import { X, CheckCircle2, XCircle, HelpCircle, BarChart2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import type { CustomValidator } from "@/store/validatorStore";

interface ComparisonPanelProps {
  validators: CustomValidator[];
  onRemove: (id: string) => void;
  onClear: () => void;
}

const METRIC_ROWS = [
  { key: "acceptThreshold",  label: "Accept Threshold",  format: (v: number) => `${Math.round(v * 100)}%`, higher: "lenient" },
  { key: "confidenceBase",   label: "Base Confidence",   format: (v: number) => `${Math.round(v * 100)}%`, higher: "confident" },
  { key: "uncertaintyRange", label: "Uncertainty Range", format: (v: number) => `${Math.round(v * 100)}%`, higher: "more uncertain" },
] as const;

export function ComparisonPanel({ validators, onRemove, onClear }: ComparisonPanelProps) {
  if (validators.length === 0) {
    return (
      <div className="rounded-xl border-2 border-dashed border-[#d8d4c8] py-16 text-center">
        <BarChart2 className="h-8 w-8 text-[#d8d4c8] mx-auto mb-3" />
        <p className="text-sm font-medium text-[#1a1a1a]">No validators selected</p>
        <p className="text-xs text-[#6b6560] mt-1 max-w-xs mx-auto">
          Click &ldquo;Add to Comparison&rdquo; on up to 3 validator cards to compare their bias profiles side by side.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-[#e8e4da]">
        <p className="text-sm font-semibold text-[#1a1a1a]">Validator Comparison</p>
        <Button variant="ghost" size="sm" className="text-xs h-7 text-[#6b6560]" onClick={onClear}>
          Clear all
        </Button>
      </div>

      {/* Validator columns */}
      <div className="grid gap-0" style={{ gridTemplateColumns: `140px repeat(${validators.length}, 1fr)` }}>
        {/* Column headers */}
        <div className="bg-[#f5f2ec] px-4 py-3 border-r border-[#e8e4da]" />
        {validators.map((v) => {
          const colors = PERSONA_COLORS[v.color] ?? PERSONA_COLORS.indigo;
          return (
            <div key={v.id} className="bg-[#f5f2ec] px-4 py-3 border-r border-[#e8e4da] last:border-r-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={cn("h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0", colors.bg, colors.text)}>
                    {v.avatar}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-[#1a1a1a]">{v.name}</p>
                    <p className="text-[10px] text-[#6b6560] capitalize">{v.persona}</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-[#6b6560]" onClick={() => onRemove(v.id)}>
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </div>
          );
        })}

        {/* Metric rows */}
        {METRIC_ROWS.map((row, ri) => (
          <>
            <div key={`label-${ri}`} className={cn("px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da]", ri % 2 === 0 ? "bg-white/40" : "bg-[#f5f2ec]/40")}>
              {row.label}
            </div>
            {validators.map((v) => {
              const val = v[row.key] as number;
              const maxVal = Math.max(...validators.map((x) => x[row.key] as number));
              const isMax = val === maxVal && validators.length > 1;
              return (
                <div key={`${v.id}-${row.key}`} className={cn("px-4 py-3 border-r border-[#e8e4da] last:border-r-0", ri % 2 === 0 ? "bg-white/40" : "bg-[#f5f2ec]/40")}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={cn("text-xs font-semibold", isMax ? "text-[#2d2a26]" : "text-[#6b6560]")}>
                      {row.format(val)}
                    </span>
                    {isMax && <span className="text-[9px] text-indigo-600 font-medium">highest</span>}
                  </div>
                  <Progress value={Math.round(val * 100)} className="h-1.5" />
                </div>
              );
            })}
          </>
        ))}

        {/* Vote stats rows (if any history) */}
        {validators.some((v) => v.totalVotes > 0) && (
          <>
            <div className="col-span-full px-5 py-2 bg-[#e8e4da]/50 border-t border-[#e8e4da]">
              <p className="text-[10px] font-semibold text-[#6b6560] uppercase tracking-wider">Historical Votes</p>
            </div>

            {/* Accept rate */}
            <div className="px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da] bg-white/40">
              Accept Rate
            </div>
            {validators.map((v) => (
              <div key={`${v.id}-accept`} className="px-4 py-3 border-r border-[#e8e4da] last:border-r-0 bg-white/40">
                {v.totalVotes > 0 ? (
                  <div className="flex items-center gap-1.5">
                    <CheckCircle2 className="h-3 w-3 text-green-500 shrink-0" />
                    <span className="text-xs font-semibold text-green-700">{Math.round(v.acceptRate * 100)}%</span>
                  </div>
                ) : (
                  <span className="text-[10px] text-[#d8d4c8]">—</span>
                )}
              </div>
            ))}

            {/* Reject rate */}
            <div className="px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da] bg-[#f5f2ec]/40">
              Reject Rate
            </div>
            {validators.map((v) => (
              <div key={`${v.id}-reject`} className="px-4 py-3 border-r border-[#e8e4da] last:border-r-0 bg-[#f5f2ec]/40">
                {v.totalVotes > 0 ? (
                  <div className="flex items-center gap-1.5">
                    <XCircle className="h-3 w-3 text-red-500 shrink-0" />
                    <span className="text-xs font-semibold text-red-700">{Math.round(v.rejectRate * 100)}%</span>
                  </div>
                ) : (
                  <span className="text-[10px] text-[#d8d4c8]">—</span>
                )}
              </div>
            ))}

            {/* Uncertain rate */}
            <div className="px-4 py-3 text-xs font-medium text-[#6b6560] border-r border-[#e8e4da] bg-white/40">
              Uncertain Rate
            </div>
            {validators.map((v) => (
              <div key={`${v.id}-uncertain`} className="px-4 py-3 border-r border-[#e8e4da] last:border-r-0 bg-white/40">
                {v.totalVotes > 0 ? (
                  <div className="flex items-center gap-1.5">
                    <HelpCircle className="h-3 w-3 text-amber-500 shrink-0" />
                    <span className="text-xs font-semibold text-amber-700">{Math.round(v.uncertainRate * 100)}%</span>
                  </div>
                ) : (
                  <span className="text-[10px] text-[#d8d4c8]">—</span>
                )}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
