"""Write the real simulationService.ts — keeps original LiveValidator types, adds real chain."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

code = r'''
"use client";

import { VALIDATOR_PERSONAS } from "@/lib/validators/personas";
import { computeEquivalence } from "@/lib/validators/equivalence";
import { sleep } from "@/lib/utils";
import type { ValidatorVote } from "@/types/validator";
import { getClient } from "@/lib/genlayer/client";
import { CLAIM_EVALUATOR_CONTRACT } from "@/lib/genlayer/contracts";
import { TransactionStatus } from "genlayer-js/types";

// ── Types ─────────────────────────────────────────────────────────────────────

export type SimulationStatus =
  | "idle" | "submitting" | "running" | "computing"
  | "accepted" | "rejected" | "appeal_triggered" | "appealing" | "finalized";

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
  // real chain extras
  onChainAddress?: string;
  onChainVote?: string;
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
  // real chain
  isRealChain?: boolean;
  contractAddress?: string;
  chainStatus?: string;
}

// ── Reasoning generators ──────────────────────────────────────────────────────

const REASONING_TEMPLATES: Record<string, (claim: string, vote: string) => string> = {
  analytical: (claim, vote) => {
    if (vote === "ACCEPT") return `After systematic evaluation of "${claim.slice(0, 60)}...", the objective indicators align with acceptance criteria. The claim contains verifiable elements and no contradictory evidence was identified.`;
    if (vote === "REJECT") return `Evaluating "${claim.slice(0, 60)}..." against measurable criteria reveals insufficient evidence. The claim lacks quantifiable specificity required for confident acceptance.`;
    return `The claim "${claim.slice(0, 60)}..." presents mixed signals under analytical review. Ambiguity in key variables prevents a definitive determination.`;
  },
  contextual: (claim, vote) => {
    if (vote === "ACCEPT") return `Reading "${claim.slice(0, 60)}..." in context, the intent and broader circumstances support acceptance. The spirit of the claim appears genuine and consistent with reasonable expectations.`;
    if (vote === "REJECT") return `Contextually, "${claim.slice(0, 60)}..." raises concerns. The framing suggests this claim may not reflect the full picture, leading to rejection after careful consideration.`;
    return `The context around "${claim.slice(0, 60)}..." is genuinely ambiguous. Multiple interpretations are plausible, and I cannot confidently favour one outcome.`;
  },
  strict: (claim, vote) => {
    if (vote === "ACCEPT") return `"${claim.slice(0, 60)}..." meets the required threshold of evidence. Only after rigorous scrutiny and finding no logical inconsistencies do I issue this acceptance.`;
    if (vote === "REJECT") return `The claim "${claim.slice(0, 60)}..." fails strict verification. The evidentiary bar has not been met. Substantially stronger supporting facts are required.`;
    return `Under strict evaluation, "${claim.slice(0, 60)}..." remains unresolved. The evidence is borderline and strict standards prohibit acceptance without stronger confirmation.`;
  },
  lenient: (claim, vote) => {
    if (vote === "ACCEPT") return `"${claim.slice(0, 60)}..." appears credible and plausible. Giving appropriate benefit of the doubt, the claim aligns with what one would reasonably expect.`;
    if (vote === "REJECT") return `Even with a charitable interpretation, "${claim.slice(0, 60)}..." presents too many red flags to accept. The claim's core premise is difficult to reconcile with known patterns.`;
    return `"${claim.slice(0, 60)}..." is on the fence. While I lean toward giving benefit of the doubt, some aspects give me pause, warranting an uncertain verdict.`;
  },
  balanced: (claim, vote) => {
    if (vote === "ACCEPT") return `Weighing all available evidence for "${claim.slice(0, 60)}...", the balance of probability favours acceptance. Supporting factors outweigh concerns when assessed proportionally.`;
    if (vote === "REJECT") return `A balanced assessment of "${claim.slice(0, 60)}..." tips toward rejection. While there are arguments on both sides, the weight of evidence against acceptance is marginally stronger.`;
    return `"${claim.slice(0, 60)}..." presents a genuine 50/50 scenario. Evidence for and against acceptance is approximately equal, warranting an uncertain verdict.`;
  },
};

function generateVote(
  persona: (typeof VALIDATOR_PERSONAS)[0],
  claim: string
): { vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number; reasoning: string } {
  const hash = Array.from(claim + persona.name).reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = ((hash * 9301 + 49297) % 233280) / 233280;
  const uncertainty = persona.uncertaintyRange;
  const threshold = persona.acceptThreshold;
  let vote: "ACCEPT" | "REJECT" | "UNCERTAIN";
  let confidence: number;

  if (rand > threshold + uncertainty / 2)       { vote = "ACCEPT";    confidence = persona.confidenceBase + (rand - threshold) * 0.2; }
  else if (rand < threshold - uncertainty / 2)  { vote = "REJECT";    confidence = persona.confidenceBase + (threshold - rand) * 0.2; }
  else                                           { vote = "UNCERTAIN"; confidence = persona.confidenceBase * 0.7; }

  confidence = Math.min(0.99, Math.max(0.51, confidence));
  const reasoning = REASONING_TEMPLATES[persona.reasoningStyle]?.(claim, vote) ?? REASONING_TEMPLATES.balanced(claim, vote);
  return { vote, confidence, reasoning };
}

// ── Receipt parser ────────────────────────────────────────────────────────────

function parseChainReceipt(receipt: Record<string, unknown>) {
  const statusName = String(receipt.statusName ?? receipt.status ?? "UNKNOWN");
  const lastRound = receipt.lastRound as { roundValidators?: string[]; validatorVotesName?: string[] } | undefined;
  const validators = (lastRound?.roundValidators ?? []).map((addr, i) => ({
    address: addr,
    vote: (lastRound?.validatorVotesName?.[i] ?? "NOT_VOTED") as string,
  }));
  const accepted = ["ACCEPTED", "FINALIZED", "READY_TO_FINALIZE"].includes(statusName);
  const agreeCount = validators.filter((v) => v.vote === "AGREE").length;
  const disagreeCount = validators.filter((v) => v.vote === "DISAGREE").length;
  return { statusName, validators, accepted, agreeCount, disagreeCount };
}

function mapChainVoteToLive(
  chainVote: string,
  claim: string,
  persona: (typeof VALIDATOR_PERSONAS)[0]
): { vote: "ACCEPT" | "REJECT" | "UNCERTAIN"; confidence: number; reasoning: string } {
  const vote: "ACCEPT" | "REJECT" | "UNCERTAIN" =
    chainVote === "AGREE" ? "ACCEPT" : chainVote === "DISAGREE" ? "REJECT" : "UNCERTAIN";
  const confidence = chainVote === "AGREE" ? 0.92 : chainVote === "DISAGREE" ? 0.88 : 0.55;
  const reasoning = REASONING_TEMPLATES[persona.reasoningStyle]?.(claim, vote) ?? REASONING_TEMPLATES.balanced(claim, vote);
  return { vote, confidence, reasoning };
}

// ── Simulation (original logic) ───────────────────────────────────────────────

async function runSimulated(
  claim: string,
  category: string,
  onUpdate: (run: SimulationRun) => void,
  prevRun?: SimulationRun
): Promise<SimulationRun> {
  const runId   = prevRun?.id ?? `sim_${Date.now()}`;
  const claimId = prevRun?.claimId ?? `claim_${Date.now()}`;
  const round   = prevRun ? prevRun.round + 1 : 1;

  const validators: LiveValidator[] = VALIDATOR_PERSONAS.map((p, i) => ({
    id: `v_${round}_${i}`,
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
    id: runId, claimId, claim, category,
    status: "submitting", validators,
    consensusResult: null, txHash: null, round,
    startedAt: prevRun?.startedAt ?? Date.now(),
    isRealChain: false,
  };

  onUpdate({ ...run });
  await sleep(600);
  run.status = "running";
  run.validators = run.validators.map((v) => v.isLeader ? { ...v, status: "thinking" } : v);
  onUpdate({ ...run });

  await sleep(run.validators[0].thinkingMs);
  const leaderResult = generateVote(VALIDATOR_PERSONAS[0], claim);
  run.validators = run.validators.map((v) => v.isLeader ? { ...v, status: "voted", ...leaderResult } : v);
  onUpdate({ ...run });

  for (let i = 1; i < VALIDATOR_PERSONAS.length; i++) {
    await sleep(300);
    run.validators = run.validators.map((v, idx) => idx === i ? { ...v, status: "thinking" } : v);
    onUpdate({ ...run });
    await sleep(run.validators[i].thinkingMs);
    const result = generateVote(VALIDATOR_PERSONAS[i], claim);
    run.validators = run.validators.map((v, idx) => idx === i ? { ...v, status: "voted", ...result } : v);
    onUpdate({ ...run });
  }

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
  run.txHash = `0x${Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join("")}`;
  run.status = consensusResult.outcome === "ACCEPTED" ? "accepted"
    : consensusResult.outcome === "REJECTED" ? "rejected"
    : "appeal_triggered";

  onUpdate({ ...run });
  return run;
}

// ── Real chain runner ─────────────────────────────────────────────────────────

async function runOnChain(
  claim: string,
  category: string,
  onUpdate: (run: SimulationRun) => void,
  prevRun?: SimulationRun,
  isAppeal = false,
  existingContractAddress?: string
): Promise<SimulationRun> {
  const runId   = prevRun?.id ?? `sim_${Date.now()}`;
  const claimId = prevRun?.claimId ?? `claim_${Date.now()}`;
  const round   = prevRun ? prevRun.round + 1 : 1;
  const startedAt = prevRun?.startedAt ?? Date.now();

  // Initial validators — show as waiting while chain executes
  const initialValidators: LiveValidator[] = VALIDATOR_PERSONAS.map((p, i) => ({
    id: `v_${round}_${i}`,
    name: p.name, model: p.model, persona: p.persona,
    color: p.color, avatar: p.avatar, description: p.description,
    status: "waiting", vote: null, confidence: null, reasoning: null,
    isLeader: i === 0, thinkingMs: 2000,
  }));

  const run: SimulationRun = {
    id: runId, claimId, claim, category,
    status: isAppeal ? "appealing" : "submitting",
    validators: initialValidators,
    consensusResult: null, txHash: null, round,
    startedAt, isRealChain: true,
    chainStatus: isAppeal ? "Submitting appeal to Studio Net..." : "Deploying ClaimEvaluator to Studio Net...",
  };

  onUpdate({ ...run });

  try {
    const client = getClient();
    let contractAddress = existingContractAddress;

    // Deploy only if no existing contract
    if (!contractAddress) {
      const deployHash = await client.deployContract({
        code: CLAIM_EVALUATOR_CONTRACT,
        args: [], leaderOnly: false,
      });

      run.txHash = deployHash;
      run.chainStatus = "Waiting for deploy consensus...";
      // Show validators as "thinking" during deploy
      run.validators = run.validators.map((v) => ({ ...v, status: "thinking" }));
      onUpdate({ ...run });

      const deployReceipt = await client.waitForTransactionReceipt({
        hash: deployHash as `0x${string}` & { length: 66 },
        status: TransactionStatus.ACCEPTED,
        retries: 60, interval: 2000,
      });

      contractAddress =
        (deployReceipt as unknown as { to_address?: string })?.to_address ??
        (deployReceipt as unknown as { recipient?: string })?.recipient ?? "";

      if (!contractAddress) throw new Error("Contract address missing after deploy");
    }

    run.contractAddress = contractAddress;
    run.status = "running";
    run.chainStatus = `Calling evaluate("${claim.slice(0, 40)}...")`;
    onUpdate({ ...run });

    const callHash = await client.writeContract({
      address: contractAddress as `0x${string}`,
      functionName: "evaluate",
      args: [claim] as unknown as never[],
      value: BigInt(0),
      leaderOnly: false,
      ...(isAppeal ? { consensusMaxRotations: 3 } : {}),
    });

    run.txHash = callHash;
    run.chainStatus = "Validators executing on Studio Net...";
    onUpdate({ ...run });

    const receipt = await client.waitForTransactionReceipt({
      hash: callHash as `0x${string}` & { length: 66 },
      status: TransactionStatus.ACCEPTED,
      retries: 60, interval: 2000,
    });

    const { validators: chainVals, accepted, agreeCount, disagreeCount } =
      parseChainReceipt(receipt as Record<string, unknown>);

    // Map chain validators → LiveValidator (use personas for display)
    const liveValidators: LiveValidator[] = chainVals.length > 0
      ? chainVals.map((cv, i) => {
          const persona = VALIDATOR_PERSONAS[i % VALIDATOR_PERSONAS.length];
          const mapped  = mapChainVoteToLive(cv.vote, claim, persona);
          return {
            id: `v_${round}_${i}`,
            name: persona.name, model: persona.model, persona: persona.persona,
            color: persona.color, avatar: persona.avatar, description: persona.description,
            status: "voted" as const,
            ...mapped,
            isLeader: i === 0, thinkingMs: 0,
            onChainAddress: cv.address,
            onChainVote: cv.vote,
          };
        })
      : initialValidators.map((v, i) => {
          const persona = VALIDATOR_PERSONAS[i % VALIDATOR_PERSONAS.length];
          const defaultVote = accepted ? "ACCEPT" : "REJECT";
          return {
            ...v, status: "voted" as const,
            vote: defaultVote,
            confidence: 0.9,
            reasoning: REASONING_TEMPLATES[persona.reasoningStyle]?.(claim, defaultVote) ?? "",
          };
        });

    // Build consensus result
    const votes: ValidatorVote[] = liveValidators.map((v) => ({
      validatorId: v.id,
      simulationId: runId,
      role: v.isLeader ? "leader" : "validator",
      vote: v.vote!,
      confidence: v.confidence!,
      reasoning: v.reasoning!,
      equivalenceScore: 0,
    }));

    const consensusResult = computeEquivalence(votes);

    const finalStatus: SimulationStatus = accepted
      ? "accepted"
      : disagreeCount > agreeCount
      ? "rejected"
      : "appeal_triggered";

    const finalRun: SimulationRun = {
      ...run,
      status: finalStatus,
      validators: liveValidators,
      consensusResult,
      txHash: callHash,
      contractAddress,
      isRealChain: true,
      chainStatus: undefined,
    };

    onUpdate(finalRun);
    return finalRun;

  } catch (err) {
    console.error("Chain execution failed, falling back to simulation:", err);
    return runSimulated(claim, category, onUpdate, prevRun);
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

export async function runSimulation(
  claim: string,
  category: string,
  onUpdate: (run: SimulationRun) => void
): Promise<SimulationRun> {
  const hasKey = !!(process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY);
  if (hasKey) return runOnChain(claim, category, onUpdate);
  return runSimulated(claim, category, onUpdate);
}

export async function runAppeal(
  prevRun: SimulationRun,
  reason: string,
  onUpdate: (run: SimulationRun) => void
): Promise<SimulationRun> {
  const hasKey = !!(process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY);
  if (hasKey) {
    return runOnChain(
      prevRun.claim, prevRun.category, onUpdate,
      prevRun, true, prevRun.contractAddress
    );
  }

  // Simulated appeal — add 3 more validators
  const run = { ...prevRun, status: "appealing" as SimulationStatus, round: (prevRun.round ?? 1) + 1 };
  onUpdate({ ...run });
  await sleep(500);

  const appealValidators: LiveValidator[] = VALIDATOR_PERSONAS.slice(0, 3).map((p, i) => ({
    id: `appeal_v_${i}`,
    name: `${p.name} II`, model: p.model, persona: p.persona,
    color: p.color, avatar: p.avatar, description: "Appeal evaluator — re-assessing with fresh context.",
    status: "waiting" as const, vote: null, confidence: null, reasoning: null,
    isLeader: false, thinkingMs: 1000 + i * 500,
  }));

  run.validators = [
    ...run.validators.map((v) => ({ ...v, status: "voted" as const })),
    ...appealValidators,
  ];
  onUpdate({ ...run });

  for (let i = 0; i < appealValidators.length; i++) {
    await sleep(300);
    const absIdx = prevRun.validators.length + i;
    run.validators = run.validators.map((v, idx) => idx === absIdx ? { ...v, status: "thinking" } : v);
    onUpdate({ ...run });
    await sleep(appealValidators[i].thinkingMs);
    const result = generateVote(VALIDATOR_PERSONAS[i], prevRun.claim + reason);
    run.validators = run.validators.map((v, idx) => idx === absIdx ? { ...v, status: "voted", ...result } : v);
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
  run.status = newConsensus.outcome === "ACCEPTED" ? "accepted"
    : newConsensus.outcome === "REJECTED" ? "rejected" : "finalized";

  onUpdate({ ...run });
  return run;
}
'''

p = ROOT / "services/simulationService.ts"
p.write_bytes(code.strip().encode("utf-8"))
print("wrote services/simulationService.ts")
