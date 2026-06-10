"""Phase 6: Appeals Arena — appeal history, round breakdown, validator expansion, mechanics education."""
import pathlib, json

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  WROTE  {rel}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Appeals Store (Zustand + persist)
# ─────────────────────────────────────────────────────────────────────────────
w("store/appealStore.ts", '''\
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SimulationRun } from "@/services/simulationService";
import type { EquivalenceResult } from "@/lib/validators/equivalence";

export type AppealStatus = "pending" | "in_progress" | "resolved_accept" | "resolved_reject" | "escalated";

export interface AppealRound {
  roundNumber: number;
  validatorCount: number;
  votes: { name: string; vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number }[];
  equivalenceResult: EquivalenceResult;
  outcome: "ACCEPTED" | "REJECTED" | "APPEAL_TRIGGERED";
  durationMs: number;
}

export interface AppealRecord {
  id: string;
  simulationId: string;
  claim: string;
  category: string;
  appealReason: string;
  status: AppealStatus;
  rounds: AppealRound[];
  createdAt: number;
  resolvedAt: number | null;
  finalOutcome: "ACCEPTED" | "REJECTED" | null;
}

interface AppealStore {
  appeals: AppealRecord[];
  activeAppealId: string | null;

  createAppeal: (run: SimulationRun, reason: string) => string;
  addRound: (appealId: string, round: AppealRound) => void;
  resolveAppeal: (appealId: string, outcome: "ACCEPTED" | "REJECTED") => void;
  setActiveAppeal: (id: string | null) => void;
  clearAppeals: () => void;
}

export const useAppealStore = create<AppealStore>()(
  persist(
    (set, get) => ({
      appeals: [],
      activeAppealId: null,

      createAppeal: (run, reason) => {
        const id = `appeal_${Date.now()}`;

        // Build round 1 from the original simulation data
        const round1: AppealRound = {
          roundNumber: 1,
          validatorCount: run.validators.filter((v) => v.vote !== null).length,
          votes: run.validators
            .filter((v) => v.vote !== null)
            .map((v) => ({ name: v.name, vote: v.vote!, confidence: v.confidence ?? 0 })),
          equivalenceResult: run.consensusResult!,
          outcome: run.consensusResult!.outcome,
          durationMs: Date.now() - run.startedAt,
        };

        const record: AppealRecord = {
          id,
          simulationId: run.id,
          claim: run.claim,
          category: run.category,
          appealReason: reason,
          status: "in_progress",
          rounds: [round1],
          createdAt: Date.now(),
          resolvedAt: null,
          finalOutcome: null,
        };

        set((s) => ({ appeals: [record, ...s.appeals], activeAppealId: id }));
        return id;
      },

      addRound: (appealId, round) =>
        set((s) => ({
          appeals: s.appeals.map((a) =>
            a.id === appealId ? { ...a, rounds: [...a.rounds, round] } : a
          ),
        })),

      resolveAppeal: (appealId, outcome) =>
        set((s) => ({
          appeals: s.appeals.map((a) =>
            a.id === appealId
              ? {
                  ...a,
                  status: outcome === "ACCEPTED" ? "resolved_accept" : "resolved_reject",
                  finalOutcome: outcome,
                  resolvedAt: Date.now(),
                }
              : a
          ),
        })),

      setActiveAppeal: (id) => set({ activeAppealId: id }),

      clearAppeals: () => set({ appeals: [], activeAppealId: null }),
    }),
    { name: "appeals-arena-store", partialize: (s) => ({ appeals: s.appeals }) }
  )
);
''')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Appeal Engine service
# ─────────────────────────────────────────────────────────────────────────────
w("services/appealService.ts", '''\
import { VALIDATOR_PERSONAS } from "@/lib/validators/personas";
import { computeEquivalence } from "@/lib/validators/equivalence";
import { sleep } from "@/lib/utils";
import { useAppealStore, type AppealRound } from "@/store/appealStore";
import type { SimulationRun, LiveValidator } from "@/services/simulationService";
import type { ValidatorVote } from "@/types/validator";

// Reasoning templates for appeal round validators
const APPEAL_REASONING: Record<string, (claim: string, vote: string, round: number) => string> = {
  ACCEPT: (claim, _v, round) =>
    round === 1
      ? `Re-evaluating "${claim.slice(0, 55)}…" with a fresh perspective. The core claim stands up to scrutiny — I find sufficient grounds for acceptance on appeal.`
      : `After extended deliberation across ${round} rounds, the weight of evidence still supports acceptance. My position is unchanged.`,
  REJECT: (claim, _v, round) =>
    round === 1
      ? `Reviewing "${claim.slice(0, 55)}…" as an appeal validator. The original rejection concerns remain unaddressed. I concur: this claim does not meet the required standard.`
      : `This is round ${round} of review. The fundamental issues with this claim persist. Rejection stands.`,
  UNCERTAIN: (claim, _v, round) =>
    `Even on appeal (round ${round}), "${claim.slice(0, 55)}…" remains genuinely ambiguous. I cannot commit to either outcome without additional context.`,
};

function generateAppealVote(
  personaIdx: number,
  claim: string,
  round: number,
  seed: string
): { vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number; reasoning: string } {
  const persona = VALIDATOR_PERSONAS[personaIdx % VALIDATOR_PERSONAS.length];
  const hash = Array.from(claim + persona.name + seed + round).reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = ((hash * 6271 + 31337) % 233280) / 233280;

  const band = persona.uncertaintyRange;
  const thr  = persona.acceptThreshold;

  let vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  let confidence: number;

  if (rand > thr + band / 2) {
    vote = "ACCEPT";
    confidence = Math.min(0.97, persona.confidenceBase + (rand - thr) * 0.15);
  } else if (rand < thr - band / 2) {
    vote = "REJECT";
    confidence = Math.min(0.97, persona.confidenceBase + (thr - rand) * 0.15);
  } else {
    vote = "UNCERTAIN";
    confidence = persona.confidenceBase * 0.65;
  }

  confidence = Math.max(0.52, confidence);
  const reasoning = APPEAL_REASONING[vote]?.(claim, vote, round) ?? "";
  return { vote, confidence, reasoning };
}

export interface AppealValidatorUpdate {
  id: string;
  name: string;
  model: string;
  avatar: string;
  color: string;
  isOriginal: boolean;
  status: "waiting" | "thinking" | "voted";
  vote: "ACCEPT" | "REJECT" | "UNCERTAIN" | null;
  confidence: number | null;
  reasoning: string | null;
  round: number;
}

export async function executeAppealRound(
  originalRun: SimulationRun,
  reason: string,
  roundNumber: number,
  onUpdate: (validators: AppealValidatorUpdate[]) => void
): Promise<AppealRound> {
  const startTime = Date.now();

  // Original validators carry over their votes (frozen)
  const originalValidators: AppealValidatorUpdate[] = originalRun.validators
    .filter((v) => v.vote !== null)
    .map((v) => ({
      id: v.id,
      name: v.name,
      model: v.model,
      avatar: v.avatar,
      color: v.color,
      isOriginal: true,
      status: "voted" as const,
      vote: v.vote,
      confidence: v.confidence,
      reasoning: v.reasoning,
      round: 1,
    }));

  // Appeal validators — expand by 3 each round (capped at 5 extra)
  const extraCount = Math.min(3 + (roundNumber - 2) * 2, 5);
  const appealValidators: AppealValidatorUpdate[] = Array.from({ length: extraCount }, (_, i) => {
    const p = VALIDATOR_PERSONAS[(i + roundNumber) % VALIDATOR_PERSONAS.length];
    return {
      id: `appeal_r${roundNumber}_v${i}`,
      name: `${p.name} (R${roundNumber})`,
      model: p.model,
      avatar: p.avatar,
      color: p.color,
      isOriginal: false,
      status: "waiting" as const,
      vote: null,
      confidence: null,
      reasoning: null,
      round: roundNumber,
    };
  });

  const allValidators = [...originalValidators, ...appealValidators];
  onUpdate([...allValidators]);

  // Stagger appeal votes
  for (let i = 0; i < appealValidators.length; i++) {
    await sleep(350);
    allValidators[originalValidators.length + i] = {
      ...allValidators[originalValidators.length + i],
      status: "thinking",
    };
    onUpdate([...allValidators]);

    await sleep(900 + i * 400);

    const result = generateAppealVote(i + roundNumber, originalRun.claim, roundNumber, reason);
    allValidators[originalValidators.length + i] = {
      ...allValidators[originalValidators.length + i],
      status: "voted",
      ...result,
    };
    onUpdate([...allValidators]);
  }

  // Compute new equivalence over ALL votes (original + appeal)
  const allVotes: ValidatorVote[] = allValidators
    .filter((v) => v.vote !== null)
    .map((v) => ({
      validatorId: v.id,
      simulationId: originalRun.id,
      role: "validator" as const,
      vote: v.vote!,
      confidence: v.confidence!,
      reasoning: v.reasoning ?? "",
      equivalenceScore: 0,
    }));

  const equivalenceResult = computeEquivalence(allVotes);

  const round: AppealRound = {
    roundNumber,
    validatorCount: allVotes.length,
    votes: allValidators
      .filter((v) => v.vote !== null)
      .map((v) => ({ name: v.name, vote: v.vote!, confidence: v.confidence! })),
    equivalenceResult,
    outcome: equivalenceResult.outcome,
    durationMs: Date.now() - startTime,
  };

  // Persist to store
  const { addRound, resolveAppeal, activeAppealId } = useAppealStore.getState();
  if (activeAppealId) {
    addRound(activeAppealId, round);
    if (equivalenceResult.outcome !== "APPEAL_TRIGGERED") {
      resolveAppeal(activeAppealId, equivalenceResult.outcome === "ACCEPTED" ? "ACCEPTED" : "REJECTED");
    }
  }

  return round;
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Appeal Round Visualizer component
# ─────────────────────────────────────────────────────────────────────────────
w("components/appeals/AppealRoundCard.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Users, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { AppealRound } from "@/store/appealStore";

interface AppealRoundCardProps {
  round: AppealRound;
  index: number;
  isLatest: boolean;
}

const VOTE_CFG = {
  ACCEPT:    { icon: CheckCircle2, cls: "text-green-600", bg: "bg-green-100" },
  REJECT:    { icon: XCircle,      cls: "text-red-600",   bg: "bg-red-100" },
  UNCERTAIN: { icon: HelpCircle,   cls: "text-amber-600", bg: "bg-amber-100" },
};

const OUTCOME_CFG = {
  ACCEPTED:          { label: "Accepted",         variant: "accept"    as const },
  REJECTED:          { label: "Rejected",         variant: "reject"    as const },
  APPEAL_TRIGGERED:  { label: "Appeal Triggered", variant: "appealed"  as const },
};

export function AppealRoundCard({ round, index, isLatest }: AppealRoundCardProps) {
  const { acceptCount, rejectCount, uncertainCount, score } = round.equivalenceResult;
  const outCfg = OUTCOME_CFG[round.outcome];

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08 }}
      className={cn(
        "rounded-xl border-2 p-5 transition-all",
        isLatest ? "border-[#2d2a26] bg-white/80 shadow-md" : "border-[#d8d4c8] bg-white/50"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={cn(
              "text-xs font-bold px-2 py-0.5 rounded-full",
              round.roundNumber === 1 ? "bg-[#2d2a26] text-[#efece4]" : "bg-purple-100 text-purple-800"
            )}>
              {round.roundNumber === 1 ? "Initial Round" : `Appeal Round ${round.roundNumber}`}
            </span>
            {isLatest && <span className="text-[10px] text-[#6b6560] font-medium">Latest</span>}
          </div>
          <div className="flex items-center gap-3 text-[11px] text-[#6b6560]">
            <span className="flex items-center gap-1"><Users className="h-3 w-3" /> {round.validatorCount} validators</span>
            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {(round.durationMs / 1000).toFixed(1)}s</span>
          </div>
        </div>
        <Badge variant={outCfg.variant} className="text-xs">{outCfg.label}</Badge>
      </div>

      {/* Vote chips */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {round.votes.map((v, i) => {
          const cfg = VOTE_CFG[v.vote];
          const Icon = cfg.icon;
          return (
            <div key={i} className={cn("flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium", cfg.bg, cfg.cls)}>
              <Icon className="h-2.5 w-2.5" />
              {v.name.split(" ")[0]}
              <span className="opacity-70">{Math.round(v.confidence * 100)}%</span>
            </div>
          );
        })}
      </div>

      {/* Agreement bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-[11px] text-[#6b6560]">
          <span>Agreement</span>
          <span className="font-semibold text-[#1a1a1a]">{Math.round(score * 100)}%</span>
        </div>
        <div className="relative h-2.5 rounded-full bg-[#e8e4da] overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.round(score * 100)}%` }}
            transition={{ duration: 0.9, ease: "easeOut" }}
            className={cn("h-full rounded-full", round.equivalenceResult.pass ? "bg-green-500" : "bg-red-400")}
          />
          <div className="absolute top-0 h-full border-r-2 border-dashed border-[#2d2a26]/30" style={{ left: "60%" }} />
        </div>
        <div className="flex gap-4 text-[10px] text-[#6b6560]">
          <span className="text-green-700 font-medium">✓ {acceptCount} accept</span>
          <span className="text-red-700 font-medium">✗ {rejectCount} reject</span>
          <span className="text-amber-700 font-medium">? {uncertainCount} uncertain</span>
        </div>
      </div>

      {/* Explanation */}
      <p className="text-[11px] text-[#6b6560] leading-relaxed mt-3 pt-3 border-t border-[#e8e4da]">
        {round.equivalenceResult.explanation}
      </p>
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Appeal Validator Grid (live voting panel for appeal round)
# ─────────────────────────────────────────────────────────────────────────────
w("components/appeals/AppealValidatorGrid.tsx", '''\
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, HelpCircle, Crown, Cpu, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PERSONA_COLORS } from "@/lib/validators/personas";
import type { AppealValidatorUpdate } from "@/services/appealService";

