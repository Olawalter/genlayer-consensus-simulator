"""Phase 7: Equivalence Explorer + Optimistic Democracy Dashboard."""
import pathlib, json

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  WROTE  {rel}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Equivalence scoring library — extended for the explorer
# ─────────────────────────────────────────────────────────────────────────────
w("lib/equivalence/scorer.ts", '''\
/**
 * Extended equivalence scoring utilities for the Equivalence Explorer.
 * Supports both Comparative and Non-Comparative modes as defined in GenLayer.
 */

export type EquivalenceMode = "comparative" | "non_comparative";

export interface ComparativeConfig {
  mode: "comparative";
  marginPercent: number;   // 0–50: how wide the equivalence band is
  threshold: number;       // 0–1: minimum agreement ratio
}

export interface NonComparativeConfig {
  mode: "non_comparative";
  criteria: string;        // human-readable criteria description
  threshold: number;       // 0–1: minimum agreement ratio
}

export type EquivalenceConfig = ComparativeConfig | NonComparativeConfig;

export interface VoteInput {
  label: string;
  value: number;   // 0–1 normalised score (1 = accept)
}

export interface EquivalenceScoreResult {
  mode: EquivalenceMode;
  votes: VoteInput[];
  agreement: number;         // 0–1 how much votes cluster
  withinMargin: number;      // count of votes within margin of the mean
  outsideMargin: number;
  mean: number;
  spread: number;            // standard deviation
  passes: boolean;
  bandLow: number;
  bandHigh: number;
  explanation: string;
}

export function scoreComparative(
  votes: VoteInput[],
  cfg: ComparativeConfig
): EquivalenceScoreResult {
  const values = votes.map((v) => v.value);
  const mean   = values.reduce((s, v) => s + v, 0) / values.length;
  const spread = Math.sqrt(values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length);

  const halfBand  = cfg.marginPercent / 100 / 2;
  const bandLow   = Math.max(0, mean - halfBand);
  const bandHigh  = Math.min(1, mean + halfBand);

  const withinMargin  = values.filter((v) => v >= bandLow && v <= bandHigh).length;
  const outsideMargin = values.length - withinMargin;
  const agreement     = withinMargin / values.length;
  const passes        = agreement >= cfg.threshold;

  const explanation = passes
    ? `${withinMargin}/${votes.length} validator outputs fall within the ±${cfg.marginPercent / 2}% equivalence band around the mean (${Math.round(mean * 100)}%). Comparative equivalence is satisfied.`
    : `Only ${withinMargin}/${votes.length} outputs are within the equivalence band. The spread of ${Math.round(spread * 100)}% exceeds what comparative equivalence allows. An appeal would be triggered.`;

  return { mode: "comparative", votes, agreement, withinMargin, outsideMargin, mean, spread, passes, bandLow, bandHigh, explanation };
}

export function scoreNonComparative(
  votes: VoteInput[],
  cfg: NonComparativeConfig
): EquivalenceScoreResult {
  // Non-comparative: each output is independently judged against criteria.
  // value >= 0.5 → meets criteria; value < 0.5 → does not meet criteria.
  const meetsCriteria = votes.filter((v) => v.value >= 0.5).length;
  const agreement     = meetsCriteria / votes.length;
  const passes        = agreement >= cfg.threshold;
  const mean          = votes.reduce((s, v) => s + v.value, 0) / votes.length;
  const spread        = Math.sqrt(votes.reduce((s, v) => s + (v.value - mean) ** 2, 0) / votes.length);

  const explanation = passes
    ? `${meetsCriteria}/${votes.length} validators judged the output as meeting the criteria "${cfg.criteria}". Non-comparative equivalence is satisfied.`
    : `Only ${meetsCriteria}/${votes.length} validators found the output meets "${cfg.criteria}". Non-comparative equivalence fails — the claim does not consistently satisfy the defined criteria.`;

  return { mode: "non_comparative", votes, agreement, withinMargin: meetsCriteria, outsideMargin: votes.length - meetsCriteria, mean, spread, passes, bandLow: 0.5, bandHigh: 1, explanation };
}

export function computeEquivalenceDetailed(
  votes: VoteInput[],
  cfg: EquivalenceConfig
): EquivalenceScoreResult {
  return cfg.mode === "comparative"
    ? scoreComparative(votes, cfg)
    : scoreNonComparative(votes, cfg);
}

// ── Pre-built scenarios for the explorer ─────────────────────────────────────

export interface ExplorerScenario {
  id: string;
  title: string;
  description: string;
  mode: EquivalenceMode;
  claim: string;
  votes: VoteInput[];
  config: EquivalenceConfig;
  category: string;
}

export const EXPLORER_SCENARIOS: ExplorerScenario[] = [
  {
    id: "s1",
    title: "Unanimous Accept",
    description: "All five validators strongly agree the claim meets the criteria.",
    mode: "comparative",
    category: "unanimous",
    claim: "The freelancer delivered the website on time with all agreed features.",
    votes: [
      { label: "Atlas",  value: 0.92 },
      { label: "Nova",   value: 0.89 },
      { label: "Orion",  value: 0.88 },
      { label: "Lyra",   value: 0.94 },
      { label: "Zephyr", value: 0.91 },
    ],
    config: { mode: "comparative", marginPercent: 20, threshold: 0.6 },
  },
  {
    id: "s2",
    title: "Majority Accept",
    description: "Four validators accept, one strict validator rejects. Equivalence still passes.",
    mode: "comparative",
    category: "majority",
    claim: "The product review reflects a genuine user experience with fair criticism.",
    votes: [
      { label: "Atlas",  value: 0.75 },
      { label: "Nova",   value: 0.82 },
      { label: "Orion",  value: 0.28 },
      { label: "Lyra",   value: 0.80 },
      { label: "Zephyr", value: 0.71 },
    ],
    config: { mode: "comparative", marginPercent: 30, threshold: 0.6 },
  },
  {
    id: "s3",
    title: "Split — Appeal Triggered",
    description: "Validators are evenly split. Agreement falls below 60% threshold.",
    mode: "comparative",
    category: "split",
    claim: "The consultant substantially completed the project to industry standard.",
    votes: [
      { label: "Atlas",  value: 0.62 },
      { label: "Nova",   value: 0.58 },
      { label: "Orion",  value: 0.31 },
      { label: "Lyra",   value: 0.74 },
      { label: "Zephyr", value: 0.40 },
    ],
    config: { mode: "comparative", marginPercent: 20, threshold: 0.6 },
  },
  {
    id: "s4",
    title: "Non-Comparative: Criteria Met",
    description: "Each validator independently checks whether the output meets the defined criteria.",
    mode: "non_comparative",
    category: "non_comparative",
    claim: "This AI-generated summary is factually accurate and unbiased.",
    votes: [
      { label: "Atlas",  value: 0.80 },
      { label: "Nova",   value: 0.71 },
      { label: "Orion",  value: 0.55 },
      { label: "Lyra",   value: 0.88 },
      { label: "Zephyr", value: 0.62 },
    ],
    config: { mode: "non_comparative", criteria: "factually accurate and unbiased", threshold: 0.6 },
  },
  {
    id: "s5",
    title: "Narrow Margin",
    description: "Votes cluster tightly — barely within the equivalence band. Tests the boundary.",
    mode: "comparative",
    category: "edge",
    claim: "The event raised the stated amount for charity within the stated time window.",
    votes: [
      { label: "Atlas",  value: 0.60 },
      { label: "Nova",   value: 0.65 },
      { label: "Orion",  value: 0.58 },
      { label: "Lyra",   value: 0.67 },
      { label: "Zephyr", value: 0.61 },
    ],
    config: { mode: "comparative", marginPercent: 12, threshold: 0.6 },
  },
];
''')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Equivalence Visualizer — dot plot + band overlay
# ─────────────────────────────────────────────────────────────────────────────
w("components/equivalence/EquivalenceVisualizer.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { EquivalenceScoreResult, VoteInput } from "@/lib/equivalence/scorer";

interface EquivalenceVisualizerProps {
  result: EquivalenceScoreResult;
}

const VALIDATOR_COLORS: Record<string, string> = {
  Atlas:  "#6366f1",
  Nova:   "#ec4899",
  Orion:  "#ef4444",
  Lyra:   "#22c55e",
  Zephyr: "#f59e0b",
};

export function EquivalenceVisualizer({ result }: EquivalenceVisualizerProps) {
  const { votes, mean, bandLow, bandHigh, passes, mode } = result;

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[#1a1a1a]">
          {mode === "comparative" ? "Comparative" : "Non-Comparative"} Equivalence Map
        </h3>
        <span className={cn(
          "text-xs font-semibold px-2.5 py-1 rounded-full",
          passes ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        )}>
          {passes ? "✓ Passes" : "✗ Fails"}
        </span>
      </div>

      {/* Number line visualisation */}
      <div className="relative h-20 select-none">
        {/* Base track */}
        <div className="absolute top-1/2 -translate-y-1/2 left-0 right-0 h-2 rounded-full bg-[#e8e4da]" />

        {/* Equivalence band */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{
            left:  `${bandLow  * 100}%`,
            width: `${(bandHigh - bandLow) * 100}%`,
            originX: 0,
          }}
          className={cn(
            "absolute top-1/2 -translate-y-1/2 h-4 rounded-full opacity-30",
            passes ? "bg-green-400" : "bg-red-400"
          )}
        />

        {/* Mean line */}
        <div
          className="absolute top-1/2 -translate-y-full h-5 w-0.5 bg-[#2d2a26]"
          style={{ left: `${mean * 100}%` }}
        >
          <span className="absolute -top-5 -translate-x-1/2 text-[9px] text-[#2d2a26] font-semibold whitespace-nowrap">
            μ {Math.round(mean * 100)}%
          </span>
        </div>

        {/* 60% threshold marker */}
        <div className="absolute top-0 h-full border-l-2 border-dashed border-[#6b6560]/40" style={{ left: "60%" }}>
          <span className="absolute top-0 left-1 text-[9px] text-[#6b6560] whitespace-nowrap">60% threshold</span>
        </div>

        {/* Validator dots */}
        {votes.map((v, i) => {
          const color  = VALIDATOR_COLORS[v.label] ?? "#2d2a26";
          const inside = v.value >= bandLow && v.value <= bandHigh;
          return (
            <motion.div
              key={v.label}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: i * 0.1 + 0.3, type: "spring", stiffness: 300 }}
              style={{ left: `${v.value * 100}%`, backgroundColor: color }}
              className={cn(
                "absolute top-1/2 -translate-x-1/2 -translate-y-1/2 h-5 w-5 rounded-full border-2 border-white shadow-md cursor-default",
                !inside && "ring-2 ring-red-400 ring-offset-1"
              )}
              title={`${v.label}: ${Math.round(v.value * 100)}%`}
            >
              <span className="absolute -bottom-6 -translate-x-1/2 left-1/2 text-[9px] font-semibold whitespace-nowrap" style={{ color }}>
                {v.label.slice(0, 2)}
              </span>
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-5 gap-1.5 pt-4">
        {votes.map((v) => {
          const color  = VALIDATOR_COLORS[v.label] ?? "#2d2a26";
          const inside = v.value >= bandLow && v.value <= bandHigh;
          return (
            <div key={v.label} className={cn(
              "rounded-lg border px-2 py-1.5 text-center text-[10px]",
              inside ? "border-[#e8e4da] bg-white/40" : "border-red-200 bg-red-50"
            )}>
              <div className="h-2 w-2 rounded-full mx-auto mb-1" style={{ backgroundColor: color }} />
              <p className="font-semibold text-[#1a1a1a]">{v.label}</p>
              <p className="text-[#6b6560]">{Math.round(v.value * 100)}%</p>
              <p className={cn("text-[9px]", inside ? "text-green-600" : "text-red-500")}>
                {inside ? "✓ in band" : "✗ outside"}
              </p>
            </div>
          );
        })}
      </div>

      {/* Stats row */}
      <div className="flex justify-between text-xs text-[#6b6560] border-t border-[#e8e4da] pt-3">
        <span>Band: <strong className="text-[#1a1a1a]">{Math.round(bandLow*100)}% – {Math.round(bandHigh*100)}%</strong></span>
        <span>Agreement: <strong className="text-[#1a1a1a]">{Math.round(result.agreement * 100)}%</strong></span>
        <span>Spread σ: <strong className="text-[#1a1a1a]">{Math.round(result.spread * 100)}%</strong></span>
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Equivalence Config Editor
# ─────────────────────────────────────────────────────────────────────────────
w("components/equivalence/EquivalenceConfigEditor.tsx", '''\
"use client";

import { cn } from "@/lib/utils";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import type { EquivalenceConfig } from "@/lib/equivalence/scorer";

interface EquivalenceConfigEditorProps {
  config: EquivalenceConfig;
  onChange: (cfg: EquivalenceConfig) => void;
}

export function EquivalenceConfigEditor({ config, onChange }: EquivalenceConfigEditorProps) {
  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-5">
      <div>
        <p className="text-sm font-semibold text-[#1a1a1a] mb-1">Equivalence Mode</p>
        <p className="text-xs text-[#6b6560] leading-relaxed mb-3">
          GenLayer contracts declare which mode applies. Comparative checks if outputs are
          numerically close. Non-comparative checks if each output independently meets criteria.
        </p>
        <div className="flex gap-2">
          {(["comparative", "non_comparative"] as const).map((m) => (
            <button
              key={m}
              onClick={() => {
                if (m === "comparative") {
                  onChange({ mode: "comparative", marginPercent: 20, threshold: 0.6 });
                } else {
                  onChange({ mode: "non_comparative", criteria: "meets quality standard", threshold: 0.6 });
                }
              }}
              className={cn(
                "flex-1 text-xs rounded-lg border-2 px-3 py-2 font-medium transition-all",
                config.mode === m
                  ? "border-[#2d2a26] bg-[#2d2a26] text-[#efece4]"
                  : "border-[#d8d4c8] text-[#6b6560] hover:border-[#b8b4a8]"
              )}
            >
              {m === "comparative" ? "Comparative" : "Non-Comparative"}
            </button>
          ))}
        </div>
      </div>

      <Separator />

      {/* Agreement threshold (shared) */}
      <div>
        <div className="flex justify-between mb-2">
          <Label className="text-xs font-medium">Agreement Threshold</Label>
          <span className="text-xs font-semibold text-[#2d2a26]">{Math.round(config.threshold * 100)}%</span>
        </div>
        <Slider
          min={0.5} max={1} step={0.05}
          value={[config.threshold]}
          onValueChange={([v]) => onChange({ ...config, threshold: v })}
        />
        <p className="text-[10px] text-[#6b6560] mt-1.5">
          Minimum fraction of validators that must agree for equivalence to pass.
          GenLayer default is 60%.
        </p>
      </div>

      {/* Mode-specific controls */}
      {config.mode === "comparative" && (
        <div>
          <div className="flex justify-between mb-2">
            <Label className="text-xs font-medium">Equivalence Margin</Label>
            <span className="text-xs font-semibold text-[#2d2a26]">±{config.marginPercent / 2}%</span>
          </div>
          <Slider
            min={4} max={50} step={2}
            value={[config.marginPercent]}
            onValueChange={([v]) => onChange({ ...config, marginPercent: v })}
          />
          <p className="text-[10px] text-[#6b6560] mt-1.5">
            How wide the equivalence band is around the mean output. Wider = more lenient.
          </p>
        </div>
      )}

      {config.mode === "non_comparative" && (
        <div className="rounded-lg bg-[#f5f2ec] p-3 text-xs text-[#6b6560] leading-relaxed">
          <strong className="text-[#1a1a1a]">Non-Comparative mode:</strong> Each validator independently
          evaluates whether the output meets the contract-defined criteria. Outputs scoring ≥ 50% are
          considered as &ldquo;meets criteria&rdquo;. No margin is needed — votes are binary.
        </div>
      )}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Scenario Selector
# ─────────────────────────────────────────────────────────────────────────────
w("components/equivalence/ScenarioSelector.tsx", '''\
"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { EXPLORER_SCENARIOS, type ExplorerScenario } from "@/lib/equivalence/scorer";

const CATEGORY_LABELS: Record<string, { label: string; variant: "accept" | "reject" | "uncertain" | "appealed" | "default" }> = {
  unanimous:      { label: "Unanimous",       variant: "accept" },
  majority:       { label: "Majority",        variant: "accept" },
  split:          { label: "Split",           variant: "appealed" },
  non_comparative:{ label: "Non-Comparative", variant: "secondary" as never },
  edge:           { label: "Edge Case",       variant: "uncertain" },
};

interface ScenarioSelectorProps {
  activeId: string;
  onSelect: (s: ExplorerScenario) => void;
}

export function ScenarioSelector({ activeId, onSelect }: ScenarioSelectorProps) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-3">Scenarios</p>
      {EXPLORER_SCENARIOS.map((s) => {
        const cat = CATEGORY_LABELS[s.category] ?? { label: s.category, variant: "default" as const };
        return (
          <button
            key={s.id}
            onClick={() => onSelect(s)}
            className={cn(
              "w-full text-left rounded-xl border-2 p-3.5 transition-all",
              activeId === s.id
                ? "border-[#2d2a26] bg-white/80 shadow-sm"
                : "border-[#d8d4c8] bg-white/40 hover:border-[#b8b4a8]"
            )}
          >
            <div className="flex items-center justify-between mb-1">
              <p className="text-xs font-semibold text-[#1a1a1a]">{s.title}</p>
              <Badge variant={cat.variant as never} className="text-[9px] px-1.5 py-0">{cat.label}</Badge>
            </div>
            <p className="text-[11px] text-[#6b6560] leading-relaxed line-clamp-2">{s.description}</p>
          </button>
        );
      })}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 5. Vote Input Sliders (interactive)
# ─────────────────────────────────────────────────────────────────────────────
w("components/equivalence/VoteInputPanel.tsx", '''\
"use client";

import { Slider } from "@/components/ui/slider";
import { cn } from "@/lib/utils";
import type { VoteInput } from "@/lib/equivalence/scorer";

const VALIDATOR_COLORS: Record<string, string> = {
  Atlas:  "#6366f1",
  Nova:   "#ec4899",
  Orion:  "#ef4444",
  Lyra:   "#22c55e",
  Zephyr: "#f59e0b",
};

interface VoteInputPanelProps {
  votes: VoteInput[];
  onChange: (votes: VoteInput[]) => void;
}

export function VoteInputPanel({ votes, onChange }: VoteInputPanelProps) {
  function handleChange(index: number, value: number) {
    const next = votes.map((v, i) => (i === index ? { ...v, value } : v));
    onChange(next);
  }

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-4">
      <p className="text-sm font-semibold text-[#1a1a1a]">Validator Confidence Scores</p>
      <p className="text-xs text-[#6b6560] leading-relaxed">
        Drag each slider to simulate a validator&apos;s confidence score (0 = strong reject, 1 = strong accept).
        Watch the equivalence map and result update in real time.
      </p>
      <div className="space-y-4">
        {votes.map((v, i) => {
          const color = VALIDATOR_COLORS[v.label] ?? "#2d2a26";
          const pct   = Math.round(v.value * 100);
          const label = pct >= 70 ? "ACCEPT" : pct <= 40 ? "REJECT" : "UNCERTAIN";
          const labelColor = pct >= 70 ? "text-green-600" : pct <= 40 ? "text-red-600" : "text-amber-600";
          return (
            <div key={v.label}>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: color }} />
                  <span className="text-xs font-medium text-[#1a1a1a]">{v.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn("text-[10px] font-semibold", labelColor)}>{label}</span>
                  <span className="text-xs font-semibold text-[#2d2a26] tabular-nums w-8 text-right">{pct}%</span>
                </div>
              </div>
              <Slider
                min={0} max={1} step={0.01}
                value={[v.value]}
                onValueChange={([val]) => handleChange(i, val)}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Equivalence Explorer Page
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/equivalence/page.tsx", '''\
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Democracy store — tracks live transactions in Optimistic Democracy lifecycle
# ─────────────────────────────────────────────────────────────────────────────
w("store/democracyStore.ts", '''\
import { create } from "zustand";
import { persist } from "zustand/middleware";

export type TxLifecycleStage =
  | "proposed"
  | "validator_review"
  | "equivalence_check"
  | "finality_window"
  | "challenge_period"
  | "finalized"
  | "appealed"
  | "rejected";

export interface DemocracyTransaction {
  id: string;
  claim: string;
  category: string;
  proposer: string;
  stage: TxLifecycleStage;
  validatorVotes: { name: string; vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number }[];
  equivalenceScore: number;
  round: number;
  finalityCountdownMs: number;
  startedAt: number;
  finalizedAt: number | null;
  outcome: "ACCEPTED" | "REJECTED" | "PENDING" | "APPEALED";
  blockHeight: number;
  txHash: string;
}

interface DemocracyStore {
  transactions: DemocracyTransaction[];
  activeId: string | null;
  networkStats: {
    totalTx: number;
    accepted: number;
    rejected: number;
    appealed: number;
    avgFinalityMs: number;
    currentBlock: number;
  };

  addTransaction: (tx: DemocracyTransaction) => void;
  updateTransaction: (id: string, patch: Partial<DemocracyTransaction>) => void;
  setActiveId: (id: string | null) => void;
  incrementBlock: () => void;
  clearTransactions: () => void;
}

export const useDemocracyStore = create<DemocracyStore>()(
  persist(
    (set) => ({
      transactions: [],
      activeId: null,
      networkStats: {
        totalTx:      0,
        accepted:     0,
        rejected:     0,
        appealed:     0,
        avgFinalityMs: 0,
        currentBlock: 14_400,
      },

      addTransaction: (tx) =>
        set((s) => ({
          transactions: [tx, ...s.transactions].slice(0, 50),
          activeId: tx.id,
          networkStats: {
            ...s.networkStats,
            totalTx: s.networkStats.totalTx + 1,
            currentBlock: s.networkStats.currentBlock + 1,
          },
        })),

      updateTransaction: (id, patch) =>
        set((s) => {
          const txs = s.transactions.map((t) => (t.id === id ? { ...t, ...patch } : t));
          // recompute stats on finalize
          const finalized = txs.filter((t) => t.finalizedAt !== null);
          const accepted  = txs.filter((t) => t.outcome === "ACCEPTED").length;
          const rejected  = txs.filter((t) => t.outcome === "REJECTED").length;
          const appealed  = txs.filter((t) => t.outcome === "APPEALED").length;
          const avgMs = finalized.length
            ? finalized.reduce((sum, t) => sum + (t.finalizedAt! - t.startedAt), 0) / finalized.length
            : s.networkStats.avgFinalityMs;
          return {
            transactions: txs,
            networkStats: { ...s.networkStats, accepted, rejected, appealed, avgFinalityMs: avgMs },
          };
        }),

      setActiveId: (id) => set({ activeId: id }),

      incrementBlock: () =>
        set((s) => ({
          networkStats: { ...s.networkStats, currentBlock: s.networkStats.currentBlock + 1 },
        })),

      clearTransactions: () =>
        set({
          transactions: [],
          activeId: null,
          networkStats: { totalTx: 0, accepted: 0, rejected: 0, appealed: 0, avgFinalityMs: 0, currentBlock: 14_400 },
        }),
    }),
    { name: "democracy-store", partialize: (s) => ({ transactions: s.transactions, networkStats: s.networkStats }) }
  )
);
''')

# ─────────────────────────────────────────────────────────────────────────────
# 8. Transaction Lifecycle stepper
# ─────────────────────────────────────────────────────────────────────────────
w("components/democracy/TxLifecycleStep.tsx", '''\
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 9. Transaction Feed card
# ─────────────────────────────────────────────────────────────────────────────
w("components/democracy/TxFeedCard.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Clock, Scale, Hash } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { formatAddress } from "@/lib/utils";
import type { DemocracyTransaction } from "@/store/democracyStore";

interface TxFeedCardProps {
  tx: DemocracyTransaction;
  isActive: boolean;
  onClick: () => void;
  index: number;
}

const STAGE_BADGE: Record<string, { label: string; variant: "accept" | "reject" | "appealed" | "uncertain" | "leader" | "secondary" | "outline" }> = {
  proposed:         { label: "Proposed",       variant: "secondary" },
  validator_review: { label: "Reviewing",      variant: "leader" },
  equivalence_check:{ label: "Eq. Check",      variant: "leader" },
  finality_window:  { label: "Finality",        variant: "uncertain" },
  challenge_period: { label: "Challenge",       variant: "uncertain" },
  finalized:        { label: "Finalized",       variant: "accept" },
  rejected:         { label: "Rejected",        variant: "reject" },
  appealed:         { label: "Appealed",        variant: "appealed" },
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function TxFeedCard({ tx, isActive, onClick, index }: TxFeedCardProps) {
  const badgeCfg = STAGE_BADGE[tx.stage] ?? { label: tx.stage, variant: "outline" as const };

  return (
    <motion.button
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04 }}
      onClick={onClick}
      className={cn(
        "w-full text-left rounded-xl border-2 p-4 transition-all hover:shadow-sm",
        isActive ? "border-[#2d2a26] bg-white/80" : "border-[#d8d4c8] bg-white/50 hover:border-[#b8b4a8]"
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <p className="text-xs text-[#1a1a1a] line-clamp-2 leading-relaxed flex-1">
          {tx.claim.slice(0, 90)}{tx.claim.length > 90 ? "…" : ""}
        </p>
        <Badge variant={badgeCfg.variant} className="text-[9px] px-1.5 py-0 shrink-0">{badgeCfg.label}</Badge>
      </div>
      <div className="flex items-center gap-3 text-[10px] text-[#6b6560]">
        <span className="flex items-center gap-1 font-mono"><Hash className="h-2.5 w-2.5" />{formatAddress(tx.txHash, 6)}</span>
        <span>Block {tx.blockHeight}</span>
        <span>R{tx.round}</span>
        <span className="ml-auto">{timeAgo(tx.startedAt)}</span>
      </div>
    </motion.button>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 10. Network Stats Bar for democracy
# ─────────────────────────────────────────────────────────────────────────────
w("components/democracy/DemocracyStats.tsx", '''\
"use client";

import { CheckCircle2, XCircle, Scale, Zap, Layers } from "lucide-react";
import type { DemocracyStore } from "@/store/democracyStore";

interface DemocracyStatsProps {
  stats: DemocracyStore["networkStats"] extends infer T ? T : never;
}

export function DemocracyStats({ stats }: DemocracyStatsProps) {
  const items = [
    { icon: Layers,      label: "Current Block",      value: stats.currentBlock.toLocaleString(), sub: "Asimov testnet" },
    { icon: CheckCircle2,label: "Accepted",            value: stats.accepted > 0 ? `${stats.accepted}` : "—", sub: "claims accepted" },
    { icon: XCircle,     label: "Rejected",            value: stats.rejected > 0 ? `${stats.rejected}` : "—", sub: "claims rejected" },
    { icon: Scale,       label: "Appealed",            value: stats.appealed > 0 ? `${stats.appealed}` : "—", sub: "appeal rounds triggered" },
    { icon: Zap,         label: "Avg Finality",        value: stats.avgFinalityMs > 0 ? `${(stats.avgFinalityMs / 1000).toFixed(1)}s` : "—", sub: "per transaction" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {items.map((s) => (
        <div key={s.label} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
          <div className="flex items-center gap-2 mb-2">
            <s.icon className="h-4 w-4 text-[#6b6560]" />
            <span className="text-xs text-[#6b6560]">{s.label}</span>
          </div>
          <p className="text-lg font-bold text-[#1a1a1a] leading-tight">{s.value}</p>
          <p className="text-[10px] text-[#6b6560] mt-0.5">{s.sub}</p>
        </div>
      ))}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 11. Live Transaction Runner
# ─────────────────────────────────────────────────────────────────────────────
w("components/democracy/LiveTxRunner.tsx", '''\
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 12. Democracy Dashboard Page
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/democracy/page.tsx", '''\
"use client";

import { useDemocracyStore } from "@/store/democracyStore";
import { DemocracyStats } from "@/components/democracy/DemocracyStats";
import { LiveTxRunner } from "@/components/democracy/LiveTxRunner";
import { TxFeedCard } from "@/components/democracy/TxFeedCard";
import { TxLifecycleStep } from "@/components/democracy/TxLifecycleStep";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export default function DemocracyPage() {
  const { transactions, activeId, setActiveId, clearTransactions, networkStats } = useDemocracyStore();
  const activeTx = transactions.find((t) => t.id === activeId) ?? null;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">
            Optimistic Democracy Dashboard
          </h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            GenLayer&apos;s Optimistic Democracy is the governance mechanism that turns individual
            validator votes into on-chain outcomes. Submit a claim and trace every step of its
            lifecycle — from proposal through validator review, equivalence check, finality
            window, and final commitment.
          </p>
        </div>

        {/* Stats */}
        <DemocracyStats stats={networkStats} />

        <Tabs defaultValue="submit">
          <TabsList className="mb-6">
            <TabsTrigger value="submit">Submit Transaction</TabsTrigger>
            <TabsTrigger value="feed">
              Transaction Feed
              {transactions.length > 0 && (
                <span className="ml-1.5 h-4 min-w-4 rounded-full bg-[#2d2a26] text-[#efece4] text-[9px] flex items-center justify-center px-1">
                  {transactions.length}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          {/* ── Submit ── */}
          <TabsContent value="submit">
            <div className="max-w-2xl">
              <LiveTxRunner />
            </div>
          </TabsContent>

          {/* ── Feed ── */}
          <TabsContent value="feed">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: transaction list */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">
                    {transactions.length} transactions
                  </p>
                  {transactions.length > 0 && (
                    <Button variant="ghost" size="sm" className="h-7 text-xs text-[#6b6560] hover:text-red-500"
                      onClick={clearTransactions}>
                      <Trash2 className="h-3 w-3 mr-1" /> Clear
                    </Button>
                  )}
                </div>

                {transactions.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-[#d8d4c8] py-12 text-center">
                    <p className="text-sm text-[#6b6560]">No transactions yet.</p>
                    <p className="text-xs text-[#6b6560] mt-1">Submit a claim to see it here.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {transactions.map((tx, i) => (
                      <TxFeedCard key={tx.id} tx={tx} isActive={activeId === tx.id}
                        onClick={() => setActiveId(tx.id)} index={i} />
                    ))}
                  </div>
                )}
              </div>

              {/* Right: detail */}
              {activeTx && (
                <div className="space-y-4">
                  <TxLifecycleStep stage={activeTx.stage} />

                  <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-3">
                    <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">Claim</p>
                    <p className="text-sm text-[#1a1a1a] leading-relaxed">&ldquo;{activeTx.claim}&rdquo;</p>

                    <div className="grid grid-cols-2 gap-3 pt-2 border-t border-[#e8e4da]">
                      {[
                        { label: "Outcome",          value: activeTx.outcome },
                        { label: "Equivalence Score",value: `${Math.round(activeTx.equivalenceScore * 100)}%` },
                        { label: "Round",             value: `${activeTx.round}` },
                        { label: "Block",             value: `#${activeTx.blockHeight}` },
                      ].map((item) => (
                        <div key={item.label} className="rounded-lg bg-[#f5f2ec] p-2.5">
                          <p className="text-[10px] text-[#6b6560] mb-0.5">{item.label}</p>
                          <p className="text-xs font-semibold text-[#1a1a1a]">{item.value}</p>
                        </div>
                      ))}
                    </div>

                    <div className="pt-2 border-t border-[#e8e4da]">
                      <p className="text-[10px] font-semibold text-[#6b6560] mb-2">Validator Votes</p>
                      <div className="flex flex-wrap gap-1.5">
                        {activeTx.validatorVotes.map((v) => (
                          <span key={v.name} className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                            v.vote === "ACCEPT" ? "bg-green-100 text-green-700" :
                            v.vote === "REJECT" ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
                          }`}>
                            {v.name} · {v.vote} ({Math.round(v.confidence * 100)}%)
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        {/* Educational cards */}
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              title: "Optimistic Execution",
              body: "Like Optimistic Rollups, GenLayer assumes transactions are valid and processes them immediately. The challenge period allows anyone to dispute outcomes before they are finalised.",
            },
            {
              title: "The Finality Window",
              body: "After validators reach consensus, a finality window opens (typically 5–10 blocks). Any stakeholder can challenge the outcome. If no valid challenge arrives, the result is committed to the state tree.",
            },
            {
              title: "On-Chain Settlement",
              body: "Once finality is reached, the contract state is updated. For Intelligent Contracts, this means the `@gl.public.write` function's side-effects are persisted — permanently and immutably.",
            },
          ].map((card) => (
            <div key={card.title} className="rounded-xl border border-[#d8d4c8] bg-white/40 p-5">
              <h3 className="text-sm font-semibold text-[#1a1a1a] mb-2">{card.title}</h3>
              <p className="text-xs text-[#6b6560] leading-relaxed">{card.body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 13. Fix DemocracyStats type — infer from the store directly
# ─────────────────────────────────────────────────────────────────────────────
# The `extends infer T` trick is valid but verbose — simplify to a direct type
w("components/democracy/DemocracyStats.tsx", '''\
"use client";

import { CheckCircle2, XCircle, Scale, Zap, Layers } from "lucide-react";

interface NetworkStats {
  totalTx: number;
  accepted: number;
  rejected: number;
  appealed: number;
  avgFinalityMs: number;
  currentBlock: number;
}

interface DemocracyStatsProps {
  stats: NetworkStats;
}

export function DemocracyStats({ stats }: DemocracyStatsProps) {
  const items = [
    { icon: Layers,       label: "Current Block",  value: stats.currentBlock.toLocaleString(), sub: "Asimov testnet" },
    { icon: CheckCircle2, label: "Accepted",        value: stats.accepted > 0 ? `${stats.accepted}` : "—", sub: "claims accepted" },
    { icon: XCircle,      label: "Rejected",        value: stats.rejected > 0 ? `${stats.rejected}` : "—", sub: "claims rejected" },
    { icon: Scale,        label: "Appealed",        value: stats.appealed > 0 ? `${stats.appealed}` : "—", sub: "appeal rounds triggered" },
    { icon: Zap,          label: "Avg Finality",    value: stats.avgFinalityMs > 0 ? `${(stats.avgFinalityMs / 1000).toFixed(1)}s` : "—", sub: "per transaction" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {items.map((s) => (
        <div key={s.label} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
          <div className="flex items-center gap-2 mb-2">
            <s.icon className="h-4 w-4 text-[#6b6560]" />
            <span className="text-xs text-[#6b6560]">{s.label}</span>
          </div>
          <p className="text-lg font-bold text-[#1a1a1a] leading-tight">{s.value}</p>
          <p className="text-[10px] text-[#6b6560] mt-0.5">{s.sub}</p>
        </div>
      ))}
    </div>
  );
}
''')

print("\nPhase 7 setup complete. All files written.\n")
