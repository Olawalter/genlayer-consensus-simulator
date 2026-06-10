"use client";

import { motion } from "framer-motion";
import { Scale, Clock, Hash, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { AppealRoundCard } from "./AppealRoundCard";
import { formatAddress } from "@/lib/utils";
import type { AppealRecord } from "@/store/appealStore";

interface AppealDetailProps {
  appeal: AppealRecord;
}

const OUTCOME_VARIANT: Record<string, "accept" | "reject" | "appealed"> = {
  ACCEPTED: "accept",
  REJECTED: "reject",
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function AppealDetail({ appeal }: AppealDetailProps) {
  const totalMs = appeal.rounds.reduce((s, r) => s + r.durationMs, 0);
  const roundCount = appeal.rounds.length;
  const appealRounds = appeal.rounds.filter((r) => r.roundNumber > 1);

  return (
    <motion.div
      key={appeal.id}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5"
    >
      {/* Claim header */}
      <div className="rounded-xl border-2 border-[#d8d4c8] bg-white/60 p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Scale className="h-4 w-4 text-[#6b6560] shrink-0" />
              <span className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">Appeal Case</span>
              {appeal.finalOutcome && (
                <Badge variant={OUTCOME_VARIANT[appeal.finalOutcome] ?? "outline"} className="text-xs">
                  Final: {appeal.finalOutcome}
                </Badge>
              )}
            </div>
            <p className="text-sm text-[#1a1a1a] leading-relaxed">
              &ldquo;{appeal.claim}&rdquo;
            </p>
          </div>
        </div>

        <Separator className="my-3" />

        {/* Reason */}
        <div className="flex items-start gap-2 mb-4">
          <FileText className="h-3.5 w-3.5 text-[#6b6560] mt-0.5 shrink-0" />
          <div>
            <p className="text-[10px] font-semibold text-[#6b6560] uppercase tracking-wider mb-0.5">Appeal Reason</p>
            <p className="text-xs text-[#6b6560] italic leading-relaxed">&ldquo;{appeal.appealReason}&rdquo;</p>
          </div>
        </div>

        {/* Meta */}
        <div className="flex flex-wrap gap-4 text-[11px] text-[#6b6560]">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> Started {timeAgo(appeal.createdAt)}
          </span>
          <span className="flex items-center gap-1">
            <span className="font-medium text-[#1a1a1a]">{roundCount}</span> round{roundCount !== 1 ? "s" : ""} total
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> Total {(totalMs / 1000).toFixed(1)}s
          </span>
          <span className="flex items-center gap-1 font-mono">
            <Hash className="h-3 w-3" /> {formatAddress(appeal.id, 10)}
          </span>
        </div>
      </div>

      {/* Round cards */}
      <div>
        <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-3">Round Breakdown</p>
        <div className="space-y-3">
          {appeal.rounds.map((round, i) => (
            <AppealRoundCard
              key={round.roundNumber}
              round={round}
              index={i}
              isLatest={i === appeal.rounds.length - 1}
            />
          ))}
        </div>
      </div>

      {/* Educational callout */}
      {appealRounds.length > 0 && (
        <div className="rounded-xl border border-purple-200 bg-purple-50/60 p-4">
          <p className="text-xs font-semibold text-purple-800 mb-1.5">
            How GenLayer Appeals Work
          </p>
          <p className="text-xs text-purple-700 leading-relaxed">
            When the Equivalence Principle fails (less than 60% agreement), an appeal adds{" "}
            <strong>3 additional validators</strong> per round. The expanded set re-evaluates the claim
            from scratch, and their votes are pooled with the originals. This continues until consensus
            is reached or the case is escalated. This appeal expanded the validator set from{" "}
            <strong>{appeal.rounds[0]?.validatorCount}</strong> to{" "}
            <strong>{appeal.rounds[appeal.rounds.length - 1]?.validatorCount}</strong> validators.
          </p>
        </div>
      )}
    </motion.div>
  );
}
