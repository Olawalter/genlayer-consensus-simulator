"""Phase 8: LLM Comparison Center — side-by-side model outputs, scoring matrix, latency sim, model deep-dives."""
import pathlib, json

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  WROTE  {rel}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. LLM model definitions + comparison engine
# ─────────────────────────────────────────────────────────────────────────────
w("lib/llm/models.ts", '''\
export interface LLMModel {
  id: string;
  name: string;
  provider: string;
  family: string;
  contextWindow: number;      // tokens
  outputSpeed: number;        // tokens/sec (simulated)
  latencyMs: { min: number; max: number };
  strengths: string[];
  weaknesses: string[];
  acceptBias: number;         // 0-1: tendency to accept subjective claims
  reasoningDepth: number;     // 0-1: how nuanced its reasoning is
  consistencyScore: number;   // 0-1: how reproducible its outputs are
  costPer1kTokens: number;    // USD
  avatar: string;
  color: string;
  description: string;
  usedByValidator: string;
}

export const LLM_MODELS: LLMModel[] = [
  {
    id: "gpt-4o",
    name: "GPT-4o",
    provider: "OpenAI",
    family: "GPT-4",
    contextWindow: 128_000,
    outputSpeed: 62,
    latencyMs: { min: 800,  max: 2200 },
    strengths: ["Instruction following", "Code generation", "Balanced reasoning", "Long context"],
    weaknesses: ["Can be verbose", "Occasionally over-explains"],
    acceptBias: 0.55,
    reasoningDepth: 0.88,
    consistencyScore: 0.85,
    costPer1kTokens: 0.005,
    avatar: "G4",
    color: "emerald",
    description: "OpenAI's most capable and efficient model. Excels at analytical tasks with strong instruction-following. Atlas validator uses GPT-4o for its methodical, data-driven evaluation style.",
    usedByValidator: "Atlas",
  },
  {
    id: "claude-3-5-sonnet",
    name: "Claude 3.5 Sonnet",
    provider: "Anthropic",
    family: "Claude 3.5",
    contextWindow: 200_000,
    outputSpeed: 75,
    latencyMs: { min: 600,  max: 1800 },
    strengths: ["Nuanced reasoning", "Long context", "Safety alignment", "Creative writing"],
    weaknesses: ["Can be overly cautious", "Longer responses"],
    acceptBias: 0.65,
    reasoningDepth: 0.92,
    consistencyScore: 0.88,
    costPer1kTokens: 0.003,
    avatar: "CS",
    color: "orange",
    description: "Anthropic's flagship model with exceptional reasoning and the largest context window. Nova validator leverages Claude's contextual awareness and nuanced interpretations.",
    usedByValidator: "Nova",
  },
  {
    id: "llama-3-70b",
    name: "Llama 3 70B",
    provider: "Meta",
    family: "Llama 3",
    contextWindow: 8_192,
    outputSpeed: 45,
    latencyMs: { min: 1200, max: 3500 },
    strengths: ["Open source", "Cost effective", "Strong reasoning", "Reproducible"],
    weaknesses: ["Smaller context window", "Less instruction-tuned"],
    acceptBias: 0.40,
    reasoningDepth: 0.78,
    consistencyScore: 0.91,
    costPer1kTokens: 0.0009,
    avatar: "L3",
    color: "blue",
    description: "Meta's open-source powerhouse. Highly consistent and reproducible — ideal for strict validation. Orion validator uses Llama 3's conservative, evidence-based approach.",
    usedByValidator: "Orion",
  },
  {
    id: "mistral-large",
    name: "Mistral Large",
    provider: "Mistral AI",
    family: "Mistral",
    contextWindow: 32_000,
    outputSpeed: 80,
    latencyMs: { min: 500,  max: 1500 },
    strengths: ["Fast inference", "European compliance", "Multilingual", "Charitable interpretation"],
    weaknesses: ["Less deep reasoning than GPT-4o", "Smaller community"],
    acceptBias: 0.75,
    reasoningDepth: 0.74,
    consistencyScore: 0.80,
    costPer1kTokens: 0.002,
    avatar: "ML",
    color: "pink",
    description: "Mistral AI's large model balances speed and quality. Known for charitable interpretation of ambiguous claims. Lyra validator uses Mistral's lenient, benefit-of-the-doubt approach.",
    usedByValidator: "Lyra",
  },
  {
    id: "gemini-1.5-pro",
    name: "Gemini 1.5 Pro",
    provider: "Google",
    family: "Gemini 1.5",
    contextWindow: 1_000_000,
    outputSpeed: 68,
    latencyMs: { min: 700,  max: 2000 },
    strengths: ["Massive context window", "Multimodal", "Strong factual grounding", "Balanced"],
    weaknesses: ["Can be inconsistent", "Variable response length"],
    acceptBias: 0.58,
    reasoningDepth: 0.82,
    consistencyScore: 0.79,
    costPer1kTokens: 0.0035,
    avatar: "GP",
    color: "violet",
    description: "Google's most capable model with a 1M token context window. Zephyr validator uses Gemini's balanced, proportional evidence-weighing approach for pragmatic consensus.",
    usedByValidator: "Zephyr",
  },
];

export const MODEL_COLORS: Record<string, { bg: string; text: string; border: string; badge: string }> = {
  emerald: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", badge: "bg-emerald-100" },
  orange:  { bg: "bg-orange-50",  text: "text-orange-700",  border: "border-orange-200",  badge: "bg-orange-100"  },
  blue:    { bg: "bg-blue-50",    text: "text-blue-700",    border: "border-blue-200",     badge: "bg-blue-100"   },
  pink:    { bg: "bg-pink-50",    text: "text-pink-700",    border: "border-pink-200",     badge: "bg-pink-100"   },
  violet:  { bg: "bg-violet-50",  text: "text-violet-700",  border: "border-violet-200",   badge: "bg-violet-100" },
};
''')

