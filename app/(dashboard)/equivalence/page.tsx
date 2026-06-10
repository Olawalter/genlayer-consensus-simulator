"use client";

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  EXPLORER_SCENARIOS,
  computeEquivalenceDetailed,
  type VoteInput,
  type EquivalenceConfig,
  type ExplorerScenario,
} from "@/lib/equivalence/scorer";
import { ScenarioSelector } from "@/components/equivalence/ScenarioSelector";
import { EquivalenceVisualizer } from "@/components/equivalence/EquivalenceVisualizer";
import { EquivalenceConfigEditor } from "@/components/equivalence/EquivalenceConfigEditor";
import { VoteInputPanel } from "@/components/equivalence/VoteInputPanel";
import { Badge } from "@/components/ui/badge";

export default function EquivalencePage() {
  const [scenario, setScenario] = useState<ExplorerScenario>(EXPLORER_SCENARIOS[0]);
  const [votes, setVotes]   = useState<VoteInput[]>(EXPLORER_SCENARIOS[0].votes);
  const [config, setConfig] = useState<EquivalenceConfig>(EXPLORER_SCENARIOS[0].config);

  function handleScenarioSelect(s: ExplorerScenario) {
    setScenario(s);
    setVotes(s.votes.map((v) => ({ ...v })));
    setConfig({ ...s.config });
  }

  const result = useMemo(
    () => computeEquivalenceDetailed(votes, config),
    [votes, config]
  );

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">Equivalence Explorer</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            The Equivalence Principle is the mathematical heart of GenLayer consensus. Explore
            how Comparative and Non-Comparative modes work, tune the margin and threshold, and
            watch the validator dot plot update in real time.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

          {/* Left — scenario picker */}
          <div className="lg:col-span-1">
            <ScenarioSelector activeId={scenario.id} onSelect={handleScenarioSelect} />
          </div>

          {/* Right — interactive workspace */}
          <div className="lg:col-span-3 space-y-5">

            {/* Claim banner */}
            <div className="rounded-xl border border-[#d8d4c8] bg-white/60 px-5 py-3">
              <div className="flex items-start gap-2 flex-wrap">
                <Badge variant={config.mode === "comparative" ? "secondary" : "leader"} className="text-[10px] shrink-0 mt-0.5">
                  {config.mode === "comparative" ? "Comparative" : "Non-Comparative"}
                </Badge>
                <p className="text-sm text-[#1a1a1a] leading-relaxed">&ldquo;{scenario.claim}&rdquo;</p>
              </div>
            </div>

            {/* Main visualizer */}
            <EquivalenceVisualizer result={result} />

            {/* Explanation */}
            <motion.div
              key={result.passes ? "pass" : "fail"}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              className={`rounded-xl border-2 px-5 py-4 text-sm leading-relaxed ${result.passes ? "border-green-200 bg-green-50 text-green-800" : "border-red-200 bg-red-50 text-red-800"}`}
            >
              {result.explanation}
            </motion.div>

            {/* Two-column controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <VoteInputPanel votes={votes} onChange={setVotes} />
              <EquivalenceConfigEditor config={config} onChange={setConfig} />
            </div>

            {/* Educational cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              {[
                {
                  title: "Comparative Equivalence",
                  body: "Used when outputs are numerical or can be mapped to a scale. Validators' scores must cluster within a defined margin around the mean. Ideal for: price estimates, confidence percentages, time estimates.",
                },
                {
                  title: "Non-Comparative Equivalence",
                  body: "Used when outputs are categorical. Each validator independently checks if the output meets a contract-defined criterion. No comparison between validators is needed — only a majority criterion match.",
                },
              ].map((c) => (
                <div key={c.title} className="rounded-xl border border-[#d8d4c8] bg-white/40 p-4">
                  <h3 className="text-xs font-semibold text-[#1a1a1a] mb-1.5">{c.title}</h3>
                  <p className="text-xs text-[#6b6560] leading-relaxed">{c.body}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
