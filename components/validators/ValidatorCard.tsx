"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Cpu, Crown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import type { LiveValidator } from "@/services/simulationService";

interface ValidatorCardProps {
  validator: LiveValidator;
  index: number;
}

const VOTE_CONFIG = {
  ACCEPT:    { icon: CheckCircle2, label: "Accept",    variant: "accept"    as const, bg: "bg-green-50",  border: "border-green-200" },
  REJECT:    { icon: XCircle,      label: "Reject",    variant: "reject"    as const, bg: "bg-red-50",    border: "border-red-200" },
  UNCERTAIN: { icon: HelpCircle,   label: "Uncertain", variant: "uncertain" as const, bg: "bg-amber-50",  border: "border-amber-200" },
};

export function ValidatorCard({ validator, index }: ValidatorCardProps) {
  const colors = PERSONA_COLORS[validator.color] ?? PERSONA_COLORS.indigo;
  const voteConfig = validator.vote ? VOTE_CONFIG[validator.vote] : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className={cn(
        "relative rounded-xl border-2 bg-white/70 backdrop-blur-sm p-4 transition-all duration-300",
        validator.status === "thinking" && "border-[#2d2a26] shadow-lg shadow-black/10",
        validator.status === "waiting"  && "border-[#d8d4c8] opacity-60",
        validator.status === "voted" && voteConfig?.border,
        validator.status === "voted" && voteConfig?.bg,
      )}
    >
      {/* Leader crown */}
      {validator.isLeader && (
        <div className="absolute -top-2.5 left-3">
          <span className="inline-flex items-center gap-1 rounded-full bg-[#2d2a26] px-2 py-0.5 text-[10px] font-semibold text-[#efece4]">
            <Crown className="h-2.5 w-2.5" /> Leader
          </span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className={cn("h-9 w-9 rounded-lg flex items-center justify-center text-xs font-bold", colors.bg, colors.text)}>
            {validator.avatar}
          </div>
          <div>
            <p className="text-sm font-semibold text-[#1a1a1a] leading-tight">{validator.name}</p>
            <p className="text-[11px] text-[#6b6560] leading-tight flex items-center gap-1">
              <Cpu className="h-2.5 w-2.5" /> {validator.model}
            </p>
          </div>
        </div>

        {/* Status indicator */}
        <div className="flex items-center">
          {validator.status === "waiting" && (
            <span className="h-2 w-2 rounded-full bg-[#d8d4c8]" />
          )}
          {validator.status === "thinking" && (
            <span className="h-2 w-2 rounded-full bg-[#2d2a26] animate-pulse" />
          )}
          {validator.status === "voted" && voteConfig && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Badge variant={voteConfig.variant} className="text-[11px] px-2 py-0.5">
                <voteConfig.icon className="h-3 w-3 mr-1" />
                {voteConfig.label}
              </Badge>
            </motion.div>
          )}
        </div>
      </div>

      {/* Thinking animation */}
      <AnimatePresence>
        {validator.status === "thinking" && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-3"
          >
            <div className="flex items-center gap-1.5 text-xs text-[#6b6560]">
              <span>Evaluating claim</span>
              <span className="flex gap-0.5">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="h-1 w-1 rounded-full bg-[#6b6560] inline-block"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                  />
                ))}
              </span>
            </div>
            <Progress value={undefined} className="mt-2 h-1" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confidence + reasoning */}
      <AnimatePresence>
        {validator.status === "voted" && validator.confidence !== null && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            transition={{ delay: 0.1 }}
          >
            <div className="mb-2">
              <div className="flex items-center justify-between text-[11px] text-[#6b6560] mb-1">
                <span>Confidence</span>
                <span className="font-medium text-[#1a1a1a]">{Math.round((validator.confidence ?? 0) * 100)}%</span>
              </div>
              <Progress value={Math.round((validator.confidence ?? 0) * 100)} className="h-1.5" />
            </div>

            {validator.reasoning && (
              <p className="text-[11px] text-[#6b6560] leading-relaxed line-clamp-3 mt-2">
                {validator.reasoning}
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Waiting state */}
      {validator.status === "waiting" && (
        <p className="text-[11px] text-[#6b6560] italic">Waiting for evaluation slot...</p>
      )}
    </motion.div>
  );
}