# ─────────────────────────────────────────────────────────────────────────────
# 2. LLM response simulator
# ─────────────────────────────────────────────────────────────────────────────
w("lib/llm/simulator.ts", '''\
import { sleep } from "@/lib/utils";
import type { LLMModel } from "./models";

export interface LLMResponse {
  modelId: string;
  vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  confidence: number;
  reasoning: string;
  latencyMs: number;
  tokensUsed: number;
  costUsd: number;
}

const RESPONSE_TEMPLATES: Record<string, (claim: string, vote: string) => string> = {
  "gpt-4o": (claim, vote) => {
    if (vote === "ACCEPT")
      return `Analysing the claim: "${claim.slice(0, 70)}…"\n\nKey evaluation points:\n1. The claim is specific and verifiable\n2. No logical inconsistencies detected\n3. Aligns with standard industry expectations\n\nVerdict: The claim satisfies the required criteria for acceptance.`;
    if (vote === "REJECT")
      return `Evaluating: "${claim.slice(0, 70)}…"\n\nIssues identified:\n1. Insufficient verifiable detail\n2. Ambiguous success criteria\n3. Claim cannot be independently corroborated\n\nVerdict: Rejection recommended pending additional evidence.`;
    return `Assessing: "${claim.slice(0, 70)}…"\n\nMixed signals detected:\n• Some criteria are satisfied\n• Others remain ambiguous or unverified\n\nVerdict: Insufficient certainty to render a definitive verdict.`;
  },
  "claude-3-5-sonnet": (claim, vote) => {
    if (vote === "ACCEPT")
      return `I've carefully considered "${claim.slice(0, 70)}…" in its full context.\n\nThe intent behind this claim appears genuine. The language used is consistent with authentic performance and the stated outcomes are plausible given the circumstances described. I find the claim credible.\n\n**Assessment:** ACCEPT — the claim meets the reasonable standard of verification.`;
    if (vote === "REJECT")
      return `After thoughtful consideration of "${claim.slice(0, 70)}…", I have concerns.\n\nWhile I want to give the benefit of the doubt, several elements of this claim raise questions that can't be resolved through charitable interpretation alone. The gap between stated and verifiable outcomes is too significant.\n\n**Assessment:** REJECT — the claim falls short of the required evidential standard.`;
    return `"${claim.slice(0, 70)}…" presents a genuinely difficult case.\n\nI can construct reasonable arguments for both acceptance and rejection. The claim sits precisely at the intersection of plausible and unverifiable. Without additional context, I cannot in good conscience commit to either outcome.\n\n**Assessment:** UNCERTAIN — further evidence is needed.`;
  },
  "llama-3-70b": (claim, vote) => {
    if (vote === "ACCEPT")
      return `CLAIM: "${claim.slice(0, 70)}…"\nRESULT: ACCEPT\n\nRATIONALE: After strict verification against defined criteria, this claim meets the required evidentiary threshold. All verifiable components pass scrutiny. No contradictory evidence found.`;
    if (vote === "REJECT")
      return `CLAIM: "${claim.slice(0, 70)}…"\nRESULT: REJECT\n\nRATIONALE: Strict evaluation reveals the claim does not meet the required standard of evidence. Critical verification criteria are not satisfied. The claim lacks the specificity and corroboration required for acceptance.`;
    return `CLAIM: "${claim.slice(0, 70)}…"\nRESULT: UNCERTAIN\n\nRATIONALE: The claim sits at the boundary of the acceptance threshold. Strict criteria cannot be definitively satisfied or rejected based on available information.`;
  },
  "mistral-large": (claim, vote) => {
    if (vote === "ACCEPT")
      return `Looking at "${claim.slice(0, 70)}…" — this is plausible and the description is consistent with a legitimate outcome. I'm giving the benefit of the doubt here. The claim is reasonable and I see no red flags that would warrant rejection. Accept.`;
    if (vote === "REJECT")
      return `Even being charitable, "${claim.slice(0, 70)}…" has too many unresolved questions. The core premise doesn't hold up on closer inspection. Despite my inclination toward leniency, I can't in good faith accept a claim with these inconsistencies. Reject.`;
    return `"${claim.slice(0, 70)}…" — I want to accept this, but something's not quite right. The claim is borderline. I'll flag as uncertain rather than force a verdict in either direction.`;
  },
  "gemini-1.5-pro": (claim, vote) => {
    if (vote === "ACCEPT")
      return `Balanced assessment of "${claim.slice(0, 70)}…":\n\n**Pro-acceptance factors:** Specific claim, reasonable scope, language consistent with genuine performance.\n**Counter-considerations:** Minor ambiguities present but not disqualifying.\n\n**Weighted conclusion:** The evidence balance tips toward acceptance (confidence: proportional to available data).`;
    if (vote === "REJECT")
      return `Balanced assessment of "${claim.slice(0, 70)}…":\n\n**Pro-acceptance factors:** Some elements plausible.\n**Counter-considerations:** Key verification criteria unmet; ambiguity exceeds acceptable threshold; evidence weight is insufficient.\n\n**Weighted conclusion:** Rejection is proportionally supported by the evidence.`;
    return `Balanced assessment of "${claim.slice(0, 70)}…":\n\n**Evidence for:** Some plausible elements.\n**Evidence against:** Some problematic elements.\n**Uncertainty factor:** High — the evidence is approximately equal on both sides.\n\n**Weighted conclusion:** Uncertain verdict; proportional to the genuine ambiguity in the claim.`;
  },
};

function generateVote(model: LLMModel, claim: string): { vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number } {
  const hash = Array.from(claim + model.id).reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = ((hash * 7919 + 104729) % 999983) / 999983;

  const bias    = model.acceptBias;
  const margin  = 0.15;

  let vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  let confidence: number;

  if (rand > bias + margin / 2) {
    vote = "ACCEPT";
    confidence = model.consistencyScore * 0.85 + (rand - bias) * 0.2;
  } else if (rand < bias - margin / 2) {
    vote = "REJECT";
    confidence = model.consistencyScore * 0.85 + (bias - rand) * 0.2;
  } else {
    vote = "UNCERTAIN";
    confidence = model.consistencyScore * 0.60;
  }

  return { vote, confidence: Math.min(0.98, Math.max(0.51, confidence)) };
}

export async function simulateLLMResponse(
  model: LLMModel,
  claim: string,
  onStart: () => void
): Promise<LLMResponse> {
  onStart();

  // Simulate latency
  const latencyMs = model.latencyMs.min + Math.random() * (model.latencyMs.max - model.latencyMs.min);
  await sleep(Math.round(latencyMs));

  const { vote, confidence } = generateVote(model, claim);
  const template = RESPONSE_TEMPLATES[model.id] ?? RESPONSE_TEMPLATES["gpt-4o"];
  const reasoning = template(claim, vote);

  const tokensUsed = Math.floor(150 + Math.random() * 300);
  const costUsd    = (tokensUsed / 1000) * model.costPer1kTokens;

  return {
    modelId: model.id,
    vote,
    confidence,
    reasoning,
    latencyMs: Math.round(latencyMs),
    tokensUsed,
    costUsd,
  };
}

export async function runLLMComparison(
  models: LLMModel[],
  claim: string,
  onUpdate: (responses: Partial<Record<string, LLMResponse>>, loadingIds: string[]) => void
): Promise<Record<string, LLMResponse>> {
  const responses: Partial<Record<string, LLMResponse>> = {};
  let loadingIds = [...models.map((m) => m.id)];
  onUpdate({ ...responses }, [...loadingIds]);

  // Run all models in parallel
  await Promise.all(
    models.map(async (model) => {
      const resp = await simulateLLMResponse(model, claim, () => {});
      responses[model.id] = resp;
      loadingIds = loadingIds.filter((id) => id !== model.id);
      onUpdate({ ...responses }, [...loadingIds]);
    })
  );

  return responses as Record<string, LLMResponse>;
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 3. LLM Comparison store
# ─────────────────────────────────────────────────────────────────────────────
w("store/llmCompareStore.ts", '''\
import { create } from "zustand";
import type { LLMResponse } from "@/lib/llm/simulator";

export interface ComparisonRun {
  id: string;
  claim: string;
  responses: Record<string, LLMResponse>;
  startedAt: number;
  completedAt: number | null;
}

interface LLMCompareStore {
  currentRun: ComparisonRun | null;
  history: ComparisonRun[];
  loadingModelIds: string[];
  selectedModelId: string | null;

  startRun: (claim: string) => string;
  updateResponses: (runId: string, responses: Partial<Record<string, LLMResponse>>, loadingIds: string[]) => void;
  finalizeRun: (runId: string, responses: Record<string, LLMResponse>) => void;
  selectModel: (id: string | null) => void;
  clearHistory: () => void;
}

export const useLLMCompareStore = create<LLMCompareStore>((set) => ({
  currentRun: null,
  history: [],
  loadingModelIds: [],
  selectedModelId: null,

  startRun: (claim) => {
    const id = `cmp_${Date.now()}`;
    const run: ComparisonRun = { id, claim, responses: {}, startedAt: Date.now(), completedAt: null };
    set({ currentRun: run, loadingModelIds: [], selectedModelId: null });
    return id;
  },

  updateResponses: (runId, responses, loadingIds) =>
    set((s) => {
      if (s.currentRun?.id !== runId) return s;
      return {
        currentRun: { ...s.currentRun, responses: { ...s.currentRun.responses, ...responses } },
        loadingModelIds: loadingIds,
      };
    }),

  finalizeRun: (runId, responses) =>
    set((s) => {
      if (s.currentRun?.id !== runId) return s;
      const finalized = { ...s.currentRun, responses, completedAt: Date.now() };
      return {
        currentRun: finalized,
        loadingModelIds: [],
        history: [finalized, ...s.history].slice(0, 10),
      };
    }),

  selectModel: (id) => set({ selectedModelId: id }),
  clearHistory: () => set({ history: [] }),
}));
''')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Model Card (full profile)
# ─────────────────────────────────────────────────────────────────────────────
w("components/llm/ModelCard.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { Zap, Brain, RefreshCw, DollarSign, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { MODEL_COLORS, type LLMModel } from "@/lib/llm/models";

interface ModelCardProps {
  model: LLMModel;
  isSelected: boolean;
  onClick: () => void;
  index: number;
}

export function ModelCard({ model, isSelected, onClick, index }: ModelCardProps) {
  const colors = MODEL_COLORS[model.color] ?? MODEL_COLORS.emerald;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      onClick={onClick}
      className={cn(
        "rounded-xl border-2 p-5 cursor-pointer transition-all duration-200",
        isSelected ? "border-[#2d2a26] bg-white/80 shadow-md" : "border-[#d8d4c8] bg-white/50 hover:border-[#b8b4a8]"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn("h-11 w-11 rounded-xl flex items-center justify-center text-sm font-bold shrink-0", colors.bg, colors.text)}>
            {model.avatar}
          </div>
          <div>
            <h3 className="text-sm font-bold text-[#1a1a1a]">{model.name}</h3>
            <p className="text-xs text-[#6b6560]">{model.provider}</p>
          </div>
        </div>
        <Badge variant="secondary" className="text-[10px]">{model.usedByValidator}</Badge>
      </div>

      <p className="text-xs text-[#6b6560] leading-relaxed mb-4 line-clamp-3">{model.description}</p>

      {/* Metrics */}
      <div className="space-y-2.5 mb-4">
        {[
          { icon: Brain,      label: "Reasoning Depth",  value: model.reasoningDepth,     color: "bg-indigo-500" },
          { icon: RefreshCw,  label: "Consistency",      value: model.consistencyScore,   color: "bg-green-500" },
          { icon: Zap,        label: "Accept Bias",      value: model.acceptBias,         color: "bg-amber-500" },
        ].map(({ icon: Icon, label, value, color }) => (
          <div key={label}>
            <div className="flex items-center justify-between text-[11px] text-[#6b6560] mb-1">
              <span className="flex items-center gap-1"><Icon className="h-2.5 w-2.5" />{label}</span>
              <span className="font-medium text-[#1a1a1a]">{Math.round(value * 100)}%</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-[#e8e4da] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value * 100}%` }}
                transition={{ duration: 0.7, ease: "easeOut", delay: index * 0.07 + 0.3 }}
                className={cn("h-full rounded-full", color)}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Specs */}
      <div className="grid grid-cols-2 gap-2 text-[10px] text-[#6b6560] border-t border-[#e8e4da] pt-3">
        <span>Context: <strong className="text-[#1a1a1a]">{(model.contextWindow / 1000).toFixed(0)}K</strong></span>
        <span className="flex items-center gap-0.5">
          <DollarSign className="h-2.5 w-2.5" />
          <strong className="text-[#1a1a1a]">${model.costPer1kTokens}</strong>/1K
        </span>
        <span>Speed: <strong className="text-[#1a1a1a]">{model.outputSpeed} t/s</strong></span>
        <span>Latency: <strong className="text-[#1a1a1a]">{model.latencyMs.min}–{model.latencyMs.max}ms</strong></span>
      </div>

      {/* Strengths */}
      <div className="mt-3 flex flex-wrap gap-1">
        {model.strengths.slice(0, 3).map((s) => (
          <span key={s} className={cn("text-[9px] px-1.5 py-0.5 rounded-full font-medium", colors.badge, colors.text)}>
            {s}
          </span>
        ))}
      </div>
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 5. Response Card (model output panel)
# ─────────────────────────────────────────────────────────────────────────────
w("components/llm/ResponseCard.tsx", '''\
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Clock, Hash, DollarSign, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { MODEL_COLORS, LLM_MODELS } from "@/lib/llm/models";
import type { LLMResponse } from "@/lib/llm/simulator";

interface ResponseCardProps {
  modelId: string;
  response: LLMResponse | undefined;
  isLoading: boolean;
  index: number;
  isWinner?: boolean;
}

const VOTE_CFG = {
  ACCEPT:    { icon: CheckCircle2, variant: "accept"    as const, bg: "bg-green-50",  border: "border-green-200" },
  REJECT:    { icon: XCircle,      variant: "reject"    as const, bg: "bg-red-50",    border: "border-red-200" },
  UNCERTAIN: { icon: HelpCircle,   variant: "uncertain" as const, bg: "bg-amber-50",  border: "border-amber-200" },
};

export function ResponseCard({ modelId, response, isLoading, index, isWinner }: ResponseCardProps) {
  const model  = LLM_MODELS.find((m) => m.id === modelId);
  if (!model) return null;

  const colors  = MODEL_COLORS[model.color] ?? MODEL_COLORS.emerald;
  const voteCfg = response ? VOTE_CFG[response.vote] : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className={cn(
        "rounded-xl border-2 flex flex-col transition-all",
        isLoading && "border-[#d8d4c8]",
        response && voteCfg?.border,
        response && voteCfg?.bg,
        !response && !isLoading && "border-[#e8e4da] bg-white/30",
        isWinner && "ring-2 ring-offset-2 ring-[#2d2a26]"
      )}
    >
      {/* Model header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#e8e4da]/60">
        <div className="flex items-center gap-2">
          <div className={cn("h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold", colors.bg, colors.text)}>
            {model.avatar}
          </div>
          <div>
            <p className="text-xs font-semibold text-[#1a1a1a] leading-tight">{model.name}</p>
            <p className="text-[10px] text-[#6b6560]">{model.provider} · {model.usedByValidator}</p>
          </div>
        </div>
        {isWinner && (
          <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-[#2d2a26] text-[#efece4]">Fastest</span>
        )}
      </div>

      {/* Body */}
      <div className="flex-1 p-4">
        {/* Loading */}
        {isLoading && !response && (
          <div className="flex flex-col items-center justify-center py-8 gap-3">
            <Loader2 className="h-5 w-5 text-[#6b6560] animate-spin" />
            <p className="text-xs text-[#6b6560]">Querying {model.name}…</p>
            <div className="w-full">
              <Progress value={undefined} className="h-1" />
            </div>
          </div>
        )}

        {/* Response */}
        <AnimatePresence>
          {response && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
              className="space-y-3"
            >
              {/* Vote badge + confidence */}
              <div className="flex items-center justify-between">
                {voteCfg && (
                  <Badge variant={voteCfg.variant} className="text-xs">
                    <voteCfg.icon className="h-3 w-3 mr-1" /> {response.vote}
                  </Badge>
                )}
                <span className="text-xs font-semibold text-[#1a1a1a] tabular-nums">
                  {Math.round(response.confidence * 100)}% conf.
                </span>
              </div>

              <Progress value={Math.round(response.confidence * 100)} className="h-1.5" />

              {/* Reasoning */}
              <div className="rounded-lg bg-white/60 p-3 border border-[#e8e4da]">
                <p className="text-[11px] text-[#1a1a1a] leading-relaxed whitespace-pre-line line-clamp-8">
                  {response.reasoning}
                </p>
              </div>

              {/* Metrics */}
              <div className="flex flex-wrap gap-3 text-[10px] text-[#6b6560] pt-1 border-t border-[#e8e4da]">
                <span className="flex items-center gap-1">
                  <Clock className="h-2.5 w-2.5" />{response.latencyMs}ms
                </span>
                <span className="flex items-center gap-1">
                  <Hash className="h-2.5 w-2.5" />{response.tokensUsed} tokens
                </span>
                <span className="flex items-center gap-1">
                  <DollarSign className="h-2.5 w-2.5" />${response.costUsd.toFixed(5)}
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {!response && !isLoading && (
          <p className="text-xs text-[#6b6560] text-center py-8 italic">Waiting for comparison run…</p>
        )}
      </div>
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Scoring Matrix
# ─────────────────────────────────────────────────────────────────────────────
w("components/llm/ScoringMatrix.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Clock, DollarSign, Hash, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { LLM_MODELS, MODEL_COLORS } from "@/lib/llm/models";
import type { LLMResponse } from "@/lib/llm/simulator";

interface ScoringMatrixProps {
  responses: Record<string, LLMResponse>;
}

const VOTE_ICONS = {
  ACCEPT:    { icon: CheckCircle2, cls: "text-green-600" },
  REJECT:    { icon: XCircle,      cls: "text-red-600" },
  UNCERTAIN: { icon: HelpCircle,   cls: "text-amber-600" },
};

export function ScoringMatrix({ responses }: ScoringMatrixProps) {
  const models = LLM_MODELS.filter((m) => responses[m.id]);
  if (models.length === 0) return null;

  const fastestId  = models.reduce((a, b) => responses[a.id].latencyMs < responses[b.id].latencyMs ? a : b).id;
  const cheapestId = models.reduce((a, b) => responses[a.id].costUsd    < responses[b.id].costUsd    ? a : b).id;
  const mostConfId = models.reduce((a, b) => responses[a.id].confidence > responses[b.id].confidence ? a : b).id;

  const maxLatency = Math.max(...models.map((m) => responses[m.id].latencyMs));
  const maxCost    = Math.max(...models.map((m) => responses[m.id].costUsd));

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 overflow-hidden">
      <div className="px-5 py-3 border-b border-[#e8e4da] flex items-center justify-between">
        <p className="text-sm font-semibold text-[#1a1a1a]">Scoring Matrix</p>
        <p className="text-xs text-[#6b6560]">{models.length} models compared</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-[#f5f2ec]">
              <th className="px-4 py-2.5 text-left font-semibold text-[#6b6560] w-36">Model</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Vote</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Confidence</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Latency</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Cost</th>
              <th className="px-4 py-2.5 text-center font-semibold text-[#6b6560]">Tokens</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model, i) => {
              const r      = responses[model.id];
              const colors = MODEL_COLORS[model.color] ?? MODEL_COLORS.emerald;
              const voteCfg = VOTE_ICONS[r.vote];
              const Icon   = voteCfg.icon;

              return (
                <motion.tr
                  key={model.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className={cn("border-t border-[#e8e4da]", i % 2 === 0 ? "bg-white/30" : "bg-[#f5f2ec]/30")}
                >
                  {/* Model */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className={cn("h-6 w-6 rounded flex items-center justify-center text-[9px] font-bold shrink-0", colors.bg, colors.text)}>
                        {model.avatar}
                      </div>
                      <div>
                        <p className="font-semibold text-[#1a1a1a] leading-tight">{model.name}</p>
                        <p className="text-[9px] text-[#6b6560]">{model.provider}</p>
                      </div>
                    </div>
                  </td>

                  {/* Vote */}
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-1">
                      <Icon className={cn("h-3.5 w-3.5", voteCfg.cls)} />
                      <span className={cn("font-semibold", voteCfg.cls)}>{r.vote}</span>
                    </div>
                  </td>

                  {/* Confidence */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Progress value={Math.round(r.confidence * 100)} className="h-1.5 w-16" />
                      <span className={cn("font-semibold tabular-nums", model.id === mostConfId && "text-indigo-600")}>
                        {Math.round(r.confidence * 100)}%
                        {model.id === mostConfId && <span className="text-[8px] ml-0.5">★</span>}
                      </span>
                    </div>
                  </td>

                  {/* Latency */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-1.5 rounded-full bg-[#e8e4da] overflow-hidden">
                        <div className="h-full rounded-full bg-blue-400" style={{ width: `${(r.latencyMs / maxLatency) * 100}%` }} />
                      </div>
                      <span className={cn("tabular-nums", model.id === fastestId && "text-green-600 font-semibold")}>
                        {r.latencyMs}ms
                        {model.id === fastestId && <span className="text-[8px] ml-0.5">⚡</span>}
                      </span>
                    </div>
                  </td>

                  {/* Cost */}
                  <td className="px-4 py-3">
                    <span className={cn("tabular-nums", model.id === cheapestId && "text-green-600 font-semibold")}>
                      ${r.costUsd.toFixed(5)}
                      {model.id === cheapestId && <span className="text-[8px] ml-0.5">💰</span>}
                    </span>
                  </td>

                  {/* Tokens */}
                  <td className="px-4 py-3 text-center text-[#6b6560] tabular-nums">{r.tokensUsed}</td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="px-5 py-3 border-t border-[#e8e4da] flex flex-wrap gap-4 text-[10px] text-[#6b6560] bg-[#f5f2ec]/50">
        <span>⚡ Fastest response</span>
        <span>💰 Lowest cost</span>
        <span>★ Highest confidence</span>
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Agreement Heatmap
# ─────────────────────────────────────────────────────────────────────────────
w("components/llm/AgreementHeatmap.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { LLM_MODELS, MODEL_COLORS } from "@/lib/llm/models";
import type { LLMResponse } from "@/lib/llm/simulator";

interface AgreementHeatmapProps {
  responses: Record<string, LLMResponse>;
}

function agreementColor(a: string, b: string): string {
  if (a === b) return "bg-green-200 text-green-800";
  if (a === "UNCERTAIN" || b === "UNCERTAIN") return "bg-amber-100 text-amber-700";
  return "bg-red-100 text-red-700";
}

function agreementLabel(a: string, b: string): string {
  if (a === b) return "Agree";
  if (a === "UNCERTAIN" || b === "UNCERTAIN") return "Partial";
  return "Disagree";
}

export function AgreementHeatmap({ responses }: AgreementHeatmapProps) {
  const models = LLM_MODELS.filter((m) => responses[m.id]);
  if (models.length < 2) return null;

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5">
      <p className="text-sm font-semibold text-[#1a1a1a] mb-1">Agreement Heatmap</p>
      <p className="text-xs text-[#6b6560] mb-4">How each model pair compares on this claim.</p>

      <div className="overflow-x-auto">
        <table className="text-[10px]">
          <thead>
            <tr>
              <th className="w-24" />
              {models.map((m) => {
                const colors = MODEL_COLORS[m.color] ?? MODEL_COLORS.emerald;
                return (
                  <th key={m.id} className="px-2 py-1 text-center">
                    <div className={cn("h-6 w-6 rounded flex items-center justify-center font-bold mx-auto", colors.bg, colors.text)}>
                      {m.avatar}
                    </div>
                    <p className="mt-1 font-normal text-[#6b6560]">{m.name.split(" ")[0]}</p>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {models.map((rowModel, ri) => {
              const colors = MODEL_COLORS[rowModel.color] ?? MODEL_COLORS.emerald;
              return (
                <tr key={rowModel.id}>
                  <td className="pr-3 py-1">
                    <div className="flex items-center gap-1.5">
                      <div className={cn("h-5 w-5 rounded flex items-center justify-center font-bold text-[9px]", colors.bg, colors.text)}>
                        {rowModel.avatar}
                      </div>
                      <span className="font-medium text-[#1a1a1a]">{rowModel.name.split(" ")[0]}</span>
                    </div>
                  </td>
                  {models.map((colModel, ci) => {
                    const a = responses[rowModel.id].vote;
                    const b = responses[colModel.id].vote;
                    const isDiag = ri === ci;
                    return (
                      <td key={colModel.id} className="px-2 py-1 text-center">
                        <motion.div
                          initial={{ scale: 0.6, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: (ri + ci) * 0.04 }}
                          className={cn(
                            "rounded-md px-2 py-1 font-semibold",
                            isDiag ? "bg-[#2d2a26] text-[#efece4]" : agreementColor(a, b)
                          )}
                        >
                          {isDiag ? a.slice(0, 3) : agreementLabel(a, b)}
                        </motion.div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Agreement summary */}
      {(() => {
        const pairs: [string, string][] = [];
        for (let i = 0; i < models.length; i++)
          for (let j = i + 1; j < models.length; j++)
            pairs.push([models[i].id, models[j].id]);
        const agreed = pairs.filter(([a, b]) => responses[a].vote === responses[b].vote).length;
        const pct    = Math.round((agreed / pairs.length) * 100);
        return (
          <p className="mt-4 text-xs text-[#6b6560] border-t border-[#e8e4da] pt-3">
            <strong className="text-[#1a1a1a]">{agreed}/{pairs.length}</strong> model pairs ({pct}%) reached the same verdict on this claim.
            {pct >= 80 ? " Strong cross-model consensus." : pct >= 60 ? " Moderate agreement." : " High disagreement — this is a genuinely subjective claim."}
          </p>
        );
      })()}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 8. Comparison Form
# ─────────────────────────────────────────────────────────────────────────────
w("components/llm/ComparisonForm.tsx", '''\
"use client";

import { useState } from "react";
import { Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

const PRESETS = [
  "The software contractor delivered a production-ready API with comprehensive test coverage and documentation by the agreed deadline.",
  "This product review is genuine — the reviewer bought and used the product for 30 days before writing their opinion.",
  "The charity event successfully raised funds and all proceeds were transferred to the intended beneficiaries within the stated timeframe.",
  "The AI-generated article is factually accurate, well-sourced, and free from misleading claims.",
];

interface ComparisonFormProps {
  onRun: (claim: string) => void;
  disabled?: boolean;
}

export function ComparisonForm({ onRun, disabled }: ComparisonFormProps) {
  const [claim, setClaim] = useState("");

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5 space-y-4">
      <div>
        <p className="text-sm font-semibold text-[#1a1a1a] mb-1">Submit a Claim for Comparison</p>
        <p className="text-xs text-[#6b6560] leading-relaxed">
          All five validator LLMs will independently evaluate the claim simultaneously.
          Compare their votes, reasoning styles, confidence levels, latency and cost.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {PRESETS.map((p, i) => (
          <button key={i} onClick={() => setClaim(p)} disabled={disabled}
            className="text-[11px] border border-[#d8d4c8] rounded-full px-3 py-1 bg-white/50 hover:bg-white transition-all text-[#6b6560] hover:text-[#1a1a1a] disabled:opacity-40">
            Preset {i + 1}
          </button>
        ))}
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs">Claim</Label>
        <Textarea value={claim} onChange={(e) => setClaim(e.target.value)} disabled={disabled}
          placeholder="Enter a subjective claim to evaluate across all LLMs…"
          className="min-h-[90px] text-sm" />
      </div>

      <Button className="w-full" onClick={() => onRun(claim.trim())} disabled={disabled || !claim.trim()}>
        <Play className="h-4 w-4 mr-2" /> Run Comparison Across All Models
      </Button>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 9. LLM Comparison Center Page
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/llm-compare/page.tsx", '''\
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
                        isWinner={allDone && model.id === fastestId}
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
''')

print("\nPhase 8 setup complete. All files written.\n")
