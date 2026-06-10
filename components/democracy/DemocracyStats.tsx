"use client";

import { CheckCircle2, XCircle, Scale, Zap, Layers } from "lucide-react";

interface NetworkStats {
  totalTx: number;
  accepted: number;
  rejected: number;
  appealed: number;
  avgFinalityMs: number;
  currentBlock: number;
}

interface DemocracyStatsProps {
  stats: NetworkStats;
}

export function DemocracyStats({ stats }: DemocracyStatsProps) {
  const items = [
    { icon: Layers,       label: "Current Block",  value: stats.currentBlock.toLocaleString(), sub: "Asimov testnet" },
    { icon: CheckCircle2, label: "Accepted",        value: stats.accepted > 0 ? `${stats.accepted}` : "—", sub: "claims accepted" },
    { icon: XCircle,      label: "Rejected",        value: stats.rejected > 0 ? `${stats.rejected}` : "—", sub: "claims rejected" },
    { icon: Scale,        label: "Appealed",        value: stats.appealed > 0 ? `${stats.appealed}` : "—", sub: "appeal rounds triggered" },
    { icon: Zap,          label: "Avg Finality",    value: stats.avgFinalityMs > 0 ? `${(stats.avgFinalityMs / 1000).toFixed(1)}s` : "—", sub: "per transaction" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {items.map((s) => (
        <div key={s.label} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
          <div className="flex items-center gap-2 mb-2">
            <s.icon className="h-4 w-4 text-[#6b6560]" />
            <span className="text-xs text-[#6b6560]">{s.label}</span>
          </div>
          <p className="text-lg font-bold text-[#1a1a1a] leading-tight">{s.value}</p>
          <p className="text-[10px] text-[#6b6560] mt-0.5">{s.sub}</p>
        </div>
      ))}
    </div>
  );
}
