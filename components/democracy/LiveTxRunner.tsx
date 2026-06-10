"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { TxLifecycleStep } from "./TxLifecycleStep";
import { ValidatorCard } from "@/components/validators/ValidatorCard";
import { ConsensusGraph } from "@/components/consensus/ConsensusGraph";
import { runSimulation, type SimulationRun } from "@/services/simulationService";
import { useDemocracyStore, type DemocracyTransaction, type TxLifecycleStage } from "@/store/democracyStore";
import { sleep } from "@/lib/utils";

const PRESET_CLAIMS = [
  "The developer delivered a fully functional API with all agreed endpoints and documentation, on schedule.",
  "This restaurant review is authentic and reflects a genuine paid dining experience.",
  "The crowdfunded project met its milestone by delivering a working prototype to all backers.",
];

export function LiveTxRunner() {
  const { addTransaction, updateTransaction, networkStats } = useDemocracyStore();
  const [claim, setClaim] = useState("");
  const [run,   setRun]   = useState<SimulationRun | null>(null);
  const [stage, setStage] = useState<TxLifecycleStage | null>(null);
  const [txId,  setTxId]  = useState<string | null>(null);
  const [busy,  setBusy]  = useState(false);

  const handleStart = useCallback(async () => {
    if (!claim.trim()) return;
    setBusy(true);
    setRun(null);

    const txHash = `0x${Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join("")}`;
    const id     = `tx_${Date.now()}`;
    setTxId(id);

    // Step 1: proposed
    setStage("proposed");
    await sleep(600);

    // Step 2: validator_review
    setStage("validator_review");
    const finalRun = await runSimulation(claim.trim(), "custom", (update) => {
      setRun({ ...update });
    });
    setRun(finalRun);

    // Step 3: equivalence_check
    setStage("equivalence_check");
    await sleep(700);

    const outcome = finalRun.consensusResult?.outcome ?? "REJECTED";
    const txStage: TxLifecycleStage = outcome === "APPEAL_TRIGGERED" ? "appealed"
      : outcome === "ACCEPTED"  ? "finality_window"
      : "rejected";

    // Build transaction record
    const tx: DemocracyTransaction = {
      id,
      claim: claim.trim(),
      category: "custom",
      proposer: "0xdemo...user",
      stage: txStage,
      validatorVotes: finalRun.validators
        .filter((v) => v.vote !== null)
        .map((v) => ({ name: v.name, vote: v.vote!, confidence: v.confidence ?? 0 })),
      equivalenceScore: finalRun.consensusResult?.score ?? 0,
      round: finalRun.round,
      finalityCountdownMs: 30_000,
      startedAt: finalRun.startedAt,
      finalizedAt: null,
      outcome: outcome === "ACCEPTED" ? "ACCEPTED" : outcome === "REJECTED" ? "REJECTED" : "APPEALED",
      blockHeight: networkStats.currentBlock + 1,
      txHash,
    };

    addTransaction(tx);
    setStage(txStage);

    // Step 4: finality window (if accepted)
    if (txStage === "finality_window") {
      await sleep(2000);
      setStage("finalized");
      updateTransaction(id, { stage: "finalized", finalizedAt: Date.now() });
    }

    setBusy(false);
  }, [claim, addTransaction, updateTransaction, networkStats.currentBlock]);

  function handleReset() {
    setRun(null);
    setStage(null);
    setTxId(null);
    setBusy(false);
    setClaim("");
  }

  return (
    <div className="space-y-4">
      {/* Form */}
      <AnimatePresence>
        {!stage && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-4">
            <div className="flex flex-wrap gap-2">
              {PRESET_CLAIMS.map((p, i) => (
                <button key={i} onClick={() => setClaim(p)}
                  className="text-[11px] border border-[#d8d4c8] rounded-full px-3 py-1 bg-white/50 hover:bg-white transition-all text-[#6b6560] hover:text-[#1a1a1a]">
                  Preset {i + 1}
                </button>
              ))}
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs">Claim to submit on-chain</Label>
              <Textarea value={claim} onChange={(e) => setClaim(e.target.value)}
                placeholder="Describe a subjective claim…" className="min-h-[80px] text-sm" />
            </div>
            <Button className="w-full" onClick={handleStart} disabled={!claim.trim()}>
              <Play className="h-4 w-4 mr-2" /> Submit to GenLayer Network
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Lifecycle */}
      {stage && (
        <div className="space-y-4">
          <TxLifecycleStep stage={stage} />

          {run && run.validators.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-3">
              {run.validators.map((v, i) => (
                <ValidatorCard key={v.id} validator={v} index={i} />
              ))}
            </div>
          )}

          {run?.consensusResult && (
            <ConsensusGraph result={run.consensusResult} totalValidators={run.validators.length} />
          )}

          {!busy && (
            <Button variant="outline" className="w-full" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" /> Submit Another
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
