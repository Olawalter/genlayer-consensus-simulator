"use client";

import { Users, TrendingUp, Zap, Activity } from "lucide-react";
import type { CustomValidator } from "@/store/validatorStore";

interface NetworkStatsProps {
  validators: CustomValidator[];
}

export function NetworkStats({ validators: vv }: NetworkStatsProps) {
  const withHistory = vv.filter((v) => v.totalVotes > 0);
  const totalVotes  = vv.reduce((s, v) => s + v.totalVotes, 0);
  const avgAccept   = withHistory.length > 0
    ? withHistory.reduce((s, v) => s + v.acceptRate, 0) / withHistory.length
    : null;
  const avgConf     = withHistory.length > 0
    ? withHistory.reduce((s, v) => s + v.avgConfidence, 0) / withHistory.length
    : null;
  const modified    = vv.filter((v) => v.isCustom).length;

  const stats = [
    { icon: Users,     label: "Active Validators", value: `${vv.length}`, sub: `${modified} modified` },
    { icon: Activity,  label: "Total Votes Cast",  value: totalVotes > 0 ? `${totalVotes}` : "—", sub: "across all validators" },
    { icon: TrendingUp,label: "Avg Accept Rate",   value: avgAccept != null ? `${Math.round(avgAccept * 100)}%` : "—", sub: "network-wide" },
    { icon: Zap,       label: "Avg Confidence",    value: avgConf != null ? `${Math.round(avgConf * 100)}%` : "—", sub: "base level" },
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
