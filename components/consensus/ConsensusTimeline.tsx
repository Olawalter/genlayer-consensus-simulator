"use client";

import { motion } from "framer-motion";
import { Send, Users, Calculator, CheckCircle2, XCircle, AlertTriangle, Scale } from "lucide-react";
import { cn } from "@/lib/utils";
import type { SimulationStatus } from "@/services/simulationService";

interface Step {
  id: SimulationStatus | string;
  label: string;
  icon: React.ElementType;
  activeStatuses: SimulationStatus[];
  completedStatuses: SimulationStatus[];
}

const STEPS: Step[] = [
  {
    id: "submit",
    label: "Claim Submitted",
    icon: Send,
    activeStatuses: ["submitting"],
    completedStatuses: ["running", "computing", "accepted", "rejected", "appeal_triggered", "appealing", "finalized"],
  },
  {
    id: "validate",
    label: "Validator Voting",
    icon: Users,
    activeStatuses: ["running"],
    completedStatuses: ["computing", "accepted", "rejected", "appeal_triggered", "appealing", "finalized"],
  },
  {
    id: "compute",
    label: "Equivalence Check",
    icon: Calculator,
    activeStatuses: ["computing"],
    completedStatuses: ["accepted", "rejected", "appeal_triggered", "appealing", "finalized"],
  },
  {
    id: "consensus",
    label: "Consensus / Appeal",
    icon: Scale,
    activeStatuses: ["appeal_triggered", "appealing"],
    completedStatuses: ["accepted", "rejected", "finalized"],
  },
  {
    id: "finalize",
    label: "Finalized",
    icon: CheckCircle2,
    activeStatuses: ["accepted", "rejected", "finalized"],
    completedStatuses: [],
  },
];

interface ConsensusTimelineProps {
  status: SimulationStatus;
}

export function ConsensusTimeline({ status }: ConsensusTimelineProps) {
  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/50 p-4">
      <h3 className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-4">
        Optimistic Democracy — Transaction Lifecycle
      </h3>
      <div className="relative flex items-center justify-between">
        {/* connecting line */}
        <div className="absolute top-4 left-0 right-0 h-[2px] bg-[#e8e4da]" />

        {STEPS.map((step, i) => {
          const isActive    = step.activeStatuses.includes(status);
          const isCompleted = step.completedStatuses.includes(status);
          const Icon = step.icon;

          return (
            <div key={step.id} className="relative flex flex-col items-center gap-2 z-10">
              <motion.div
                animate={isActive ? { scale: [1, 1.15, 1] } : {}}
                transition={{ duration: 1.5, repeat: Infinity }}
                className={cn(
                  "h-8 w-8 rounded-full border-2 flex items-center justify-center",
                  isCompleted && "bg-[#2d2a26] border-[#2d2a26]",
                  isActive    && "bg-white border-[#2d2a26] shadow-md",
                  !isCompleted && !isActive && "bg-white border-[#d8d4c8]"
                )}
              >
                <Icon className={cn(
                  "h-3.5 w-3.5",
                  isCompleted && "text-[#efece4]",
                  isActive    && "text-[#2d2a26]",
                  !isCompleted && !isActive && "text-[#d8d4c8]"
                )} />
              </motion.div>
              <span className={cn(
                "text-[10px] text-center leading-tight max-w-[60px]",
                (isActive || isCompleted) ? "text-[#1a1a1a] font-medium" : "text-[#d8d4c8]"
              )}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
