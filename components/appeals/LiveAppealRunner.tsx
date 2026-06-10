"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { ConsensusStatus } from "@/components/consensus/ConsensusStatus";
import { ConsensusGraph } from "@/components/consensus/ConsensusGraph";
import { AppealValidatorGrid } from "./AppealValidatorGrid";
import { AppealRoundCard } from "./AppealRoundCard";
import { runSimulation, runAppeal, type SimulationRun } from "@/services/simulationService";
import { useAppealStore } from "@/store/appealStore";
import type { AppealRound } from "@/store/appealStore";

const PRESET_CLAIMS = [
  { label: "Ambiguous Delivery", text: "The courier delivered the package on time according to the agreed schedule, and it arrived in the condition described in the contract." },
  { label: "Split Review",       text: "This restaurant delivers an above-average dining experience with good value for money in its price category." },
  { label: "Edge Case",          text: "The consultant completed 80% of the agreed deliverables within the project timeline, which satisfies the substantial completion clause." },
];

export function LiveAppealRunner() {
  const { createAppeal } = useAppealStore();
  const [claim, setClaim] = useState("");
  const [reason, setReason] = useState("");
  const [phase, setPhase] = useState<"setup" | "simulating" | "appealing" | "done">("setup");
  const [run, setRun] = useState<SimulationRun | null>(null);
  const [liveValidators, setLiveValidators] = useState<Parameters<typeof import("@/components/appeals/AppealValidatorGrid").AppealValidatorGrid>[0]["validators"]>([]);
  const [rounds, setRounds] = useState<AppealRound[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleStart = useCallback(async () => {
    if (!claim.trim() || !reason.trim()) return;
    setError(null);
    setPhase("simulating");
    setRounds([]);
    setLiveValidators([]);

    try {
      // Step 1: run simulation — we want it to produce a result (may or may not be a split)
      const finalRun = await runSimulation(claim.trim(), "custom", (update) => {
        setRun({ ...update });
      });
      setRun(finalRun);

      if (finalRun.consensusResult?.outcome !== "APPEAL_TRIGGERED") {
        // Force into appeal anyway for demonstration
      }

      // Step 2: register appeal in store
      createAppeal(finalRun, reason.trim());
      setPhase("appealing");

      // Step 3: run the appeal round through the simulation service
      const appealRun = await runAppeal(finalRun, reason.trim(), (update) => {
        setRun({ ...update });
        // Map to AppealValidatorUpdate shape for the grid
        const mapped = update.validators.map((v) => ({
          id: v.id,
          name: v.name,
          model: v.model,
          avatar: v.avatar,
          color: v.color,
          isOriginal: !v.name.includes(" II"),
          status: v.status,
          vote: v.vote,
          confidence: v.confidence,
          reasoning: v.reasoning,
          round: 2,
        }));
        setLiveValidators(mapped as never);
      });

      // Build a round record from the final state
      if (appealRun.consensusResult) {
        const appealRound: AppealRound = {
          roundNumber: 2,
          validatorCount: appealRun.validators.filter((v) => v.vote !== null).length,
          votes: appealRun.validators
            .filter((v) => v.vote !== null)
            .map((v) => ({ name: v.name, vote: v.vote!, confidence: v.confidence ?? 0 })),
          equivalenceResult: appealRun.consensusResult,
          outcome: appealRun.consensusResult.outcome,
          durationMs: Date.now() - finalRun.startedAt,
        };
        setRounds([appealRound]);
      }

      setPhase("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation failed.");
      setPhase("setup");
    }
  }, [claim, reason, createAppeal]);

  function handleReset() {
    setPhase("setup");
    setRun(null);
    setLiveValidators([]);
    setRounds([]);
    setError(null);
  }

  return (
    <div className="space-y-5">
      {/* Setup form */}
      <AnimatePresence>
        {phase === "setup" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-[#1a1a1a]">Run a Live Appeal Simulation</h3>
            <p className="text-xs text-[#6b6560] leading-relaxed">
              Enter a claim and an appeal reason. The simulator will first run an initial validation round,
              then immediately trigger an appeal so you can observe the full appeals process end-to-end.
            </p>

            {/* Presets */}
            <div className="flex flex-wrap gap-2">
              {PRESET_CLAIMS.map((p) => (
                <button key={p.label} onClick={() => setClaim(p.text)}
                  className="text-[11px] border border-[#d8d4c8] rounded-full px-3 py-1 bg-white/50 hover:bg-white hover:border-[#b8b4a8] transition-all text-[#6b6560] hover:text-[#1a1a1a]">
                  {p.label}
                </button>
              ))}
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs">Claim</Label>
              <Textarea value={claim} onChange={(e) => setClaim(e.target.value)}
                placeholder="Enter the claim to evaluate…"
                className="min-h-[80px] text-sm" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs">Appeal Reason</Label>
              <Textarea value={reason} onChange={(e) => setReason(e.target.value)}
                placeholder="Why should this be appealed? (e.g. validators disagreed on interpretation of 'on time')"
                className="min-h-[60px] text-sm" />
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                <AlertTriangle className="h-3.5 w-3.5 shrink-0" /> {error}
              </div>
            )}

            <Button className="w-full" onClick={handleStart} disabled={!claim.trim() || !reason.trim()}>
              <Play className="h-4 w-4 mr-2" /> Start Appeal Simulation
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Live status */}
      {run && phase !== "setup" && (
        <div className="space-y-4">
          <ConsensusStatus status={run.status} round={run.round} />

          {liveValidators.length > 0 && phase === "appealing" && (
            <div className="rounded-xl border border-[#d8d4c8] bg-white/50 p-4">
              <AppealValidatorGrid validators={liveValidators} />
            </div>
          )}

          {/* Round result */}
          {rounds.length > 0 && run.consensusResult && (
            <div className="space-y-3">
              <ConsensusGraph result={run.consensusResult} totalValidators={run.validators.length} />
              {rounds.map((r, i) => (
                <AppealRoundCard key={r.roundNumber} round={r} index={i} isLatest />
              ))}
            </div>
          )}

          {phase === "done" && (
            <Button variant="outline" className="w-full" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" /> Reset
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
