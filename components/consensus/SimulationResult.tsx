"use client";

import { motion } from "framer-motion";
import { Hash, Clock, RotateCcw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConsensusGraph } from "./ConsensusGraph";
import { formatAddress } from "@/lib/utils";
import type { SimulationRun } from "@/services/simulationService";

interface SimulationResultProps {
  run: SimulationRun;
  onReset: () => void;
  onAppeal?: (reason: string) => void;
}

export function SimulationResult({ run, onReset }: SimulationResultProps) {
  const { consensusResult, validators, txHash, status, claim, startedAt } = run;
  if (!consensusResult) return null;

  const elapsed = ((Date.now() - startedAt) / 1000).toFixed(1);
  const votedValidators = validators.filter((v) => v.vote !== null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Outcome header */}
      <div className="rounded-xl border-2 border-[#d8d4c8] bg-white/60 p-5">
        <div className="flex items-start justify-between mb-3">
          <div>
            <Badge
              variant={
                status === "accepted" ? "accept" :
                status === "rejected" ? "reject" :
                "appealed"
              }
              className="text-xs mb-2"
            >
              {status.replace("_", " ").toUpperCase()}
            </Badge>
            <p className="text-xs text-[#6b6560] leading-relaxed max-w-sm">
              &ldquo;{claim.slice(0, 120)}{claim.length > 120 ? "…" : ""}&rdquo;
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onReset} className="text-xs h-8 shrink-0">
            <RotateCcw className="h-3 w-3 mr-1" /> New
          </Button>
        </div>

        {/* Meta */}
        <div className="flex flex-wrap gap-3 text-[11px] text-[#6b6560] mt-3 pt-3 border-t border-[#e8e4da]">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> {elapsed}s
          </span>
          <span className="flex items-center gap-1">
            <span className="font-medium text-[#1a1a1a]">{votedValidators.length}</span> validators
          </span>
          {txHash && (
            <span className="flex items-center gap-1 font-mono">
              <Hash className="h-3 w-3" /> {formatAddress(txHash, 8)}
            </span>
          )}
          <span>
            Round <span className="font-medium text-[#1a1a1a]">{run.round}</span>
          </span>
        </div>
      </div>

      {/* Vote Distribution */}
      <ConsensusGraph
        result={consensusResult}
        totalValidators={votedValidators.length}
      />
    </motion.div>
  );
}
