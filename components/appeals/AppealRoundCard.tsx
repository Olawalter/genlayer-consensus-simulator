"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Users, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { AppealRound } from "@/store/appealStore";

interface AppealRoundCardProps {
  round: AppealRound;
  index: number;
  isLatest: boolean;
}

const VOTE_CFG = {
  ACCEPT:    { icon: CheckCircle2, cls: "text-green-600", bg: "bg-green-100" },
  REJECT:    { icon: XCircle,      cls: "text-red-600",   bg: "bg-red-100" },
  UNCERTAIN: { icon: HelpCircle,   cls: "text-amber-600", bg: "bg-amber-100" },
};

const OUTCOME_CFG = {
  ACCEPTED:          { label: "Accepted",         variant: "accept"    as const },
  REJECTED:          { label: "Rejected",         variant: "reject"    as const },
  APPEAL_TRIGGERED:  { label: "Appeal Triggered", variant: "appealed"  as const },
};

export function AppealRoundCard({ round, index, isLatest }: AppealRoundCardProps) {
  const { acceptCount, rejectCount, uncertainCount, score } = round.equivalenceResult;
  const outCfg = OUTCOME_CFG[round.outcome];

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08 }}
      className={cn(
        "rounded-xl border-2 p-5 transition-all",
        isLatest ? "border-[#2d2a26] bg-white/80 shadow-md" : "border-[#d8d4c8] bg-white/50"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={cn(
              "text-xs font-bold px-2 py-0.5 rounded-full",
              round.roundNumber === 1 ? "bg-[#2d2a26] text-[#efece4]" : "bg-purple-100 text-purple-800"
            )}>
              {round.roundNumber === 1 ? "Initial Round" : `Appeal Round ${round.roundNumber}`}
            </span>
            {isLatest && <span className="text-[10px] text-[#6b6560] font-medium">Latest</span>}
          </div>
          <div className="flex items-center gap-3 text-[11px] text-[#6b6560]">
            <span className="flex items-center gap-1"><Users className="h-3 w-3" /> {round.validatorCount} validators</span>
            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {(round.durationMs / 1000).toFixed(1)}s</span>
          </div>
        </div>
        <Badge variant={outCfg.variant} className="text-xs">{outCfg.label}</Badge>
      </div>

      {/* Vote chips */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {round.votes.map((v, i) => {
          const cfg = VOTE_CFG[v.vote];
          const Icon = cfg.icon;
          return (
            <div key={i} className={cn("flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium", cfg.bg, cfg.cls)}>
              <Icon className="h-2.5 w-2.5" />
              {v.name.split(" ")[0]}
              <span className="opacity-70">{Math.round(v.confidence * 100)}%</span>
            </div>
          );
        })}
      </div>

      {/* Agreement bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-[11px] text-[#6b6560]">
          <span>Agreement</span>
          <span className="font-semibold text-[#1a1a1a]">{Math.round(score * 100)}%</span>
        </div>
        <div className="relative h-2.5 rounded-full bg-[#e8e4da] overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.round(score * 100)}%` }}
            transition={{ duration: 0.9, ease: "easeOut" }}
            className={cn("h-full rounded-full", round.equivalenceResult.pass ? "bg-green-500" : "bg-red-400")}
          />
          <div className="absolute top-0 h-full border-r-2 border-dashed border-[#2d2a26]/30" style={{ left: "60%" }} />
        </div>
        <div className="flex gap-4 text-[10px] text-[#6b6560]">
          <span className="text-green-700 font-medium">✓ {acceptCount} accept</span>
          <span className="text-red-700 font-medium">✗ {rejectCount} reject</span>
          <span className="text-amber-700 font-medium">? {uncertainCount} uncertain</span>
        </div>
      </div>

      {/* Explanation */}
      <p className="text-[11px] text-[#6b6560] leading-relaxed mt-3 pt-3 border-t border-[#e8e4da]">
        {round.equivalenceResult.explanation}
      </p>
    </motion.div>
  );
}
