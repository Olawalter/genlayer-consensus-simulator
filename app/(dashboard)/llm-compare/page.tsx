"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LLM_MODELS } from "@/lib/llm/models";
import { runLLMComparison, type LLMResponse } from "@/lib/llm/simulator";
import { useLLMCompareStore } from "@/store/llmCompareStore";
import { ModelCard } from "@/components/llm/ModelCard";
import { ResponseCard } from "@/components/llm/ResponseCard";
import { ScoringMatrix } from "@/components/llm/ScoringMatrix";
import { AgreementHeatmap } from "@/components/llm/AgreementHeatmap";
import { ComparisonForm } from "@/components/llm/ComparisonForm";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function LLMComparePage() {
  const {
    currentRun, loadingModelIds, selectedModelId,
    startRun, updateResponses, finalizeRun, selectModel,
  } = useLLMCompareStore();

  const [isRunning, setIsRunning] = useState(false);

  const handleRun = useCallback(async (claim: string) => {
    setIsRunning(true);
    const runId = startRun(claim);

    await runLLMComparison(LLM_MODELS, claim, (partial, loading) => {
      updateResponses(runId, partial, loading);
    });

    const finalResponses: Record<string, LLMResponse> = {};
    for (const m of LLM_MODELS) {
      const r = useLLMCompareStore.getState().currentRun?.responses[m.id];
      if (r) finalResponses[m.id] = r;
    }
    finalizeRun(runId, finalResponses);
    setIsRunning(false);
  }, [startRun, updateResponses, finalizeRun]);

  const hasResponses = currentRun && Object.keys(currentRun.responses).length > 0;
  const allDone = currentRun && Object.keys(currentRun.responses).length === LLM_MODELS.length;

  const fastestId = allDone
    ? LLM_MODELS.filter((m) => currentRun.responses[m.id])
        .reduce((a, b) =>
          currentRun.responses[a.id].latencyMs < currentRun.responses[b.id].latencyMs ? a : b
        ).id
    : null;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">LLM Comparison Center</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            GenLayer assigns each validator a different LLM. See how GPT-4o, Claude 3.5 Sonnet,
            Llama 3, Mistral Large, and Gemini 1.5 Pro evaluate the same claim simultaneously —
            and understand why their disagreements trigger the Equivalence Principle.
          </p>
        </div>

        <Tabs defaultValue="compare">
          <TabsList className="mb-6">
            <TabsTrigger value="compare">Live Comparison</TabsTrigger>
            <TabsTrigger value="models">Model Profiles</TabsTrigger>
            {allDone && <TabsTrigger value="analysis">Analysis</TabsTrigger>}
          </TabsList>

          {/* ── Compare tab ── */}
          <TabsContent value="compare">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: form */}
              <div className="lg:col-span-1 space-y-4">
                <ComparisonForm onRun={handleRun} disabled={isRunning} />

                {currentRun && (
                  <div className="rounded-xl border border-[#d8d4c8] bg-white/50 p-4">
                    <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-2">Claim</p>
                    <p className="text-xs text-[#1a1a1a] leading-relaxed">&ldquo;{currentRun.claim}&rdquo;</p>
                    <div className="mt-3 flex items-center justify-between text-[11px] text-[#6b6560]">
                      <span>{Object.keys(currentRun.responses).length}/{LLM_MODELS.length} responded</span>
                      {currentRun.completedAt && (
                        <span>{((currentRun.completedAt - currentRun.startedAt) / 1000).toFixed(1)}s total</span>
                      )}
                    </div>
                  </div>
                )}

                {allDone && currentRun && (
                  <AgreementHeatmap responses={currentRun.responses} />
                )}
              </div>

              {/* Right: response cards grid */}
              <div className="lg:col-span-2">
                {!currentRun ? (
                  <div className="h-full rounded-xl border-2 border-dashed border-[#d8d4c8] flex flex-col items-center justify-center py-20 text-center px-8">
                    <div className="text-4xl mb-4">🤖</div>
                    <h3 className="text-base font-semibold text-[#1a1a1a] mb-2">Five models, one claim</h3>
                    <p className="text-sm text-[#6b6560] max-w-xs leading-relaxed">
                      Submit a claim to see all five GenLayer validator LLMs respond in real time —
                      simultaneously, independently, with full reasoning.
                    </p>
                    <div className="mt-5 flex flex-wrap justify-center gap-2">
                      {LLM_MODELS.map((m) => (
                        <span key={m.id} className="text-xs rounded-full border border-[#e8e4da] bg-white/50 px-3 py-1 text-[#6b6560]">
                          {m.name}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                    {LLM_MODELS.map((model, i) => (
                      <ResponseCard
                        key={model.id}
                        modelId={model.id}
                        response={currentRun.responses[model.id]}
                        isLoading={loadingModelIds.includes(model.id) || (isRunning && !currentRun.responses[model.id])}
                        index={i}
                        isWinner={allDone === true && model.id === fastestId}
                      />
                    ))}
                  </div>
                )}

                {allDone && currentRun && (
                  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-5">
                    <ScoringMatrix responses={currentRun.responses} />
                  </motion.div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* ── Models tab ── */}
          <TabsContent value="models">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {LLM_MODELS.map((model, i) => (
                <ModelCard
                  key={model.id}
                  model={model}
                  isSelected={selectedModelId === model.id}
                  onClick={() => selectModel(selectedModelId === model.id ? null : model.id)}
                  index={i}
                />
              ))}
            </div>

            {/* Selected model detail */}
            <AnimatePresence>
              {selectedModelId && (() => {
                const m = LLM_MODELS.find((x) => x.id === selectedModelId);
                if (!m) return null;
                return (
                  <motion.div
                    key={m.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="mt-6 rounded-xl border border-[#d8d4c8] bg-white/60 p-6"
                  >
                    <h3 className="text-base font-bold text-[#1a1a1a] mb-1">{m.name} — Deep Dive</h3>
                    <p className="text-sm text-[#6b6560] leading-relaxed mb-5">{m.description}</p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-[#6b6560] mb-1.5 font-semibold">Strengths</p>
                        <ul className="space-y-1">{m.strengths.map((s) => <li key={s} className="text-xs text-green-700 flex items-start gap-1"><span>✓</span>{s}</li>)}</ul>
                      </div>
                      <div>
                        <p className="text-xs text-[#6b6560] mb-1.5 font-semibold">Weaknesses</p>
                        <ul className="space-y-1">{m.weaknesses.map((s) => <li key={s} className="text-xs text-red-600 flex items-start gap-1"><span>·</span>{s}</li>)}</ul>
                      </div>
                      <div>
                        <p className="text-xs text-[#6b6560] mb-1.5 font-semibold">Specifications</p>
                        <ul className="space-y-1 text-xs text-[#6b6560]">
                          <li>Context: <strong className="text-[#1a1a1a]">{(m.contextWindow / 1000).toFixed(0)}K tokens</strong></li>
                          <li>Speed: <strong className="text-[#1a1a1a]">{m.outputSpeed} t/s</strong></li>
                          <li>Latency: <strong className="text-[#1a1a1a]">{m.latencyMs.min}–{m.latencyMs.max}ms</strong></li>
                          <li>Cost: <strong className="text-[#1a1a1a]">${m.costPer1kTokens}/1K tokens</strong></li>
                        </ul>
                      </div>
                      <div>
                        <p className="text-xs text-[#6b6560] mb-1.5 font-semibold">GenLayer Role</p>
                        <p className="text-xs text-[#1a1a1a]">Used by <strong>{m.usedByValidator}</strong> validator</p>
                        <p className="text-xs text-[#6b6560] mt-1 leading-relaxed">
                          {m.provider}&apos;s {m.family} model handles all <code className="text-[10px] bg-[#e8e4da] px-1 rounded">gl.exec_prompt()</code> calls for this validator node.
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
              })()}
            </AnimatePresence>
          </TabsContent>

          {/* ── Analysis tab (only when comparison is done) ── */}
          {allDone && currentRun && (
            <TabsContent value="analysis">
              <div className="space-y-5 max-w-4xl">
                <ScoringMatrix responses={currentRun.responses} />
                <AgreementHeatmap responses={currentRun.responses} />

                {/* Key insight */}
                <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-5">
                  <h3 className="text-sm font-semibold text-indigo-800 mb-2">Why Models Disagree</h3>
                  <p className="text-xs text-indigo-700 leading-relaxed">
                    Even when evaluating the exact same claim, different LLMs reach different verdicts
                    due to their training data, RLHF tuning, and inherent biases. This is precisely why
                    GenLayer uses multiple validators — the Equivalence Principle mathematically resolves
                    these disagreements into a single on-chain outcome rather than relying on any single
                    model&apos;s judgment.
                  </p>
                </div>
              </div>
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );
}
