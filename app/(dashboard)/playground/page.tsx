"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { runSimulation, runAppeal, type SimulationRun } from "@/services/simulationService";
import { useSimulationStore } from "@/store/simulationStore";
import { useAppealStore } from "@/store/appealStore";
import { recordSimulationVotes } from "@/lib/validators/recordVotes";
import { ClaimForm } from "@/components/consensus/ClaimForm";
import { ValidatorCard } from "@/components/validators/ValidatorCard";
import { ConsensusStatus } from "@/components/consensus/ConsensusStatus";
import { ConsensusTimeline } from "@/components/consensus/ConsensusTimeline";
import { SimulationResult } from "@/components/consensus/SimulationResult";
import { AppealTrigger } from "@/components/appeals/AppealTrigger";

export default function PlaygroundPage() {
  const { currentRun, isRunning, setCurrentRun, clearCurrentRun, addToHistory } = useSimulationStore();
  const { createAppeal } = useAppealStore();
  const [localRun, setLocalRun] = useState<SimulationRun | null>(null);

  const activeRun = localRun ?? currentRun;

  const handleSimulate = useCallback(async (claim: string, category: string) => {
    setLocalRun(null);
    const finalRun = await runSimulation(claim, category, (update) => {
      setLocalRun({ ...update });
      setCurrentRun({ ...update });
    });
    recordSimulationVotes(finalRun);
    addToHistory(finalRun);
  }, [setCurrentRun, addToHistory]);

  const handleAppeal = useCallback(async (reason: string) => {
    if (!activeRun) return;
    // Register in appeals store before running
    createAppeal(activeRun, reason);
    const finalRun = await runAppeal(activeRun, reason, (update) => {
      setLocalRun({ ...update });
      setCurrentRun({ ...update });
    });
    recordSimulationVotes(finalRun);
    addToHistory(finalRun);
  }, [activeRun, setCurrentRun, addToHistory, createAppeal]);

  const handleReset = useCallback(() => {
    setLocalRun(null);
    clearCurrentRun();
  }, [clearCurrentRun]);

  const status = activeRun?.status ?? "idle";
  const showAppeal     = status === "appeal_triggered" && !isRunning;
  const showResult     = ["accepted", "rejected", "appeal_triggered", "finalized"].includes(status) && !isRunning;
  const showValidators = activeRun && activeRun.validators.length > 0;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">Consensus Playground</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            Submit a subjective claim and watch GenLayer&apos;s Optimistic Democracy in action.
            Five AI validators independently evaluate the claim and attempt to reach consensus
            through the Equivalence Principle.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-4">
            <AnimatePresence>
              {(!activeRun || showResult) && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <ClaimForm onSubmit={handleSimulate} disabled={isRunning} />
                </motion.div>
              )}
            </AnimatePresence>

            {activeRun && <ConsensusStatus status={status} round={activeRun.round} />}
            {activeRun && <ConsensusTimeline status={status} />}
            {showAppeal && <AppealTrigger onAppeal={handleAppeal} disabled={isRunning} />}

            {showResult && activeRun?.consensusResult && !showAppeal && (
              <SimulationResult run={activeRun} onReset={handleReset} onAppeal={handleAppeal} />
            )}
          </div>

          <div className="lg:col-span-2">
            {!showValidators ? (
              <div className="h-full rounded-xl border-2 border-dashed border-[#d8d4c8] flex flex-col items-center justify-center py-20 text-center px-8">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-base font-semibold text-[#1a1a1a] mb-2">Waiting for a claim</h3>
                <p className="text-sm text-[#6b6560] max-w-xs leading-relaxed">
                  Submit a claim on the left to start the simulation. Watch 5 AI validators
                  independently reason about your claim in real time.
                </p>
                <div className="mt-6 flex flex-wrap gap-2 justify-center text-xs text-[#6b6560]">
                  {["Analytical", "Creative", "Strict", "Lenient", "Balanced"].map((p) => (
                    <span key={p} className="rounded-full border border-[#e8e4da] bg-white/50 px-3 py-1">{p}</span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-[#1a1a1a]">
                    Validator Network
                    {activeRun.round > 1 && (
                      <span className="ml-2 text-xs text-purple-600 font-normal">Appeal Round {activeRun.round}</span>
                    )}
                  </h2>
                  <span className="text-xs text-[#6b6560]">
                    {activeRun.validators.filter((v) => v.status === "voted").length} / {activeRun.validators.length} voted
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                  <AnimatePresence>
                    {activeRun.validators.map((validator, i) => (
                      <ValidatorCard key={validator.id} validator={validator} index={i} />
                    ))}
                  </AnimatePresence>
                </div>

                {isRunning && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="rounded-lg border border-[#d8d4c8] bg-white/40 p-3 text-xs text-[#6b6560] leading-relaxed">
                    <span className="font-medium text-[#1a1a1a]">Equivalence Principle: </span>
                    Each validator runs the claim through its assigned LLM independently.
                    Results are compared — if 60%+ agree, consensus is reached. Otherwise, an appeal is triggered.
                  </motion.div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
