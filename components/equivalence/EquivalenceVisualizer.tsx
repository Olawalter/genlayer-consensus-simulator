"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { EquivalenceScoreResult, VoteInput } from "@/lib/equivalence/scorer";

interface EquivalenceVisualizerProps {
  result: EquivalenceScoreResult;
}

const VALIDATOR_COLORS: Record<string, string> = {
  Atlas:  "#6366f1",
  Nova:   "#ec4899",
  Orion:  "#ef4444",
  Lyra:   "#22c55e",
  Zephyr: "#f59e0b",
};

export function EquivalenceVisualizer({ result }: EquivalenceVisualizerProps) {
  const { votes, mean, bandLow, bandHigh, passes, mode } = result;

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[#1a1a1a]">
          {mode === "comparative" ? "Comparative" : "Non-Comparative"} Equivalence Map
        </h3>
        <span className={cn(
          "text-xs font-semibold px-2.5 py-1 rounded-full",
          passes ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        )}>
          {passes ? "✓ Passes" : "✗ Fails"}
        </span>
      </div>

      {/* Number line visualisation */}
      <div className="relative h-20 select-none">
        {/* Base track */}
        <div className="absolute top-1/2 -translate-y-1/2 left-0 right-0 h-2 rounded-full bg-[#e8e4da]" />

        {/* Equivalence band */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{
            left:  `${bandLow  * 100}%`,
            width: `${(bandHigh - bandLow) * 100}%`,
            originX: 0,
          }}
          className={cn(
            "absolute top-1/2 -translate-y-1/2 h-4 rounded-full opacity-30",
            passes ? "bg-green-400" : "bg-red-400"
          )}
        />

        {/* Mean line */}
        <div
          className="absolute top-1/2 -translate-y-full h-5 w-0.5 bg-[#2d2a26]"
          style={{ left: `${mean * 100}%` }}
        >
          <span className="absolute -top-5 -translate-x-1/2 text-[9px] text-[#2d2a26] font-semibold whitespace-nowrap">
            μ {Math.round(mean * 100)}%
          </span>
        </div>

        {/* 60% threshold marker */}
        <div className="absolute top-0 h-full border-l-2 border-dashed border-[#6b6560]/40" style={{ left: "60%" }}>
          <span className="absolute top-0 left-1 text-[9px] text-[#6b6560] whitespace-nowrap">60% threshold</span>
        </div>

        {/* Validator dots */}
        {votes.map((v, i) => {
          const color  = VALIDATOR_COLORS[v.label] ?? "#2d2a26";
          const inside = v.value >= bandLow && v.value <= bandHigh;
          return (
            <motion.div
              key={v.label}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: i * 0.1 + 0.3, type: "spring", stiffness: 300 }}
              style={{ left: `${v.value * 100}%`, backgroundColor: color }}
              className={cn(
                "absolute top-1/2 -translate-x-1/2 -translate-y-1/2 h-5 w-5 rounded-full border-2 border-white shadow-md cursor-default",
                !inside && "ring-2 ring-red-400 ring-offset-1"
              )}
              title={`${v.label}: ${Math.round(v.value * 100)}%`}
            >
              <span className="absolute -bottom-6 -translate-x-1/2 left-1/2 text-[9px] font-semibold whitespace-nowrap" style={{ color }}>
                {v.label.slice(0, 2)}
              </span>
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-5 gap-1.5 pt-4">
        {votes.map((v) => {
          const color  = VALIDATOR_COLORS[v.label] ?? "#2d2a26";
          const inside = v.value >= bandLow && v.value <= bandHigh;
          return (
            <div key={v.label} className={cn(
              "rounded-lg border px-2 py-1.5 text-center text-[10px]",
              inside ? "border-[#e8e4da] bg-white/40" : "border-red-200 bg-red-50"
            )}>
              <div className="h-2 w-2 rounded-full mx-auto mb-1" style={{ backgroundColor: color }} />
              <p className="font-semibold text-[#1a1a1a]">{v.label}</p>
              <p className="text-[#6b6560]">{Math.round(v.value * 100)}%</p>
              <p className={cn("text-[9px]", inside ? "text-green-600" : "text-red-500")}>
                {inside ? "✓ in band" : "✗ outside"}
              </p>
            </div>
          );
        })}
      </div>

      {/* Stats row */}
      <div className="flex justify-between text-xs text-[#6b6560] border-t border-[#e8e4da] pt-3">
        <span>Band: <strong className="text-[#1a1a1a]">{Math.round(bandLow*100)}% – {Math.round(bandHigh*100)}%</strong></span>
        <span>Agreement: <strong className="text-[#1a1a1a]">{Math.round(result.agreement * 100)}%</strong></span>
        <span>Spread σ: <strong className="text-[#1a1a1a]">{Math.round(result.spread * 100)}%</strong></span>
      </div>
    </div>
  );
}
