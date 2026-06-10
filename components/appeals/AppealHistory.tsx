"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, AlertTriangle, Clock, ChevronRight, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AppealRecord, AppealStatus } from "@/store/appealStore";

interface AppealHistoryProps {
  appeals: AppealRecord[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onClear: () => void;
}

const STATUS_CFG: Record<AppealStatus, { label: string; icon: React.ElementType; cls: string }> = {
  pending:          { label: "Pending",           icon: Clock,          cls: "text-[#6b6560]" },
  in_progress:      { label: "In Progress",       icon: AlertTriangle,  cls: "text-amber-600" },
  resolved_accept:  { label: "Resolved: Accept",  icon: CheckCircle2,   cls: "text-green-600" },
  resolved_reject:  { label: "Resolved: Reject",  icon: XCircle,        cls: "text-red-600" },
  escalated:        { label: "Escalated",         icon: AlertTriangle,  cls: "text-purple-600" },
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function AppealHistory({ appeals, activeId, onSelect, onClear }: AppealHistoryProps) {
  if (appeals.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-[#d8d4c8] py-10 text-center">
        <p className="text-sm text-[#6b6560]">No appeals recorded yet.</p>
        <p className="text-xs text-[#6b6560] mt-1">
          Trigger an appeal from the Playground when validators disagree.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">
          {appeals.length} appeal{appeals.length !== 1 ? "s" : ""}
        </p>
        <Button variant="ghost" size="sm" className="h-7 text-xs text-[#6b6560] hover:text-red-500" onClick={onClear}>
          <Trash2 className="h-3 w-3 mr-1" /> Clear
        </Button>
      </div>
      <AnimatePresence>
        {appeals.map((a, i) => {
          const cfg = STATUS_CFG[a.status];
          const Icon = cfg.icon;
          const isActive = a.id === activeId;

          return (
            <motion.button
              key={a.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => onSelect(a.id)}
              className={cn(
                "w-full text-left rounded-xl border-2 p-4 transition-all hover:shadow-sm",
                isActive ? "border-[#2d2a26] bg-white/80" : "border-[#d8d4c8] bg-white/50 hover:border-[#b8b4a8]"
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-[#1a1a1a] line-clamp-2 leading-relaxed">
                    {a.claim.slice(0, 100)}{a.claim.length > 100 ? "…" : ""}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className={cn("flex items-center gap-1 text-[11px]", cfg.cls)}>
                      <Icon className="h-3 w-3" /> {cfg.label}
                    </span>
                    <span className="text-[10px] text-[#6b6560]">·</span>
                    <span className="text-[10px] text-[#6b6560]">{a.rounds.length} round{a.rounds.length !== 1 ? "s" : ""}</span>
                    <span className="text-[10px] text-[#6b6560]">·</span>
                    <span className="text-[10px] text-[#6b6560]">{timeAgo(a.createdAt)}</span>
                  </div>
                </div>
                <ChevronRight className={cn("h-4 w-4 shrink-0 mt-0.5 transition-transform", isActive && "rotate-90 text-[#2d2a26]", "text-[#d8d4c8]")} />
              </div>
            </motion.button>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
