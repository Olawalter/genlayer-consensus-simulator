"use client";

import { motion } from "framer-motion";
import { Send, Users, Calculator, Clock, Shield, CheckCircle2, XCircle, Scale } from "lucide-react";
import { cn } from "@/lib/utils";
import type { TxLifecycleStage } from "@/store/democracyStore";

interface Step {
  stage: TxLifecycleStage;
  label: string;
  sublabel: string;
  icon: React.ElementType;
}

const STEPS: Step[] = [
  { stage: "proposed",        label: "Proposed",        sublabel: "Leader submits claim",          icon: Send },
  { stage: "validator_review",label: "Validator Review", sublabel: "Network evaluates independently",icon: Users },
  { stage: "equivalence_check",label:"Equivalence Check",sublabel: "Outputs compared / checked",    icon: Calculator },
  { stage: "finality_window", label: "Finality Window",  sublabel: "Challenge period open",         icon: Clock },
  { stage: "finalized",       label: "Finalized",        sublabel: "Committed to state tree",       icon: CheckCircle2 },
];

const STAGE_ORDER: TxLifecycleStage[] = [
  "proposed", "validator_review", "equivalence_check", "finality_window",
  "challenge_period", "finalized", "appealed", "rejected",
];

function stageIndex(s: TxLifecycleStage): number {
  return STAGE_ORDER.indexOf(s);
}

interface TxLifecycleStepProps {
  stage: TxLifecycleStage;
}

export function TxLifecycleStep({ stage }: TxLifecycleStepProps) {
  const currentIdx = stageIndex(stage);
  const isTerminal = stage === "finalized" || stage === "rejected";
  const isAppealed = stage === "appealed";

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/50 p-4">
      <p className="text-[10px] font-semibold text-[#6b6560] uppercase tracking-wider mb-4">
        Optimistic Democracy — Transaction Lifecycle
      </p>
      <div className="relative flex items-start justify-between gap-1">
        {/* connecting line */}
        <div className="absolute top-4 left-4 right-4 h-[2px] bg-[#e8e4da]" />

        {STEPS.map((step, i) => {
          const stepIdx    = stageIndex(step.stage);
          const isCompleted = !isAppealed && currentIdx > stepIdx;
          const isActive    = step.stage === stage;
          const isFuture    = currentIdx < stepIdx;
          const Icon = step.icon;

          return (
            <div key={step.stage} className="relative flex flex-col items-center gap-1 z-10 flex-1">
              <motion.div
                animate={isActive ? { scale: [1, 1.12, 1] } : {}}
                transition={{ duration: 1.5, repeat: Infinity }}
                className={cn(
                  "h-8 w-8 rounded-full border-2 flex items-center justify-center shrink-0",
                  isCompleted && "bg-[#2d2a26] border-[#2d2a26]",
                  isActive    && "bg-white border-[#2d2a26] shadow-lg",
                  isFuture    && "bg-white border-[#e8e4da]",
                  isAppealed  && "opacity-50"
                )}
              >
                <Icon className={cn(
                  "h-3.5 w-3.5",
                  isCompleted && "text-[#efece4]",
                  isActive    && "text-[#2d2a26]",
                  isFuture    && "text-[#d8d4c8]"
                )} />
              </motion.div>
              <div className="text-center">
                <p className={cn("text-[9px] font-semibold leading-tight",
                  (isActive || isCompleted) ? "text-[#1a1a1a]" : "text-[#d8d4c8]"
                )}>{step.label}</p>
                <p className="text-[8px] text-[#6b6560] leading-tight max-w-[60px]">{step.sublabel}</p>
              </div>
            </div>
          );
        })}

        {/* Appeal branch */}
        {isAppealed && (
          <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-1.5 text-[10px] text-purple-600 font-medium">
            <Scale className="h-3 w-3" /> Appeal in progress
          </div>
        )}
      </div>
    </div>
  );
}
