"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Clock, Scale, Hash } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { formatAddress } from "@/lib/utils";
import type { DemocracyTransaction } from "@/store/democracyStore";

interface TxFeedCardProps {
  tx: DemocracyTransaction;
  isActive: boolean;
  onClick: () => void;
  index: number;
}

const STAGE_BADGE: Record<string, { label: string; variant: "accept" | "reject" | "appealed" | "uncertain" | "leader" | "secondary" | "outline" }> = {
  proposed:         { label: "Proposed",       variant: "secondary" },
  validator_review: { label: "Reviewing",      variant: "leader" },
  equivalence_check:{ label: "Eq. Check",      variant: "leader" },
  finality_window:  { label: "Finality",        variant: "uncertain" },
  challenge_period: { label: "Challenge",       variant: "uncertain" },
  finalized:        { label: "Finalized",       variant: "accept" },
  rejected:         { label: "Rejected",        variant: "reject" },
  appealed:         { label: "Appealed",        variant: "appealed" },
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function TxFeedCard({ tx, isActive, onClick, index }: TxFeedCardProps) {
  const badgeCfg = STAGE_BADGE[tx.stage] ?? { label: tx.stage, variant: "outline" as const };

  return (
    <motion.button
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04 }}
      onClick={onClick}
      className={cn(
        "w-full text-left rounded-xl border-2 p-4 transition-all hover:shadow-sm",
        isActive ? "border-[#2d2a26] bg-white/80" : "border-[#d8d4c8] bg-white/50 hover:border-[#b8b4a8]"
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <p className="text-xs text-[#1a1a1a] line-clamp-2 leading-relaxed flex-1">
          {tx.claim.slice(0, 90)}{tx.claim.length > 90 ? "…" : ""}
        </p>
        <Badge variant={badgeCfg.variant} className="text-[9px] px-1.5 py-0 shrink-0">{badgeCfg.label}</Badge>
      </div>
      <div className="flex items-center gap-3 text-[10px] text-[#6b6560]">
        <span className="flex items-center gap-1 font-mono"><Hash className="h-2.5 w-2.5" />{formatAddress(tx.txHash, 6)}</span>
        <span>Block {tx.blockHeight}</span>
        <span>R{tx.round}</span>
        <span className="ml-auto">{timeAgo(tx.startedAt)}</span>
      </div>
    </motion.button>
  );
}
