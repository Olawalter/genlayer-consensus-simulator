"use client";

import { motion } from "framer-motion";
import { cn, toPercent } from "@/lib/utils";
import type { EquivalenceResult } from "@/lib/validators/equivalence";

interface ConsensusGraphProps {
  result: EquivalenceResult;
  totalValidators: number;
}

export function ConsensusGraph({ result, totalValidators }: ConsensusGraphProps) {
  const { acceptCount, rejectCount, uncertainCount, score, pass, explanation } = result;

  const bars = [
    { label: "Accept",    count: acceptCount,    color: "bg-green-500",  textColor: "text-green-700" },
    { label: "Reject",    count: rejectCount,    color: "bg-red-500",    textColor: "text-red-700" },
    { label: "Uncertain", count: uncertainCount, color: "bg-amber-400",  textColor: "text-amber-700" },
  ];

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/50 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[#1a1a1a]">Vote Distribution</h3>
        <span className={cn(
          "text-xs font-semibold px-2 py-0.5 rounded-full",
          pass ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        )}>
          {Math.round(score * 100)}% agreement
        </span>
      </div>

      {/* Bar chart */}
      <div className="space-y-2">
        {bars.map((bar) => (
          <div key={bar.label} className="flex items-center gap-3">
            <span className="text-xs text-[#6b6560] w-16 shrink-0">{bar.label}</span>
            <div className="flex-1 h-5 rounded-full bg-[#e8e4da] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${toPercent(bar.count, totalValidators)}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className={cn("h-full rounded-full", bar.color)}
              />
            </div>
            <span className={cn("text-xs font-semibold w-6 text-right shrink-0", bar.textColor)}>
              {bar.count}
            </span>
          </div>
        ))}
      </div>

      {/* Equivalence threshold line indicator */}
      <div className="relative h-2 rounded-full bg-[#e8e4da] overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.round(score * 100)}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={cn("h-full rounded-full", pass ? "bg-green-500" : "bg-red-400")}
        />
        {/* 60% threshold marker */}
        <div className="absolute top-0 h-full border-r-2 border-dashed border-[#2d2a26]/40" style={{ left: "60%" }} />
      </div>
      <div className="flex justify-between text-[10px] text-[#6b6560]">
        <span>0%</span>
        <span className="font-medium">60% threshold (Equivalence Principle)</span>
        <span>100%</span>
      </div>

      {/* Explanation */}
      <p className="text-xs text-[#6b6560] leading-relaxed border-t border-[#e8e4da] pt-3">
        {explanation}
      </p>
    </div>
  );
}
