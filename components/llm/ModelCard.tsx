"use client";

import { motion } from "framer-motion";
import { Zap, Brain, RefreshCw, DollarSign, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { MODEL_COLORS, type LLMModel } from "@/lib/llm/models";

interface ModelCardProps {
  model: LLMModel;
  isSelected: boolean;
  onClick: () => void;
  index: number;
}

export function ModelCard({ model, isSelected, onClick, index }: ModelCardProps) {
  const colors = MODEL_COLORS[model.color] ?? MODEL_COLORS.emerald;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      onClick={onClick}
      className={cn(
        "rounded-xl border-2 p-5 cursor-pointer transition-all duration-200",
        isSelected ? "border-[#2d2a26] bg-white/80 shadow-md" : "border-[#d8d4c8] bg-white/50 hover:border-[#b8b4a8]"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn("h-11 w-11 rounded-xl flex items-center justify-center text-sm font-bold shrink-0", colors.bg, colors.text)}>
            {model.avatar}
          </div>
          <div>
            <h3 className="text-sm font-bold text-[#1a1a1a]">{model.name}</h3>
            <p className="text-xs text-[#6b6560]">{model.provider}</p>
          </div>
        </div>
        <Badge variant="secondary" className="text-[10px]">{model.usedByValidator}</Badge>
      </div>

      <p className="text-xs text-[#6b6560] leading-relaxed mb-4 line-clamp-3">{model.description}</p>

      {/* Metrics */}
      <div className="space-y-2.5 mb-4">
        {[
          { icon: Brain,      label: "Reasoning Depth",  value: model.reasoningDepth,     color: "bg-indigo-500" },
          { icon: RefreshCw,  label: "Consistency",      value: model.consistencyScore,   color: "bg-green-500" },
          { icon: Zap,        label: "Accept Bias",      value: model.acceptBias,         color: "bg-amber-500" },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label}>
            <div className="flex items-center justify-between text-[11px] text-[#6b6560] mb-1">
              <span className="flex items-center gap-1"><Icon className="h-2.5 w-2.5" />{label}</span>
              <span className="font-medium text-[#1a1a1a]">{Math.round(value * 100)}%</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-[#e8e4da] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value * 100}%` }}
                transition={{ duration: 0.7, ease: "easeOut", delay: index * 0.07 + 0.3 }}
                className={cn("h-full rounded-full", color)}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Specs */}
      <div className="grid grid-cols-2 gap-2 text-[10px] text-[#6b6560] border-t border-[#e8e4da] pt-3">
        <span>Context: <strong className="text-[#1a1a1a]">{(model.contextWindow / 1000).toFixed(0)}K</strong></span>
        <span className="flex items-center gap-0.5">
          <DollarSign className="h-2.5 w-2.5" />
          <strong className="text-[#1a1a1a]">${model.costPer1kTokens}</strong>/1K
        </span>
        <span>Speed: <strong className="text-[#1a1a1a]">{model.outputSpeed} t/s</strong></span>
        <span>Latency: <strong className="text-[#1a1a1a]">{model.latencyMs.min}–{model.latencyMs.max}ms</strong></span>
      </div>

      {/* Strengths */}
      <div className="mt-3 flex flex-wrap gap-1">
        {model.strengths.slice(0, 3).map((s) => (
          <span key={s} className={cn("text-[9px] px-1.5 py-0.5 rounded-full font-medium", colors.badge, colors.text)}>
            {s}
          </span>
        ))}
      </div>
    </motion.div>
  );
}
