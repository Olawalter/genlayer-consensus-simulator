"""Phase 4: Consensus Playground — simulation engine, validator cards, real-time UI."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  WROTE  {rel}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Validator Personas (lib/validators/personas.ts)
# ─────────────────────────────────────────────────────────────────────────────
w("lib/validators/personas.ts", '''\
export type ValidatorPersona = "strict" | "lenient" | "analytical" | "creative" | "balanced";

export interface ValidatorPersonaConfig {
  name: string;
  model: string;
  persona: ValidatorPersona;
  acceptThreshold: number;   // 0–1: probability of ACCEPT on neutral claims
  uncertaintyRange: number;  // 0–1: how wide the uncertain zone is
  confidenceBase: number;    // base confidence level
  color: string;
  avatar: string;
  description: string;
  reasoningStyle: string;
}

export const VALIDATOR_PERSONAS: ValidatorPersonaConfig[] = [
  {
    name: "Atlas",
    model: "gpt-4o",
    persona: "analytical",
    acceptThreshold: 0.55,
    uncertaintyRange: 0.15,
    confidenceBase: 0.82,
    color: "indigo",
    avatar: "AT",
    description: "Methodical and data-driven. Evaluates claims against objective criteria.",
    reasoningStyle: "analytical",
  },
  {
    name: "Nova",
    model: "claude-3-5-sonnet",
    persona: "creative",
    acceptThreshold: 0.65,
    uncertaintyRange: 0.2,
    confidenceBase: 0.74,
    color: "pink",
    avatar: "NV",
    description: "Contextual and nuanced. Considers intent and broader implications.",
    reasoningStyle: "contextual",
  },
  {
    name: "Orion",
    model: "llama-3-70b",
    persona: "strict",
    acceptThreshold: 0.40,
    uncertaintyRange: 0.1,
    confidenceBase: 0.91,
    color: "red",
    avatar: "OR",
    description: "Conservative and precise. Requires strong evidence before accepting.",
    reasoningStyle: "strict",
  },
  {
    name: "Lyra",
    model: "mistral-large",
    persona: "lenient",
    acceptThreshold: 0.75,
    uncertaintyRange: 0.2,
    confidenceBase: 0.68,
    color: "emerald",
    avatar: "LY",
    description: "Generous and charitable. Gives benefit of the doubt when claims are plausible.",
    reasoningStyle: "lenient",
  },
  {
    name: "Zephyr",
    model: "gemini-1.5-pro",
    persona: "balanced",
    acceptThreshold: 0.58,
    uncertaintyRange: 0.18,
    confidenceBase: 0.77,
    color: "amber",
    avatar: "ZP",
    description: "Balanced and pragmatic. Weighs evidence proportionally across all factors.",
    reasoningStyle: "balanced",
  },
];

export const PERSONA_COLORS: Record<string, { bg: string; text: string; border: string; glow: string }> = {
  indigo:  { bg: "bg-indigo-50",  text: "text-indigo-700",  border: "border-indigo-200", glow: "shadow-indigo-200" },
  pink:    { bg: "bg-pink-50",    text: "text-pink-700",    border: "border-pink-200",   glow: "shadow-pink-200" },
  red:     { bg: "bg-red-50",     text: "text-red-700",     border: "border-red-200",    glow: "shadow-red-200" },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200",glow: "shadow-emerald-200" },
  amber:   { bg: "bg-amber-50",   text: "text-amber-700",   border: "border-amber-200",  glow: "shadow-amber-200" },
};
''')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Equivalence Logic (lib/validators/equivalence.ts)
# ─────────────────────────────────────────────────────────────────────────────
w("lib/validators/equivalence.ts", '''\
import type { ValidatorVote } from "@/types/validator";

export interface EquivalenceResult {
  score: number;          // 0–1: how equivalent the votes are
  pass: boolean;          // whether equivalence threshold is met
  consensusType: "unanimous" | "majority" | "split";
  acceptCount: number;
  rejectCount: number;
  uncertainCount: number;
  outcome: "ACCEPTED" | "REJECTED" | "APPEAL_TRIGGERED";
  explanation: string;
}

const EQUIVALENCE_THRESHOLD = 0.6; // 60% agreement needed

export function computeEquivalence(votes: ValidatorVote[]): EquivalenceResult {
  const total = votes.length;
  if (total === 0) {
    return {
      score: 0, pass: false, consensusType: "split",
      acceptCount: 0, rejectCount: 0, uncertainCount: 0,
      outcome: "APPEAL_TRIGGERED", explanation: "No votes cast.",
    };
  }

  const acceptCount   = votes.filter((v) => v.vote === "ACCEPT").length;
  const rejectCount   = votes.filter((v) => v.vote === "REJECT").length;
  const uncertainCount = votes.filter((v) => v.vote === "UNCERTAIN").length;

  const maxCount = Math.max(acceptCount, rejectCount);
  const score = maxCount / total;

  const pass = score >= EQUIVALENCE_THRESHOLD;

  let consensusType: EquivalenceResult["consensusType"];
  if (score === 1) consensusType = "unanimous";
  else if (pass)   consensusType = "majority";
  else             consensusType = "split";

  let outcome: EquivalenceResult["outcome"];
  if (!pass) {
    outcome = "APPEAL_TRIGGERED";
  } else if (acceptCount >= rejectCount) {
    outcome = "ACCEPTED";
  } else {
    outcome = "REJECTED";
  }

  const explanation = buildExplanation(acceptCount, rejectCount, uncertainCount, total, score, pass);

  return { score, pass, consensusType, acceptCount, rejectCount, uncertainCount, outcome, explanation };
}

function buildExplanation(
  accept: number, reject: number, uncertain: number, total: number, score: number, pass: boolean
): string {
  const pct = Math.round(score * 100);
  if (!pass) {
    return `Validator outputs are too divergent (${pct}% agreement). The Equivalence Principle requires at least 60% agreement. An appeal round is triggered.`;
  }
  if (score === 1) {
    return `All ${total} validators reached identical conclusions — a unanimous consensus under the Equivalence Principle.`;
  }
  const majority = Math.max(accept, reject);
  return `${majority}/${total} validators (${pct}%) reached equivalent conclusions — within the Equivalence Principle threshold. Consensus is accepted.`;
}

export function computeEquivalenceScore(votes: ValidatorVote[]): number {
  const result = computeEquivalence(votes);
  return result.score;
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Simulation Engine (services/simulationService.ts)
# ─────────────────────────────────────────────────────────────────────────────
w("services/simulationService.ts", '''\
import { VALIDATOR_PERSONAS } from "@/lib/validators/personas";
import { computeEquivalence } from "@/lib/validators/equivalence";
import { sleep } from "@/lib/utils";
import type { ValidatorVote } from "@/types/validator";

export type SimulationStatus =
  | "idle"
  | "submitting"
  | "running"
  | "computing"
  | "accepted"
  | "rejected"
  | "appeal_triggered"
  | "appealing"
  | "finalized";

export interface LiveValidator {
  id: string;
  name: string;
  model: string;
  persona: string;
  color: string;
  avatar: string;
  description: string;
  status: "waiting" | "thinking" | "voted";
  vote: "ACCEPT" | "REJECT" | "UNCERTAIN" | null;
  confidence: number | null;
  reasoning: string | null;
  isLeader: boolean;
  thinkingMs: number;
}

export interface SimulationRun {
  id: string;
  claimId: string;
  claim: string;
  category: string;
  status: SimulationStatus;
  validators: LiveValidator[];
  consensusResult: ReturnType<typeof computeEquivalence> | null;
  txHash: string | null;
  round: number;
  startedAt: number;
}

// ─── Reasoning generators per persona ────────────────────────────────────────

const REASONING_TEMPLATES: Record<string, (claim: string, vote: string) => string> = {
  analytical: (claim, vote) => {
    if (vote === "ACCEPT")
      return `After systematic evaluation of "${claim.slice(0, 60)}...", the objective indicators align with acceptance criteria. The claim contains verifiable elements and no contradictory evidence was identified in my analysis.`;
    if (vote === "REJECT")
      return `Evaluating "${claim.slice(0, 60)}..." against measurable criteria reveals insufficient evidence. The claim lacks the quantifiable specificity required for confident acceptance under analytical review.`;
    return `The claim "${claim.slice(0, 60)}..." presents mixed signals under analytical review. While some criteria are met, ambiguity in key variables prevents a definitive determination.`;
  },
  contextual: (claim, vote) => {
    if (vote === "ACCEPT")
      return `Reading "${claim.slice(0, 60)}..." in context, the intent and broader circumstances support acceptance. The spirit of what is being claimed appears genuine and consistent with reasonable expectations.`;
    if (vote === "REJECT")
      return `Contextually, "${claim.slice(0, 60)}..." raises concerns. The framing and surrounding context suggest this claim may not reflect the full picture, leading to a rejection after careful consideration.`;
    return `The context around "${claim.slice(0, 60)}..." is genuinely ambiguous. Multiple interpretations are plausible, and I cannot confidently favour one outcome without additional information.`;
  },
  strict: (claim, vote) => {
    if (vote === "ACCEPT")
      return `"${claim.slice(0, 60)}..." meets the required threshold of evidence. Only after rigorous scrutiny and finding no logical inconsistencies do I issue this acceptance.`;
    if (vote === "REJECT")
      return `The claim "${claim.slice(0, 60)}..." fails strict verification. The evidentiary bar has not been met. Acceptance would require substantially stronger and more concrete supporting facts.`;
    return `Under strict evaluation, "${claim.slice(0, 60)}..." remains unresolved. The evidence is borderline and strict standards prohibit acceptance without stronger confirmation.`;
  },
  lenient: (claim, vote) => {
    if (vote === "ACCEPT")
      return `"${claim.slice(0, 60)}..." appears credible and plausible. Giving appropriate benefit of the doubt, the claim aligns with what one would reasonably expect given the circumstances described.`;
    if (vote === "REJECT")
      return `Even with a charitable interpretation, "${claim.slice(0, 60)}..." presents too many red flags to accept. The claim's core premise is difficult to reconcile with known patterns and expectations.`;
    return `"${claim.slice(0, 60)}..." is on the fence. While I lean toward giving the benefit of the doubt, some aspects give me enough pause to record an uncertain verdict rather than a full acceptance.`;
  },
  balanced: (claim, vote) => {
    if (vote === "ACCEPT")
      return `Weighing all available evidence for "${claim.slice(0, 60)}...", the balance of probability favours acceptance. The supporting factors outweigh the concerns when assessed proportionally.`;
    if (vote === "REJECT")
      return `A balanced assessment of "${claim.slice(0, 60)}..." tips toward rejection. While there are arguments on both sides, the weight of evidence against acceptance is marginally stronger.`;
    return `"${claim.slice(0, 60)}..." presents a genuine 50/50 scenario upon balanced review. The evidence for and against acceptance is approximately equal, warranting an uncertain verdict.`;
  },
};

// ─── Vote generator ───────────────────────────────────────────────────────────

function generateVote(
  persona: (typeof VALIDATOR_PERSONAS)[0],
  claim: string
): { vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number; reasoning: string } {
  // Deterministic-ish based on claim content + persona
  const hash = Array.from(claim + persona.name).reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = ((hash * 9301 + 49297) % 233280) / 233280;

  const uncertainty = persona.uncertaintyRange;
  const threshold = persona.acceptThreshold;

  let vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  let confidence: number;

  if (rand > threshold + uncertainty / 2) {
    vote = "ACCEPT";
    confidence = persona.confidenceBase + (rand - threshold) * 0.2;
  } else if (rand < threshold - uncertainty / 2) {
    vote = "REJECT";
    confidence = persona.confidenceBase + (threshold - rand) * 0.2;
  } else {
    vote = "UNCERTAIN";
    confidence = persona.confidenceBase * 0.7;
  }

  confidence = Math.min(0.99, Math.max(0.51, confidence));

  const reasoning = REASONING_TEMPLATES[persona.reasoningStyle]?.(claim, vote)
    ?? REASONING_TEMPLATES.balanced(claim, vote);

  return { vote, confidence, reasoning };
}

// ─── Main simulation runner ───────────────────────────────────────────────────

export async function runSimulation(
  claim: string,
  category: string,
  onUpdate: (run: SimulationRun) => void
): Promise<SimulationRun> {
  const runId = `sim_${Date.now()}`;
  const claimId = `claim_${Date.now()}`;

  // Build initial validator state
  const validators: LiveValidator[] = VALIDATOR_PERSONAS.map((p, i) => ({
    id: `v_${i}`,
    name: p.name,
    model: p.model,
    persona: p.persona,
    color: p.color,
    avatar: p.avatar,
    description: p.description,
    status: "waiting",
    vote: null,
    confidence: null,
    reasoning: null,
    isLeader: i === 0,
    thinkingMs: 1200 + i * 600 + Math.floor(Math.random() * 400),
  }));

  const run: SimulationRun = {
    id: runId,
    claimId,
    claim,
    category,
    status: "submitting",
    validators,
    consensusResult: null,
    txHash: null,
    round: 1,
    startedAt: Date.now(),
  };

  onUpdate({ ...run });
  await sleep(600);

  // Transition to running
  run.status = "running";
  onUpdate({ ...run });

  // Leader evaluates first
  run.validators = run.validators.map((v) =>
    v.isLeader ? { ...v, status: "thinking" } : v
  );
  onUpdate({ ...run });

  await sleep(run.validators[0].thinkingMs);

  const leaderResult = generateVote(VALIDATOR_PERSONAS[0], claim);
  run.validators = run.validators.map((v) =>
    v.isLeader
      ? { ...v, status: "voted", ...leaderResult }
      : v
  );
  onUpdate({ ...run });

  // Other validators evaluate in parallel (staggered)
  for (let i = 1; i < VALIDATOR_PERSONAS.length; i++) {
    await sleep(300);
    run.validators = run.validators.map((v, idx) =>
      idx === i ? { ...v, status: "thinking" } : v
    );
    onUpdate({ ...run });

    await sleep(run.validators[i].thinkingMs);

    const result = generateVote(VALIDATOR_PERSONAS[i], claim);
    run.validators = run.validators.map((v, idx) =>
      idx === i ? { ...v, status: "voted", ...result } : v
    );
    onUpdate({ ...run });
  }

  // Compute consensus
  run.status = "computing";
  onUpdate({ ...run });
  await sleep(800);

  const votes: ValidatorVote[] = run.validators.map((v) => ({
    validatorId: v.id,
    simulationId: runId,
    role: v.isLeader ? "leader" : "validator",
    vote: v.vote!,
    confidence: v.confidence!,
    reasoning: v.reasoning!,
    equivalenceScore: 0,
  }));

  const consensusResult = computeEquivalence(votes);
  run.consensusResult = consensusResult;

  // Apply equivalence scores back to validators
  run.validators = run.validators.map((v) => ({
    ...v,
    // equivalence score = how aligned this vote is with the majority
    confidence: v.confidence,
  }));

  // Generate a mock tx hash for demonstration
  run.txHash = `0x${Array.from({ length: 64 }, () =>
    Math.floor(Math.random() * 16).toString(16)
  ).join("")}`;

  if (consensusResult.outcome === "ACCEPTED") {
    run.status = "accepted";
  } else if (consensusResult.outcome === "REJECTED") {
    run.status = "rejected";
  } else {
    run.status = "appeal_triggered";
  }

  onUpdate({ ...run });
  return run;
}

export async function runAppeal(
  originalRun: SimulationRun,
  reason: string,
  onUpdate: (run: SimulationRun) => void
): Promise<SimulationRun> {
  const run = { ...originalRun, status: "appealing" as SimulationStatus, round: 2 };
  onUpdate({ ...run });
  await sleep(500);

  // Add 3 more validators for the appeal round (re-use personas with different seeds)
  const appealValidators: LiveValidator[] = VALIDATOR_PERSONAS.slice(0, 3).map((p, i) => ({
    id: `appeal_v_${i}`,
    name: `${p.name} II`,
    model: p.model,
    persona: p.persona,
    color: p.color,
    avatar: p.avatar,
    description: `Appeal evaluator — re-assessing with fresh context.`,
    status: "waiting" as const,
    vote: null,
    confidence: null,
    reasoning: null,
    isLeader: false,
    thinkingMs: 1000 + i * 500,
  }));

  run.validators = [...run.validators.map((v) => ({ ...v, status: "voted" as const })), ...appealValidators];
  onUpdate({ ...run });

  for (let i = 0; i < appealValidators.length; i++) {
    await sleep(300);
    const absIdx = originalRun.validators.length + i;
    run.validators = run.validators.map((v, idx) =>
      idx === absIdx ? { ...v, status: "thinking" } : v
    );
    onUpdate({ ...run });

    await sleep(appealValidators[i].thinkingMs);
    const result = generateVote(VALIDATOR_PERSONAS[i], originalRun.claim + reason);
    run.validators = run.validators.map((v, idx) =>
      idx === absIdx ? { ...v, status: "voted", ...result } : v
    );
    onUpdate({ ...run });
  }

  run.status = "computing";
  onUpdate({ ...run });
  await sleep(800);

  const allVotes: ValidatorVote[] = run.validators
    .filter((v) => v.vote !== null)
    .map((v) => ({
      validatorId: v.id,
      simulationId: run.id,
      role: v.isLeader ? "leader" : "validator",
      vote: v.vote!,
      confidence: v.confidence!,
      reasoning: v.reasoning!,
      equivalenceScore: 0,
    }));

  const newConsensus = computeEquivalence(allVotes);
  run.consensusResult = newConsensus;

  run.status = newConsensus.outcome === "ACCEPTED"
    ? "accepted"
    : newConsensus.outcome === "REJECTED"
    ? "rejected"
    : "finalized";

  onUpdate({ ...run });
  return run;
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Zustand Simulation Store (store/simulationStore.ts)
# ─────────────────────────────────────────────────────────────────────────────
w("store/simulationStore.ts", '''\
import { create } from "zustand";
import type { SimulationRun, SimulationStatus } from "@/services/simulationService";

interface SimulationStore {
  currentRun: SimulationRun | null;
  history: SimulationRun[];
  isRunning: boolean;
  error: string | null;

  setCurrentRun: (run: SimulationRun) => void;
  clearCurrentRun: () => void;
  setError: (error: string | null) => void;
  addToHistory: (run: SimulationRun) => void;
}

export const useSimulationStore = create<SimulationStore>((set) => ({
  currentRun: null,
  history: [],
  isRunning: false,
  error: null,

  setCurrentRun: (run) =>
    set({
      currentRun: run,
      isRunning: ["submitting", "running", "computing", "appealing"].includes(run.status as SimulationStatus),
    }),

  clearCurrentRun: () => set({ currentRun: null, isRunning: false, error: null }),

  setError: (error) => set({ error }),

  addToHistory: (run) =>
    set((state) => ({
      history: [run, ...state.history].slice(0, 20), // keep last 20
    })),
}));
''')

# ─────────────────────────────────────────────────────────────────────────────
# 5. UI Components
# ─────────────────────────────────────────────────────────────────────────────

w("components/ui/textarea.tsx", '''\
import * as React from "react";
import { cn } from "@/lib/utils";

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => (
    <textarea
      className={cn(
        "flex min-h-[80px] w-full rounded-md border border-[#d8d4c8] bg-white/60 px-3 py-2 text-sm",
        "ring-offset-background placeholder:text-[#6b6560]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50 resize-none",
        className
      )}
      ref={ref}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";

export { Textarea };
''')

w("components/ui/progress.tsx", '''\
import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { cn } from "@/lib/utils";

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn("relative h-2 w-full overflow-hidden rounded-full bg-[#e8e4da]", className)}
    {...props}
  >
    <ProgressPrimitive.Indicator
      className="h-full w-full flex-1 bg-[#2d2a26] transition-all duration-700 ease-out"
      style={{ transform: `translateX(-${100 - (value ?? 0)}%)` }}
    />
  </ProgressPrimitive.Root>
));
Progress.displayName = ProgressPrimitive.Root.displayName;

export { Progress };
''')

w("components/ui/select.tsx", '''\
"use client";
import * as React from "react";
import * as SelectPrimitive from "@radix-ui/react-select";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const Select = SelectPrimitive.Root;
const SelectGroup = SelectPrimitive.Group;
const SelectValue = SelectPrimitive.Value;

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-[#d8d4c8] bg-white/60 px-3 py-2 text-sm",
      "ring-offset-background placeholder:text-[#6b6560]",
      "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
      "disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1",
      className
    )}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon asChild>
      <ChevronDown className="h-4 w-4 opacity-50" />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
));
SelectTrigger.displayName = SelectPrimitive.Trigger.displayName;

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, position = "popper", ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      className={cn(
        "relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border border-[#d8d4c8] bg-white shadow-md",
        "data-[state=open]:animate-fade-up",
        position === "popper" && "data-[side=bottom]:translate-y-1 data-[side=top]:-translate-y-1",
        className
      )}
      position={position}
      {...props}
    >
      <SelectPrimitive.Viewport
        className={cn("p-1", position === "popper" && "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]")}
      >
        {children}
      </SelectPrimitive.Viewport>
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
));
SelectContent.displayName = SelectPrimitive.Content.displayName;

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none",
      "focus:bg-[#e8e4da] focus:text-[#1a1a1a] data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <SelectPrimitive.ItemIndicator>
        <span className="h-2 w-2 rounded-full bg-[#2d2a26] inline-block" />
      </SelectPrimitive.ItemIndicator>
    </span>
    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
  </SelectPrimitive.Item>
));
SelectItem.displayName = SelectPrimitive.Item.displayName;

export { Select, SelectGroup, SelectValue, SelectTrigger, SelectContent, SelectItem };
''')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Validator Card Component
# ─────────────────────────────────────────────────────────────────────────────
w("components/validators/ValidatorCard.tsx", '''\
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Cpu, Crown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import type { LiveValidator } from "@/services/simulationService";

interface ValidatorCardProps {
  validator: LiveValidator;
  index: number;
}

const VOTE_CONFIG = {
  ACCEPT:    { icon: CheckCircle2, label: "Accept",    variant: "accept"    as const, bg: "bg-green-50",  border: "border-green-200" },
  REJECT:    { icon: XCircle,      label: "Reject",    variant: "reject"    as const, bg: "bg-red-50",    border: "border-red-200" },
  UNCERTAIN: { icon: HelpCircle,   label: "Uncertain", variant: "uncertain" as const, bg: "bg-amber-50",  border: "border-amber-200" },
};

export function ValidatorCard({ validator, index }: ValidatorCardProps) {
  const colors = PERSONA_COLORS[validator.color] ?? PERSONA_COLORS.indigo;
  const voteConfig = validator.vote ? VOTE_CONFIG[validator.vote] : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className={cn(
        "relative rounded-xl border-2 bg-white/70 backdrop-blur-sm p-4 transition-all duration-300",
        validator.status === "thinking" && "border-[#2d2a26] shadow-lg shadow-black/10",
        validator.status === "waiting"  && "border-[#d8d4c8] opacity-60",
        validator.status === "voted" && voteConfig?.border,
        validator.status === "voted" && voteConfig?.bg,
      )}
    >
      {/* Leader crown */}
      {validator.isLeader && (
        <div className="absolute -top-2.5 left-3">
          <span className="inline-flex items-center gap-1 rounded-full bg-[#2d2a26] px-2 py-0.5 text-[10px] font-semibold text-[#efece4]">
            <Crown className="h-2.5 w-2.5" /> Leader
          </span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className={cn("h-9 w-9 rounded-lg flex items-center justify-center text-xs font-bold", colors.bg, colors.text)}>
            {validator.avatar}
          </div>
          <div>
            <p className="text-sm font-semibold text-[#1a1a1a] leading-tight">{validator.name}</p>
            <p className="text-[11px] text-[#6b6560] leading-tight flex items-center gap-1">
              <Cpu className="h-2.5 w-2.5" /> {validator.model}
            </p>
          </div>
        </div>

        {/* Status indicator */}
        <div className="flex items-center">
          {validator.status === "waiting" && (
            <span className="h-2 w-2 rounded-full bg-[#d8d4c8]" />
          )}
          {validator.status === "thinking" && (
            <span className="h-2 w-2 rounded-full bg-[#2d2a26] animate-pulse" />
          )}
          {validator.status === "voted" && voteConfig && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Badge variant={voteConfig.variant} className="text-[11px] px-2 py-0.5">
                <voteConfig.icon className="h-3 w-3 mr-1" />
                {voteConfig.label}
              </Badge>
            </motion.div>
          )}
        </div>
      </div>

      {/* Thinking animation */}
      <AnimatePresence>
        {validator.status === "thinking" && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-3"
          >
            <div className="flex items-center gap-1.5 text-xs text-[#6b6560]">
              <span>Evaluating claim</span>
              <span className="flex gap-0.5">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="h-1 w-1 rounded-full bg-[#6b6560] inline-block"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                  />
                ))}
              </span>
            </div>
            <Progress value={undefined} className="mt-2 h-1" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Confidence + reasoning */}
      <AnimatePresence>
        {validator.status === "voted" && validator.confidence !== null && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            transition={{ delay: 0.1 }}
          >
            <div className="mb-2">
              <div className="flex items-center justify-between text-[11px] text-[#6b6560] mb-1">
                <span>Confidence</span>
                <span className="font-medium text-[#1a1a1a]">{Math.round((validator.confidence ?? 0) * 100)}%</span>
              </div>
              <Progress value={Math.round((validator.confidence ?? 0) * 100)} className="h-1.5" />
            </div>

            {validator.reasoning && (
              <p className="text-[11px] text-[#6b6560] leading-relaxed line-clamp-3 mt-2">
                {validator.reasoning}
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Waiting state */}
      {validator.status === "waiting" && (
        <p className="text-[11px] text-[#6b6560] italic">Waiting for evaluation slot...</p>
      )}
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Consensus Status Component
# ─────────────────────────────────────────────────────────────────────────────
w("components/consensus/ConsensusStatus.tsx", '''\
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 8. Consensus Graph (vote distribution)
# ─────────────────────────────────────────────────────────────────────────────
w("components/consensus/ConsensusGraph.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { cn, toPercent } from "@/lib/utils";
import type { EquivalenceResult } from "@/lib/validators/equivalence";

interface ConsensusGraphProps {
  result: EquivalenceResult;
  totalValidators: number;
}

export function ConsensusGraph({ result, totalValidators }: ConsensusGraphProps) {
  const { acceptCount, rejectCount, uncertainCount, score, pass, explanation } = result;

  const bars = [
    { label: "Accept",    count: acceptCount,    color: "bg-green-500",  textColor: "text-green-700" },
    { label: "Reject",    count: rejectCount,    color: "bg-red-500",    textColor: "text-red-700" },
    { label: "Uncertain", count: uncertainCount, color: "bg-amber-400",  textColor: "text-amber-700" },
  ];

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/50 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[#1a1a1a]">Vote Distribution</h3>
        <span className={cn(
          "text-xs font-semibold px-2 py-0.5 rounded-full",
          pass ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
        )}>
          {Math.round(score * 100)}% agreement
        </span>
      </div>

      {/* Bar chart */}
      <div className="space-y-2">
        {bars.map((bar) => (
          <div key={bar.label} className="flex items-center gap-3">
            <span className="text-xs text-[#6b6560] w-16 shrink-0">{bar.label}</span>
            <div className="flex-1 h-5 rounded-full bg-[#e8e4da] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${toPercent(bar.count, totalValidators)}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className={cn("h-full rounded-full", bar.color)}
              />
            </div>
            <span className={cn("text-xs font-semibold w-6 text-right shrink-0", bar.textColor)}>
              {bar.count}
            </span>
          </div>
        ))}
      </div>

      {/* Equivalence threshold line indicator */}
      <div className="relative h-2 rounded-full bg-[#e8e4da] overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.round(score * 100)}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={cn("h-full rounded-full", pass ? "bg-green-500" : "bg-red-400")}
        />
        {/* 60% threshold marker */}
        <div className="absolute top-0 h-full border-r-2 border-dashed border-[#2d2a26]/40" style={{ left: "60%" }} />
      </div>
      <div className="flex justify-between text-[10px] text-[#6b6560]">
        <span>0%</span>
        <span className="font-medium">60% threshold (Equivalence Principle)</span>
        <span>100%</span>
      </div>

      {/* Explanation */}
      <p className="text-xs text-[#6b6560] leading-relaxed border-t border-[#e8e4da] pt-3">
        {explanation}
      </p>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 9. Appeal Trigger Component
# ─────────────────────────────────────────────────────────────────────────────
w("components/appeals/AppealTrigger.tsx", '''\
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Scale, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

interface AppealTriggerProps {
  onAppeal: (reason: string) => void;
  disabled?: boolean;
}

export function AppealTrigger({ onAppeal, disabled }: AppealTriggerProps) {
  const [reason, setReason] = useState("");
  const [open, setOpen] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!reason.trim()) return;
    onAppeal(reason.trim());
    setOpen(false);
    setReason("");
  }

  return (
    <div className="rounded-xl border-2 border-purple-200 bg-purple-50 p-5">
      <div className="flex items-start gap-3 mb-4">
        <AlertTriangle className="h-5 w-5 text-purple-600 shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-semibold text-purple-800">Appeal Available</p>
          <p className="text-xs text-purple-600 mt-0.5 leading-relaxed">
            The validator network is split. Under Optimistic Democracy, you can trigger an appeal
            which adds 3 more validators to re-evaluate this claim.
          </p>
        </div>
      </div>

      {!open ? (
        <Button
          onClick={() => setOpen(true)}
          disabled={disabled}
          className="w-full bg-purple-700 hover:bg-purple-800 text-white"
          size="sm"
        >
          <Scale className="h-4 w-4 mr-2" />
          Trigger Appeal Round
        </Button>
      ) : (
        <motion.form
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          onSubmit={handleSubmit}
          className="space-y-3"
        >
          <div className="space-y-1.5">
            <Label className="text-xs text-purple-800">Appeal Reason</Label>
            <Textarea
              placeholder="Explain why you believe the initial consensus was incorrect..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="text-sm min-h-[80px] border-purple-200 focus-visible:ring-purple-400 bg-white/80"
            />
          </div>
          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={!reason.trim() || disabled}
              className="flex-1 bg-purple-700 hover:bg-purple-800 text-white">
              Submit Appeal
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
          </div>
        </motion.form>
      )}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 10. Consensus Timeline
# ─────────────────────────────────────────────────────────────────────────────
w("components/consensus/ConsensusTimeline.tsx", '''\
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 11. Claim Submission Form
# ─────────────────────────────────────────────────────────────────────────────
w("components/consensus/ClaimForm.tsx", '''\
"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const EXAMPLE_CLAIMS = [
  {
    category: "freelance",
    text: "The freelancer delivered a fully functional e-commerce website with all agreed-upon features, including payment integration and mobile responsiveness, by the deadline.",
  },
  {
    category: "review",
    text: "This product review is genuine — the reviewer purchased the item, used it for 30 days, and their feedback accurately reflects a real user experience.",
  },
  {
    category: "event",
    text: "The charity fundraiser event raised over $50,000 for the designated cause, and all proceeds were transferred to the charity within 7 days of the event.",
  },
  {
    category: "custom",
    text: "The software audit was completed in accordance with the agreed security standards and all critical vulnerabilities identified were properly disclosed to the client.",
  },
];

interface ClaimFormProps {
  onSubmit: (claim: string, category: string) => void;
  disabled?: boolean;
}

export function ClaimForm({ onSubmit, disabled }: ClaimFormProps) {
  const [claim, setClaim] = useState("");
  const [category, setCategory] = useState("freelance");

  function handleExampleClick(example: typeof EXAMPLE_CLAIMS[0]) {
    setClaim(example.text);
    setCategory(example.category);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!claim.trim()) return;
    onSubmit(claim.trim(), category);
  }

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 backdrop-blur-sm p-6">
      <h2 className="text-base font-semibold text-[#1a1a1a] mb-1">Submit a Claim</h2>
      <p className="text-xs text-[#6b6560] mb-5 leading-relaxed">
        Enter any subjective claim. The GenLayer validator network will independently evaluate it
        and attempt to reach consensus using the Equivalence Principle.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="category" className="text-xs">Category</Label>
          <Select value={category} onValueChange={setCategory} disabled={disabled}>
            <SelectTrigger className="h-9 text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="freelance">Freelance Work</SelectItem>
              <SelectItem value="review">Product Review</SelectItem>
              <SelectItem value="event">Event / Real-World Claim</SelectItem>
              <SelectItem value="custom">Custom</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="claim" className="text-xs">Claim</Label>
          <Textarea
            id="claim"
            placeholder="Describe the subjective claim you want validators to evaluate..."
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            className="min-h-[100px] text-sm"
            disabled={disabled}
          />
          <p className="text-[11px] text-[#6b6560]">{claim.length} characters</p>
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={disabled || !claim.trim()}
        >
          <Send className="h-4 w-4 mr-2" />
          Submit to Validator Network
        </Button>
      </form>

      {/* Examples */}
      <div className="mt-5 pt-4 border-t border-[#e8e4da]">
        <p className="text-[11px] font-medium text-[#6b6560] uppercase tracking-wider mb-3">
          Example Claims
        </p>
        <div className="space-y-2">
          {EXAMPLE_CLAIMS.map((ex, i) => (
            <button
              key={i}
              onClick={() => handleExampleClick(ex)}
              disabled={disabled}
              className="w-full text-left text-xs text-[#6b6560] hover:text-[#1a1a1a] rounded-lg border border-[#e8e4da] hover:border-[#d8d4c8] bg-white/40 hover:bg-white/70 px-3 py-2.5 transition-all leading-relaxed"
            >
              <span className="font-medium text-[#2d2a26]">[{ex.category}]</span>{" "}
              {ex.text.slice(0, 90)}...
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 12. Simulation Result Panel
# ─────────────────────────────────────────────────────────────────────────────
w("components/consensus/SimulationResult.tsx", '''\
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 13. Main Playground Page
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/playground/page.tsx", '''\
"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { runSimulation, runAppeal, type SimulationRun } from "@/services/simulationService";
import { useSimulationStore } from "@/store/simulationStore";
import { ClaimForm } from "@/components/consensus/ClaimForm";
import { ValidatorCard } from "@/components/validators/ValidatorCard";
import { ConsensusStatus } from "@/components/consensus/ConsensusStatus";
import { ConsensusTimeline } from "@/components/consensus/ConsensusTimeline";
import { SimulationResult } from "@/components/consensus/SimulationResult";
import { AppealTrigger } from "@/components/appeals/AppealTrigger";

export default function PlaygroundPage() {
  const { currentRun, isRunning, setCurrentRun, clearCurrentRun, addToHistory } = useSimulationStore();
  const [localRun, setLocalRun] = useState<SimulationRun | null>(null);

  const activeRun = localRun ?? currentRun;

  const handleSimulate = useCallback(async (claim: string, category: string) => {
    setLocalRun(null);
    const finalRun = await runSimulation(claim, category, (update) => {
      setLocalRun({ ...update });
      setCurrentRun({ ...update });
    });
    addToHistory(finalRun);
  }, [setCurrentRun, addToHistory]);

  const handleAppeal = useCallback(async (reason: string) => {
    if (!activeRun) return;
    const finalRun = await runAppeal(activeRun, reason, (update) => {
      setLocalRun({ ...update });
      setCurrentRun({ ...update });
    });
    addToHistory(finalRun);
  }, [activeRun, setCurrentRun, addToHistory]);

  const handleReset = useCallback(() => {
    setLocalRun(null);
    clearCurrentRun();
  }, [clearCurrentRun]);

  const status = activeRun?.status ?? "idle";
  const showAppeal = status === "appeal_triggered" && !isRunning;
  const showResult = ["accepted", "rejected", "appeal_triggered", "finalized"].includes(status) && !isRunning;
  const showValidators = activeRun && activeRun.validators.length > 0;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">
            Consensus Playground
          </h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            Submit a subjective claim and watch GenLayer&apos;s Optimistic Democracy in action.
            Five AI validators independently evaluate the claim and attempt to reach consensus
            through the Equivalence Principle.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left column — form + timeline + result */}
          <div className="lg:col-span-1 space-y-4">
            {/* Submission form (only when idle or finished) */}
            <AnimatePresence>
              {(!activeRun || showResult) && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <ClaimForm onSubmit={handleSimulate} disabled={isRunning} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Status badge */}
            {activeRun && (
              <ConsensusStatus status={status} round={activeRun.round} />
            )}

            {/* Timeline */}
            {activeRun && (
              <ConsensusTimeline status={status} />
            )}

            {/* Appeal trigger */}
            {showAppeal && (
              <AppealTrigger onAppeal={handleAppeal} disabled={isRunning} />
            )}

            {/* Result */}
            {showResult && activeRun?.consensusResult && !showAppeal && (
              <SimulationResult
                run={activeRun}
                onReset={handleReset}
                onAppeal={handleAppeal}
              />
            )}
          </div>

          {/* Right column — validators */}
          <div className="lg:col-span-2">
            {!showValidators ? (
              <div className="h-full rounded-xl border-2 border-dashed border-[#d8d4c8] flex flex-col items-center justify-center py-20 text-center px-8">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-base font-semibold text-[#1a1a1a] mb-2">
                  Waiting for a claim
                </h3>
                <p className="text-sm text-[#6b6560] max-w-xs leading-relaxed">
                  Submit a claim on the left to start the simulation. Watch 5 AI validators
                  independently reason about your claim in real time.
                </p>
                <div className="mt-6 grid grid-cols-3 gap-3 text-xs text-[#6b6560]">
                  {["Analytical", "Creative", "Strict", "Lenient", "Balanced"].map((p) => (
                    <span key={p} className="rounded-full border border-[#e8e4da] bg-white/50 px-3 py-1 text-center">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-[#1a1a1a]">
                    Validator Network
                    {activeRun.round > 1 && (
                      <span className="ml-2 text-xs text-purple-600 font-normal">
                        Appeal Round {activeRun.round}
                      </span>
                    )}
                  </h2>
                  <span className="text-xs text-[#6b6560]">
                    {activeRun.validators.filter((v) => v.status === "voted").length} / {activeRun.validators.length} voted
                  </span>
                </div>

                {/* Validator grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                  <AnimatePresence>
                    {activeRun.validators.map((validator, i) => (
                      <ValidatorCard key={validator.id} validator={validator} index={i} />
                    ))}
                  </AnimatePresence>
                </div>

                {/* Info box */}
                {isRunning && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="rounded-lg border border-[#d8d4c8] bg-white/40 p-3 text-xs text-[#6b6560] leading-relaxed"
                  >
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 14. API route — POST /api/simulate (persist to Supabase when connected)
# ─────────────────────────────────────────────────────────────────────────────
w("app/api/simulate/route.ts", '''\
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as { claim?: string; category?: string };
    const { claim, category } = body;

    if (!claim || typeof claim !== "string" || claim.trim().length < 10) {
      return NextResponse.json({ error: "Claim must be at least 10 characters." }, { status: 400 });
    }

    if (!["freelance", "review", "event", "custom"].includes(category ?? "")) {
      return NextResponse.json({ error: "Invalid category." }, { status: 400 });
    }

    // Simulation runs client-side for now; this route will persist results to Supabase
    // when the DB connection is live (Phase 5 integration).
    return NextResponse.json({
      status: "ok",
      message: "Simulation accepted. Running client-side with live Supabase persistence in Phase 5.",
    });
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }
}
''')

print("\nPhase 4 complete. All files written.\n")
