"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Trash2, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { CustomValidator, VoteRecord } from "@/store/validatorStore";

interface VoteHistoryProps {
  validator: CustomValidator;
  onClear: () => void;
}

const VOTE_ICONS = {
  ACCEPT:    { icon: CheckCircle2, variant: "accept"    as const, color: "text-green-600" },
  REJECT:    { icon: XCircle,      variant: "reject"    as const, color: "text-red-600" },
  UNCERTAIN: { icon: HelpCircle,   variant: "uncertain" as const, color: "text-amber-600" },
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function VoteHistory({ validator, onClear }: VoteHistoryProps) {
  const { voteHistory } = validator;

  if (voteHistory.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-[#d8d4c8] py-12 text-center">
        <p className="text-sm text-[#6b6560]">No vote history yet.</p>
        <p className="text-xs text-[#6b6560] mt-1">Run simulations in the Playground to see {validator.name}&apos;s votes here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">
          Vote History · {voteHistory.length} records
        </p>
        <Button variant="ghost" size="sm" className="h-7 text-xs text-[#6b6560] hover:text-red-500" onClick={onClear}>
          <Trash2 className="h-3 w-3 mr-1" /> Clear
        </Button>
      </div>

      <AnimatePresence>
        {voteHistory.map((record, i) => (
          <VoteRow key={record.id} record={record} index={i} />
        ))}
      </AnimatePresence>
    </div>
  );
}

function VoteRow({ record, index }: { record: VoteRecord; index: number }) {
  const cfg = VOTE_ICONS[record.vote];
  const Icon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="rounded-lg border border-[#e8e4da] bg-white/60 p-3.5"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <p className="text-xs text-[#1a1a1a] leading-relaxed line-clamp-2 flex-1">
          {record.claim}
        </p>
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant={cfg.variant} className="text-[10px] px-1.5 py-0">
            <Icon className="h-2.5 w-2.5 mr-0.5" /> {record.vote}
          </Badge>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <div className="flex justify-between text-[10px] text-[#6b6560] mb-1">
            <span>Confidence</span>
            <span className="font-medium">{Math.round(record.confidence * 100)}%</span>
          </div>
          <Progress value={Math.round(record.confidence * 100)} className="h-1" />
        </div>
        <div className="flex items-center gap-1 text-[10px] text-[#6b6560] shrink-0">
          <Clock className="h-2.5 w-2.5" /> {timeAgo(record.timestamp)}
        </div>
      </div>
      {record.reasoning && (
        <p className="text-[10px] text-[#6b6560] leading-relaxed mt-2 line-clamp-2 italic">
          &ldquo;{record.reasoning}&rdquo;
        </p>
      )}
    </motion.div>
  );
}