interface AppealValidatorGridProps {
  validators: AppealValidatorUpdate[];
}

const VOTE_CFG = {
  ACCEPT:    { icon: CheckCircle2, variant: "accept"    as const },
  REJECT:    { icon: XCircle,      variant: "reject"    as const },
  UNCERTAIN: { icon: HelpCircle,   variant: "uncertain" as const },
};

export function AppealValidatorGrid({ validators }: AppealValidatorGridProps) {
  const original = validators.filter((v) => v.isOriginal);
  const appeal   = validators.filter((v) => !v.isOriginal);

  return (
    <div className="space-y-5">
      {/* Original validators */}
      {original.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Crown className="h-3 w-3" /> Original Validators (Round 1)
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {original.map((v, i) => (
              <ValidatorMiniCard key={v.id} validator={v} index={i} dimmed />
            ))}
          </div>
        </div>
      )}

      {/* Appeal validators */}
      {appeal.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-purple-700 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Shield className="h-3 w-3" /> Appeal Validators (Round {appeal[0]?.round})
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {appeal.map((v, i) => (
              <ValidatorMiniCard key={v.id} validator={v} index={i} highlight />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ValidatorMiniCard({
  validator: v,
  index,
  dimmed,
  highlight,
}: {
  validator: AppealValidatorUpdate;
  index: number;
  dimmed?: boolean;
  highlight?: boolean;
}) {
  const colors = PERSONA_COLORS[v.color] ?? PERSONA_COLORS.indigo;
  const voteCfg = v.vote ? VOTE_CFG[v.vote] : null;
  const Icon = voteCfg?.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: dimmed ? 0.7 : 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      className={cn(
        "rounded-lg border p-3 text-center",
        highlight && v.status === "thinking" && "border-purple-300 bg-purple-50",
        highlight && v.status === "voted"   && "border-purple-200 bg-purple-50/50",
        highlight && v.status === "waiting" && "border-[#d8d4c8] bg-white/40",
        dimmed && "border-[#e8e4da] bg-white/30",
      )}
    >
      <div className={cn("h-8 w-8 rounded-lg flex items-center justify-center text-xs font-bold mx-auto mb-2", colors.bg, colors.text)}>
        {v.avatar}
      </div>
      <p className="text-[10px] font-semibold text-[#1a1a1a] leading-tight truncate">{v.name.split(" ")[0]}</p>
      <p className="text-[9px] text-[#6b6560] flex items-center justify-center gap-0.5 mt-0.5">
        <Cpu className="h-2 w-2" /> {v.model.split("-")[0]}
      </p>

      <div className="mt-2">
        {v.status === "waiting" && <span className="h-1.5 w-1.5 rounded-full bg-[#d8d4c8] inline-block" />}
        {v.status === "thinking" && (
          <span className="flex justify-center gap-0.5">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="h-1 w-1 rounded-full bg-purple-500 inline-block"
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </span>
        )}
        {v.status === "voted" && voteCfg && Icon && (
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 300 }}>
            <Badge variant={voteCfg.variant} className="text-[9px] px-1.5 py-0">
              <Icon className="h-2.5 w-2.5 mr-0.5" /> {v.vote}
            </Badge>
            <div className="mt-1">
              <Progress value={Math.round((v.confidence ?? 0) * 100)} className="h-0.5" />
              <p className="text-[9px] text-[#6b6560] mt-0.5">{Math.round((v.confidence ?? 0) * 100)}%</p>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 5. Appeal History List
# ─────────────────────────────────────────────────────────────────────────────
w("components/appeals/AppealHistory.tsx", '''\
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, AlertTriangle, Clock, ChevronRight, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AppealRecord, AppealStatus } from "@/store/appealStore";

interface AppealHistoryProps {
  appeals: AppealRecord[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onClear: () => void;
}

const STATUS_CFG: Record<AppealStatus, { label: string; icon: React.ElementType; cls: string }> = {
  pending:          { label: "Pending",           icon: Clock,          cls: "text-[#6b6560]" },
  in_progress:      { label: "In Progress",       icon: AlertTriangle,  cls: "text-amber-600" },
  resolved_accept:  { label: "Resolved: Accept",  icon: CheckCircle2,   cls: "text-green-600" },
  resolved_reject:  { label: "Resolved: Reject",  icon: XCircle,        cls: "text-red-600" },
  escalated:        { label: "Escalated",         icon: AlertTriangle,  cls: "text-purple-600" },
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function AppealHistory({ appeals, activeId, onSelect, onClear }: AppealHistoryProps) {
  if (appeals.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-[#d8d4c8] py-10 text-center">
        <p className="text-sm text-[#6b6560]">No appeals recorded yet.</p>
        <p className="text-xs text-[#6b6560] mt-1">
          Trigger an appeal from the Playground when validators disagree.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">
          {appeals.length} appeal{appeals.length !== 1 ? "s" : ""}
        </p>
        <Button variant="ghost" size="sm" className="h-7 text-xs text-[#6b6560] hover:text-red-500" onClick={onClear}>
          <Trash2 className="h-3 w-3 mr-1" /> Clear
        </Button>
      </div>
      <AnimatePresence>
        {appeals.map((a, i) => {
          const cfg = STATUS_CFG[a.status];
          const Icon = cfg.icon;
          const isActive = a.id === activeId;

          return (
            <motion.button
              key={a.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => onSelect(a.id)}
              className={cn(
                "w-full text-left rounded-xl border-2 p-4 transition-all hover:shadow-sm",
                isActive ? "border-[#2d2a26] bg-white/80" : "border-[#d8d4c8] bg-white/50 hover:border-[#b8b4a8]"
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-[#1a1a1a] line-clamp-2 leading-relaxed">
                    {a.claim.slice(0, 100)}{a.claim.length > 100 ? "…" : ""}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className={cn("flex items-center gap-1 text-[11px]", cfg.cls)}>
                      <Icon className="h-3 w-3" /> {cfg.label}
                    </span>
                    <span className="text-[10px] text-[#6b6560]">·</span>
                    <span className="text-[10px] text-[#6b6560]">{a.rounds.length} round{a.rounds.length !== 1 ? "s" : ""}</span>
                    <span className="text-[10px] text-[#6b6560]">·</span>
                    <span className="text-[10px] text-[#6b6560]">{timeAgo(a.createdAt)}</span>
                  </div>
                </div>
                <ChevronRight className={cn("h-4 w-4 shrink-0 mt-0.5 transition-transform", isActive && "rotate-90 text-[#2d2a26]", "text-[#d8d4c8]")} />
              </div>
            </motion.button>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Appeal Detail Panel
# ─────────────────────────────────────────────────────────────────────────────
w("components/appeals/AppealDetail.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { Scale, Clock, Hash, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { AppealRoundCard } from "./AppealRoundCard";
import { formatAddress } from "@/lib/utils";
import type { AppealRecord } from "@/store/appealStore";

interface AppealDetailProps {
  appeal: AppealRecord;
}

const OUTCOME_VARIANT: Record<string, "accept" | "reject" | "appealed"> = {
  ACCEPTED: "accept",
  REJECTED: "reject",
};

function timeAgo(ts: number): string {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return `${Math.floor(s / 3600)}h ago`;
}

export function AppealDetail({ appeal }: AppealDetailProps) {
  const totalMs = appeal.rounds.reduce((s, r) => s + r.durationMs, 0);
  const roundCount = appeal.rounds.length;
  const appealRounds = appeal.rounds.filter((r) => r.roundNumber > 1);

  return (
    <motion.div
      key={appeal.id}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5"
    >
      {/* Claim header */}
      <div className="rounded-xl border-2 border-[#d8d4c8] bg-white/60 p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Scale className="h-4 w-4 text-[#6b6560] shrink-0" />
              <span className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">Appeal Case</span>
              {appeal.finalOutcome && (
                <Badge variant={OUTCOME_VARIANT[appeal.finalOutcome] ?? "outline"} className="text-xs">
                  Final: {appeal.finalOutcome}
                </Badge>
              )}
            </div>
            <p className="text-sm text-[#1a1a1a] leading-relaxed">
              &ldquo;{appeal.claim}&rdquo;
            </p>
          </div>
        </div>

        <Separator className="my-3" />

        {/* Reason */}
        <div className="flex items-start gap-2 mb-4">
          <FileText className="h-3.5 w-3.5 text-[#6b6560] mt-0.5 shrink-0" />
          <div>
            <p className="text-[10px] font-semibold text-[#6b6560] uppercase tracking-wider mb-0.5">Appeal Reason</p>
            <p className="text-xs text-[#6b6560] italic leading-relaxed">&ldquo;{appeal.appealReason}&rdquo;</p>
          </div>
        </div>

        {/* Meta */}
        <div className="flex flex-wrap gap-4 text-[11px] text-[#6b6560]">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> Started {timeAgo(appeal.createdAt)}
          </span>
          <span className="flex items-center gap-1">
            <span className="font-medium text-[#1a1a1a]">{roundCount}</span> round{roundCount !== 1 ? "s" : ""} total
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> Total {(totalMs / 1000).toFixed(1)}s
          </span>
          <span className="flex items-center gap-1 font-mono">
            <Hash className="h-3 w-3" /> {formatAddress(appeal.id, 10)}
          </span>
        </div>
      </div>

      {/* Round cards */}
      <div>
        <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-3">Round Breakdown</p>
        <div className="space-y-3">
          {appeal.rounds.map((round, i) => (
            <AppealRoundCard
              key={round.roundNumber}
              round={round}
              index={i}
              isLatest={i === appeal.rounds.length - 1}
            />
          ))}
        </div>
      </div>

      {/* Educational callout */}
      {appealRounds.length > 0 && (
        <div className="rounded-xl border border-purple-200 bg-purple-50/60 p-4">
          <p className="text-xs font-semibold text-purple-800 mb-1.5">
            How GenLayer Appeals Work
          </p>
          <p className="text-xs text-purple-700 leading-relaxed">
            When the Equivalence Principle fails (less than 60% agreement), an appeal adds{" "}
            <strong>3 additional validators</strong> per round. The expanded set re-evaluates the claim
            from scratch, and their votes are pooled with the originals. This continues until consensus
            is reached or the case is escalated. This appeal expanded the validator set from{" "}
            <strong>{appeal.rounds[0]?.validatorCount}</strong> to{" "}
            <strong>{appeal.rounds[appeal.rounds.length - 1]?.validatorCount}</strong> validators.
          </p>
        </div>
      )}
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Live Appeal Simulator (run a new appeal from the Arena)
# ─────────────────────────────────────────────────────────────────────────────
w("components/appeals/LiveAppealRunner.tsx", '''\
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
          isOriginal: v.round === undefined ? true : !v.name.includes(" II"),
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
''')

# ─────────────────────────────────────────────────────────────────────────────
# 8. Appeals Stats Bar
# ─────────────────────────────────────────────────────────────────────────────
w("components/appeals/AppealStats.tsx", '''\
"use client";

import { Scale, CheckCircle2, XCircle, TrendingUp } from "lucide-react";
import type { AppealRecord } from "@/store/appealStore";

interface AppealStatsProps {
  appeals: AppealRecord[];
}

export function AppealStats({ appeals }: AppealStatsProps) {
  const total     = appeals.length;
  const resolved  = appeals.filter((a) => a.finalOutcome !== null);
  const accepted  = resolved.filter((a) => a.finalOutcome === "ACCEPTED").length;
  const rejected  = resolved.filter((a) => a.finalOutcome === "REJECTED").length;
  const avgRounds = total > 0
    ? (appeals.reduce((s, a) => s + a.rounds.length, 0) / total).toFixed(1)
    : "—";

  const stats = [
    { icon: Scale,        label: "Total Appeals",     value: `${total}`,       sub: `${resolved.length} resolved` },
    { icon: CheckCircle2, label: "Resolved: Accept",  value: accepted > 0 ? `${accepted}` : "—", sub: "overturned to accept" },
    { icon: XCircle,      label: "Resolved: Reject",  value: rejected > 0 ? `${rejected}` : "—", sub: "confirmed rejection" },
    { icon: TrendingUp,   label: "Avg Rounds",        value: avgRounds,        sub: "per appeal" },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      {stats.map((s) => (
        <div key={s.label} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
          <div className="flex items-center gap-2 mb-2">
            <s.icon className="h-4 w-4 text-[#6b6560]" />
            <span className="text-xs text-[#6b6560]">{s.label}</span>
          </div>
          <p className="text-xl font-bold text-[#1a1a1a] leading-tight">{s.value}</p>
          <p className="text-[10px] text-[#6b6560] mt-0.5">{s.sub}</p>
        </div>
      ))}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 9. Appeals Arena Page
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/appeals/page.tsx", '''\
"use client";

import { useAppealStore } from "@/store/appealStore";
import { AppealStats } from "@/components/appeals/AppealStats";
import { AppealHistory } from "@/components/appeals/AppealHistory";
import { AppealDetail } from "@/components/appeals/AppealDetail";
import { LiveAppealRunner } from "@/components/appeals/LiveAppealRunner";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function AppealsPage() {
  const { appeals, activeAppealId, setActiveAppeal, clearAppeals } = useAppealStore();
  const activeAppeal = appeals.find((a) => a.id === activeAppealId) ?? null;

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">Appeals Arena</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            When GenLayer validators can&apos;t reach consensus, an appeal is triggered. The validator
            set expands, new evaluators weigh in, and the Equivalence Principle is re-applied across
            the full pool. Explore past appeals or run a live appeal simulation.
          </p>
        </div>

        <AppealStats appeals={appeals} />

        <Tabs defaultValue="simulate">
          <TabsList className="mb-6">
            <TabsTrigger value="simulate">Live Simulation</TabsTrigger>
            <TabsTrigger value="history">
              Appeal History
              {appeals.length > 0 && (
                <span className="ml-1.5 h-4 min-w-4 rounded-full bg-[#2d2a26] text-[#efece4] text-[9px] flex items-center justify-center px-1">
                  {appeals.length}
                </span>
              )}
            </TabsTrigger>
            {activeAppeal && (
              <TabsTrigger value="detail">Case Detail</TabsTrigger>
            )}
          </TabsList>

          {/* ── Live simulation ── */}
          <TabsContent value="simulate">
            <div className="max-w-2xl">
              <LiveAppealRunner />
            </div>
          </TabsContent>

          {/* ── History ── */}
          <TabsContent value="history">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AppealHistory
                appeals={appeals}
                activeId={activeAppealId}
                onSelect={setActiveAppeal}
                onClear={clearAppeals}
              />
              {activeAppeal && (
                <AppealDetail appeal={activeAppeal} />
              )}
            </div>
          </TabsContent>

          {/* ── Case detail ── */}
          {activeAppeal && (
            <TabsContent value="detail">
              <div className="max-w-2xl">
                <AppealDetail appeal={activeAppeal} />
              </div>
            </TabsContent>
          )}
        </Tabs>

        {/* Educational callout */}
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            {
              title: "Why Appeals Exist",
              body: "Subjective claims don't always have a clear right answer. When validators genuinely disagree, an appeal adds more perspectives rather than forcing a premature consensus.",
            },
            {
              title: "Validator Expansion",
              body: "Each appeal round adds 3 more validators. Their votes are pooled with all previous rounds. The Equivalence Principle is applied across the full pool each time.",
            },
            {
              title: "Finality Window",
              body: "Once consensus is reached — even after multiple rounds — a finality window opens. The outcome is committed to the GenLayer state tree after this window expires.",
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
# 10. Wire appeals: update playground to auto-register appeal in store
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/playground/page.tsx", '''\
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
''')

print("\nPhase 6 setup complete. All files written.\n")
