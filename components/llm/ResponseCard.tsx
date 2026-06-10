"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Clock, Hash, DollarSign, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { MODEL_COLORS, LLM_MODELS } from "@/lib/llm/models";
import type { LLMResponse } from "@/lib/llm/simulator";

interface ResponseCardProps {
  modelId: string;
  response: LLMResponse | undefined;
  isLoading: boolean;
  index: number;
  isWinner?: boolean;
}

const VOTE_CFG = {
  ACCEPT:    { icon: CheckCircle2, variant: "accept"    as const, bg: "bg-green-50",  border: "border-green-200" },
  REJECT:    { icon: XCircle,      variant: "reject"    as const, bg: "bg-red-50",    border: "border-red-200" },
  UNCERTAIN: { icon: HelpCircle,   variant: "uncertain" as const, bg: "bg-amber-50",  border: "border-amber-200" },
};

export function ResponseCard({ modelId, response, isLoading, index, isWinner }: ResponseCardProps) {
  const model  = LLM_MODELS.find((m) => m.id === modelId);
  if (!model) return null;

  const colors  = MODEL_COLORS[model.color] ?? MODEL_COLORS.emerald;
  const voteCfg = response ? VOTE_CFG[response.vote] : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className={cn(
        "rounded-xl border-2 flex flex-col transition-all",
        isLoading && "border-[#d8d4c8]",
        response && voteCfg?.border,
        response && voteCfg?.bg,
        !response && !isLoading && "border-[#e8e4da] bg-white/30",
        isWinner && "ring-2 ring-offset-2 ring-[#2d2a26]"
      )}
    >
      {/* Model header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#e8e4da]/60">
        <div className="flex items-center gap-2">
          <div className={cn("h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold", colors.bg, colors.text)}>
            {model.avatar}
          </div>
          <div>
            <p className="text-xs font-semibold text-[#1a1a1a] leading-tight">{model.name}</p>
            <p className="text-[10px] text-[#6b6560]">{model.provider} · {model.usedByValidator}</p>
          </div>
        </div>
        {isWinner && (
          <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-[#2d2a26] text-[#efece4]">Fastest</span>
        )}
      </div>

      {/* Body */}
      <div className="flex-1 p-4">
        {/* Loading */}
        {isLoading && !response && (
          <div className="flex flex-col items-center justify-center py-8 gap-3">
            <Loader2 className="h-5 w-5 text-[#6b6560] animate-spin" />
            <p className="text-xs text-[#6b6560]">Querying {model.name}…</p>
            <div className="w-full">
              <Progress value={undefined} className="h-1" />
            </div>
          </div>
        )}

        {/* Response */}
        <AnimatePresence>
          {response && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
              className="space-y-3"
            >
              {/* Vote badge + confidence */}
              <div className="flex items-center justify-between">
                {voteCfg && (
                  <Badge variant={voteCfg.variant} className="text-xs">
                    <voteCfg.icon className="h-3 w-3 mr-1" /> {response.vote}
                  </Badge>
                )}
                <span className="text-xs font-semibold text-[#1a1a1a] tabular-nums">
                  {Math.round(response.confidence * 100)}% conf.
                </span>
              </div>

              <Progress value={Math.round(response.confidence * 100)} className="h-1.5" />

              {/* Reasoning */}
              <div className="rounded-lg bg-white/60 p-3 border border-[#e8e4da]">
                <p className="text-[11px] text-[#1a1a1a] leading-relaxed whitespace-pre-line line-clamp-8">
                  {response.reasoning}
                </p>
              </div>

              {/* Metrics */}
              <div className="flex flex-wrap gap-3 text-[10px] text-[#6b6560] pt-1 border-t border-[#e8e4da]">
                <span className="flex items-center gap-1">
                  <Clock className="h-2.5 w-2.5" />{response.latencyMs}ms
                </span>
                <span className="flex items-center gap-1">
                  <Hash className="h-2.5 w-2.5" />{response.tokensUsed} tokens
                </span>
                <span className="flex items-center gap-1">
                  <DollarSign className="h-2.5 w-2.5" />${response.costUsd.toFixed(5)}
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {!response && !isLoading && (
          <p className="text-xs text-[#6b6560] text-center py-8 italic">Waiting for comparison run…</p>
        )}
      </div>
    </motion.div>
  );
}
