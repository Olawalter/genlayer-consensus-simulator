"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { LLM_MODELS, MODEL_COLORS } from "@/lib/llm/models";
import type { LLMResponse } from "@/lib/llm/simulator";

interface AgreementHeatmapProps {
  responses: Record<string, LLMResponse>;
}

function agreementColor(a: string, b: string): string {
  if (a === b) return "bg-green-200 text-green-800";
  if (a === "UNCERTAIN" || b === "UNCERTAIN") return "bg-amber-100 text-amber-700";
  return "bg-red-100 text-red-700";
}

function agreementLabel(a: string, b: string): string {
  if (a === b) return "Agree";
  if (a === "UNCERTAIN" || b === "UNCERTAIN") return "Partial";
  return "Disagree";
}

export function AgreementHeatmap({ responses }: AgreementHeatmapProps) {
  const models = LLM_MODELS.filter((m) => responses[m.id]);
  if (models.length < 2) return null;

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5">
      <p className="text-sm font-semibold text-[#1a1a1a] mb-1">Agreement Heatmap</p>
      <p className="text-xs text-[#6b6560] mb-4">How each model pair compares on this claim.</p>

      <div className="overflow-x-auto">
        <table className="text-[10px]">
          <thead>
            <tr>
              <th className="w-24" />
              {models.map((m) => {
                const colors = MODEL_COLORS[m.color] ?? MODEL_COLORS.emerald;
                return (
                  <th key={m.id} className="px-2 py-1 text-center">
                    <div className={cn("h-6 w-6 rounded flex items-center justify-center font-bold mx-auto", colors.bg, colors.text)}>
                      {m.avatar}
                    </div>
                    <p className="mt-1 font-normal text-[#6b6560]">{m.name.split(" ")[0]}</p>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {models.map((rowModel, ri) => {
              const colors = MODEL_COLORS[rowModel.color] ?? MODEL_COLORS.emerald;
              return (
                <tr key={rowModel.id}>
                  <td className="pr-3 py-1">
                    <div className="flex items-center gap-1.5">
                      <div className={cn("h-5 w-5 rounded flex items-center justify-center font-bold text-[9px]", colors.bg, colors.text)}>
                        {rowModel.avatar}
                      </div>
                      <span className="font-medium text-[#1a1a1a]">{rowModel.name.split(" ")[0]}</span>
                    </div>
                  </td>
                  {models.map((colModel, ci) => {
                    const a = responses[rowModel.id].vote;
                    const b = responses[colModel.id].vote;
                    const isDiag = ri === ci;
                    return (
                      <td key={colModel.id} className="px-2 py-1 text-center">
                        <motion.div
                          initial={{ scale: 0.6, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: (ri + ci) * 0.04 }}
                          className={cn(
                            "rounded-md px-2 py-1 font-semibold",
                            isDiag ? "bg-[#2d2a26] text-[#efece4]" : agreementColor(a, b)
                          )}
                        >
                          {isDiag ? a.slice(0, 3) : agreementLabel(a, b)}
                        </motion.div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Agreement summary */}
      {(() => {
        const pairs: [string, string][] = [];
        for (let i = 0; i < models.length; i++)
          for (let j = i + 1; j < models.length; j++)
            pairs.push([models[i].id, models[j].id]);
        const agreed = pairs.filter(([a, b]) => responses[a].vote === responses[b].vote).length;
        const pct    = Math.round((agreed / pairs.length) * 100);
        return (
          <p className="mt-4 text-xs text-[#6b6560] border-t border-[#e8e4da] pt-3">
            <strong className="text-[#1a1a1a]">{agreed}/{pairs.length}</strong> model pairs ({pct}%) reached the same verdict on this claim.
            {pct >= 80 ? " Strong cross-model consensus." : pct >= 60 ? " Moderate agreement." : " High disagreement — this is a genuinely subjective claim."}
          </p>
        );
      })()}
    </div>
  );
}
