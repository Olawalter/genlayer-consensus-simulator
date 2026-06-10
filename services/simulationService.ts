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
