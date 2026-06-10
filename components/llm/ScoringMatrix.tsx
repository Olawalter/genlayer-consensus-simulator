"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Clock, DollarSign, Hash, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { LLM_MODELS, MODEL_COLORS } from "@/lib/llm/models";
import type { LLMResponse } from "@/lib/llm/simulator";

interface ScoringMatrixProps {
  responses: Record<string, LLMResponse>;
}

const VOTE_ICONS = {
  ACCEPT:    { icon: CheckCircle2, cls: "text-green-600" },
  REJECT:    { icon: XCircle,      cls: "text-red-600" },
  UNCERTAIN: { icon: HelpCircle,   cls: "text-amber-600" },
};

export function ScoringMatrix({ responses }: ScoringMatrixProps) {
  const models = LLM_MODELS.filter((m) => responses[m.id]);
  if (models.length === 0) return null;

  const fastestId  = models.reduce((a, b) => responses[a.id].latencyMs < responses[b.id].latencyMs ? a : b).id;
  const cheapestId = models.reduce((a, b) => responses[a.id].costUsd    < responses[b.id].costUsd    ? a : b).id;
  const mostConfId = models.reduce((a, b) => responses[a.id].confidence > responses[b.id].confidence ? a : b).id;

  const maxLatency = Math.max(...models.map((m) => responses[m.id].latencyMs));
  const maxCost    = Math.max(...models.map((m) => responses[m.id].costUsd));

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 overflow-hidden">
      <div className="px-5 py-3 border-b border-[#e8e4da] flex items-center justify-between">
        <p className="text-sm font-semibold text-[#1a1a1a]">Scoring Matrix</p>
        <p className="text-xs text-[#6b6560]">{models.length} models compared</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-[#f5f2ec]">
              <th className="px-4 py-2.5 text-left font-semibold text-[#6b6560] w-36">Model</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Vote</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Confidence</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Latency</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Cost</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Tokens</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model, i) => {
              const r      = responses[model.id];
              const colors = MODEL_COLORS[model.color] ?? MODEL_COLORS.emerald;
              const voteCfg = VOTE_ICONS[r.vote];
              const Icon   = voteCfg.icon;

              return (
                <motion.tr
                  key={model.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className={cn("border-t border-[#e8e4da]", i % 2 === 0 ? "bg-white/30" : "bg-[#f5f2ec]/30")}
                >
                  {/* Model */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className={cn("h-6 w-6 rounded flex items-center justify-center text-[9px] font-bold shrink-0", colors.bg, colors.text)}>
                        {model.avatar}
                      </div>
                      <div>
                        <p className="font-semibold text-[#1a1a1a] leading-tight">{model.name}</p>
                        <p className="text-[9px] text-[#6b6560]">{model.provider}</p>
                      </div>
                    </div>
                  </td>

                  {/* Vote */}
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-1">
                      <Icon className={cn("h-3.5 w-3.5", voteCfg.cls)} />
                      <span className={cn("font-semibold", voteCfg.cls)}>{r.vote}</span>
                    </div>
                  </td>

                  {/* Confidence */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Progress value={Math.round(r.confidence * 100)} className="h-1.5 w-16" />
                      <span className={cn("font-semibold tabular-nums", model.id === mostConfId && "text-indigo-600")}>
                        {Math.round(r.confidence * 100)}%
                        {model.id === mostConfId && <span className="text-[8px] ml-0.5">★</span>}
                      </span>
                    </div>
                  </td>

                  {/* Latency */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-1.5 rounded-full bg-[#e8e4da] overflow-hidden">
                        <div className="h-full rounded-full bg-blue-400" style={{ width: `${(r.latencyMs / maxLatency) * 100}%` }} />
                      </div>
                      <span className={cn("tabular-nums", model.id === fastestId && "text-green-600 font-semibold")}>
                        {r.latencyMs}ms
                        {model.id === fastestId && <span className="text-[8px] ml-0.5">⚡</span>}
                      </span>
                    </div>
                  </td>

                  {/* Cost */}
                  <td className="px-4 py-3">
                    <span className={cn("tabular-nums", model.id === cheapestId && "text-green-600 font-semibold")}>
                      ${r.costUsd.toFixed(5)}
                      {model.id === cheapestId && <span className="text-[8px] ml-0.5">💰</span>}
                    </span>
                  </td>

                  {/* Tokens */}
                  <td className="px-4 py-3 text-center text-[#6b6560] tabular-nums">{r.tokensUsed}</td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="px-5 py-3 border-t border-[#e8e4da] flex flex-wrap gap-4 text-[10px] text-[#6b6560] bg-[#f5f2ec]/50">
        <span>⚡ Fastest response</span>
        <span>💰 Lowest cost</span>
        <span>★ Highest confidence</span>
      </div>
    </div>
  );
}
