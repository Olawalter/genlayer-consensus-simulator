"use client";

import { Scale, CheckCircle2, XCircle, TrendingUp } from "lucide-react";
import type { AppealRecord } from "@/store/appealStore";

interface AppealStatsProps {
  appeals: AppealRecord[];
}

export function AppealStats({ appeals }: AppealStatsProps) {
  const total     = appeals.length;
  const resolved  = appeals.filter((a) => a.finalOutcome !== null);
  const accepted  = resolved.filter((a) => a.finalOutcome === "ACCEPTED").length;
  const rejected  = resolved.filter((a) => a.finalOutcome === "REJECTED").length;
  const avgRounds = total > 0
    ? (appeals.reduce((s, a) => s + a.rounds.length, 0) / total).toFixed(1)
    : "—";

  const stats = [
    { icon: Scale,        label: "Total Appeals",     value: `${total}`,       sub: `${resolved.length} resolved` },
    { icon: CheckCircle2, label: "Resolved: Accept",  value: accepted > 0 ? `${accepted}` : "—", sub: "overturned to accept" },
    { icon: XCircle,      label: "Resolved: Reject",  value: rejected > 0 ? `${rejected}` : "—", sub: "confirmed rejection" },
    { icon: TrendingUp,   label: "Avg Rounds",        value: avgRounds,        sub: "per appeal" },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      {stats.map((s) => (
        <div key={s.label} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
          <div className="flex items-center gap-2 mb-2">
            <s.icon className="h-4 w-4 text-[#6b6560]" />
            <span className="text-xs text-[#6b6560]">{s.label}</span>
          </div>
          <p className="text-xl font-bold text-[#1a1a1a] leading-tight">{s.value}</p>
          <p className="text-[10px] text-[#6b6560] mt-0.5">{s.sub}</p>
        </div>
      ))}
    </div>
  );
}
