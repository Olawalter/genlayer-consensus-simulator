"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, AlertTriangle, Scale, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { SimulationStatus } from "@/services/simulationService";

interface ConsensusStatusProps {
  status: SimulationStatus;
  round?: number;
}

const STATUS_CONFIG: Record<SimulationStatus, {
  icon: React.ElementType;
  label: string;
  description: string;
  className: string;
  animate?: boolean;
}> = {
  idle:             { icon: Scale,         label: "Ready",              description: "Submit a claim to begin simulation.",            className: "border-[#d8d4c8] bg-white/40 text-[#6b6560]" },
  submitting:       { icon: Loader2,       label: "Submitting",         description: "Broadcasting claim to the validator network...", className: "border-indigo-200 bg-indigo-50 text-indigo-700", animate: true },
  running:          { icon: Loader2,       label: "Validators Voting",  description: "Validators are independently evaluating the claim.", className: "border-amber-200 bg-amber-50 text-amber-700", animate: true },
  computing:        { icon: Loader2,       label: "Computing Consensus","description": "Applying the Equivalence Principle...",         className: "border-blue-200 bg-blue-50 text-blue-700", animate: true },
  accepted:         { icon: CheckCircle2,  label: "Consensus: ACCEPTED","description": "The validator network has accepted this claim.", className: "border-green-200 bg-green-50 text-green-700" },
  rejected:         { icon: XCircle,       label: "Consensus: REJECTED","description": "The validator network has rejected this claim.", className: "border-red-200 bg-red-50 text-red-700" },
  appeal_triggered: { icon: AlertTriangle, label: "Appeal Triggered",   description: "Validator disagreement exceeded the Equivalence threshold.", className: "border-purple-200 bg-purple-50 text-purple-700" },
  appealing:        { icon: Loader2,       label: "Appeal in Progress", description: "Additional validators are re-evaluating the claim...", className: "border-purple-200 bg-purple-50 text-purple-700", animate: true },
  finalized:        { icon: Scale,         label: "Finalized",          description: "Final consensus achieved after appeal round.",    className: "border-[#d8d4c8] bg-white/60 text-[#1a1a1a]" },
};

export function ConsensusStatus({ status, round = 1 }: ConsensusStatusProps) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.idle;
  const Icon = cfg.icon;

  return (
    <motion.div
      key={status}
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("rounded-xl border-2 px-4 py-3 flex items-center gap-3", cfg.className)}
    >
      <Icon className={cn("h-5 w-5 shrink-0", cfg.animate && "animate-spin")} />
      <div>
        <p className="text-sm font-semibold leading-tight">
          {cfg.label}
          {round > 1 && <span className="ml-2 text-xs font-normal opacity-70">(Round {round})</span>}
        </p>
        <p className="text-xs opacity-80 leading-tight mt-0.5">{cfg.description}</p>
      </div>
    </motion.div>
  );
}
