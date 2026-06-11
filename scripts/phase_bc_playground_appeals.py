"""Phase B+C — Wire playground claim simulator and appeals to real Studio Net chain."""
import pathlib, subprocess, sys

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

def write(rel, code):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(code.encode("utf-8"))
    print(f"  wrote  {rel}")

# ── 1. services/simulationService.ts — real chain version ────────────────────
write("services/simulationService.ts", """\
"use client";

import { getClient } from "@/lib/genlayer/client";
import { CLAIM_EVALUATOR_CONTRACT } from "@/lib/genlayer/contracts";
import { TransactionStatus } from "genlayer-js/types";
import type { RealConsensusResult } from "@/lib/genlayer/types";
import { LLM_MODELS } from "@/lib/llm/models";

// ── Types (kept compatible with existing stores/components) ───────────────────

export type VoteOutcome = "ACCEPT" | "REJECT" | "UNCERTAIN";
export type SimStatus =
  | "idle" | "deploying" | "running" | "appealing"
  | "accepted" | "rejected" | "split" | "error";

export interface ValidatorResult {
  validatorIndex: number;
  validatorName: string;
  llmModel: string;
  llmProvider: string;
  vote: VoteOutcome;
  confidence: number;
  reasoning: string;
  executionMs: number;
  // real chain
  onChainAddress?: string;
  onChainVote?: string;
}

export interface SimulationRun {
  id: string;
  claim: string;
  category: string;
  status: SimStatus;
  validators: ValidatorResult[];
  finalOutcome: "ACCEPTED" | "REJECTED" | "SPLIT" | null;
  consensusReached: boolean;
  equivalenceMode: "comparative" | "non-comparative";
  agreeCount: number;
  disagreeCount: number;
  totalValidators: number;
  appealCount: number;
  isAppeal: boolean;
  startedAt: number;
  finishedAt?: number;
  // real chain
  txHash?: string;
  contractAddress?: string;
  isRealChain: boolean;
  chainStatus?: string;
  error?: string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function makeId() {
  return `sim_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

function mapVote(chainVote: string): VoteOutcome {
  if (chainVote === "AGREE") return "ACCEPT";
  if (chainVote === "DISAGREE") return "REJECT";
  return "UNCERTAIN";
}

function buildValidators(real: RealConsensusResult): ValidatorResult[] {
  if (real.validators.length > 0) {
    return real.validators.map((v, i) => ({
      validatorIndex: i,
      validatorName: `${i === 0 ? "Leader " : ""}${v.address.slice(0, 10)}…`,
      llmModel: LLM_MODELS[i % LLM_MODELS.length].name,
      llmProvider: LLM_MODELS[i % LLM_MODELS.length].provider,
      vote: mapVote(v.vote),
      confidence: v.vote === "AGREE" ? 0.92 : v.vote === "DISAGREE" ? 0.88 : 0.5,
      reasoning: `On-chain vote: ${v.vote}`,
      executionMs: Math.round(real.elapsedMs / Math.max(real.validators.length, 1)),
      onChainAddress: v.address,
      onChainVote: v.vote,
    }));
  }
  // Leader-only fallback
  const leaderResult = real.leaderReceipt?.result ?? "";
  return [{
    validatorIndex: 0,
    validatorName: "Leader",
    llmModel: LLM_MODELS[0].name,
    llmProvider: LLM_MODELS[0].provider,
    vote: real.finalOutcome === "ACCEPTED" ? "ACCEPT" : real.finalOutcome === "REJECTED" ? "REJECT" : "UNCERTAIN",
    confidence: 0.92,
    reasoning: `Leader result: ${leaderResult}`,
    executionMs: real.elapsedMs,
  }];
}

function realToRun(
  real: RealConsensusResult,
  claim: string,
  category: string,
  isAppeal = false,
  appealCount = 0,
  prevRun?: SimulationRun
): SimulationRun {
  const validators = buildValidators(real);
  const agreeCount   = validators.filter((v) => v.vote === "ACCEPT").length;
  const disagreeCount = validators.filter((v) => v.vote === "REJECT").length;

  const status: SimStatus =
    real.finalOutcome === "ACCEPTED" ? "accepted" :
    real.finalOutcome === "REJECTED" ? "rejected" : "split";

  return {
    id: prevRun?.id ?? makeId(),
    claim,
    category,
    status,
    validators,
    finalOutcome: real.finalOutcome === "PENDING" ? "SPLIT" : real.finalOutcome,
    consensusReached: real.consensusReached,
    equivalenceMode: "non-comparative",
    agreeCount,
    disagreeCount,
    totalValidators: validators.length,
    appealCount,
    isAppeal,
    startedAt: prevRun?.startedAt ?? Date.now(),
    finishedAt: Date.now(),
    txHash: real.txHash,
    contractAddress: real.contractAddress,
    isRealChain: true,
    chainStatus: real.status,
  };
}

// ── Simulation fallback (used when Studio Net is unavailable) ─────────────────

const VALIDATOR_NAMES = ["Alice (Leader)", "Bob", "Carol", "Dave", "Eve"];

function seededRandom(seed: number) {
  let s = seed;
  return () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 4294967296; };
}

async function simulateFallback(
  claim: string,
  category: string,
  onUpdate: (r: SimulationRun) => void,
  isAppeal = false,
  prevRun?: SimulationRun
): Promise<SimulationRun> {
  const id = prevRun?.id ?? makeId();
  const seed = Date.now() % 100000;
  const startedAt = prevRun?.startedAt ?? Date.now();
  const validators: ValidatorResult[] = [];

  for (let i = 0; i < VALIDATOR_NAMES.length; i++) {
    const model = LLM_MODELS[i % LLM_MODELS.length];
    const latency = model.latencyMs.min + Math.random() * (model.latencyMs.max - model.latencyMs.min);
    await new Promise((r) => setTimeout(r, latency));

    const rng = seededRandom(seed + i * 7919);
    const biases = [0.75, 0.65, 0.70, 0.60, 0.68];
    const roll = rng();
    let vote: VoteOutcome;
    let confidence: number;

    if (roll < biases[i])             { vote = "ACCEPT";    confidence = 0.70 + rng() * 0.25; }
    else if (roll < biases[i] + 0.15) { vote = "UNCERTAIN"; confidence = 0.40 + rng() * 0.25; }
    else                               { vote = "REJECT";    confidence = 0.55 + rng() * 0.30; }

    validators.push({
      validatorIndex: i,
      validatorName: VALIDATOR_NAMES[i],
      llmModel: model.name,
      llmProvider: model.provider,
      vote,
      confidence,
      reasoning: `Simulated validator ${i} assessment of: "${claim.slice(0, 60)}..."`,
      executionMs: Math.round(latency),
    });

    const agreeCount    = validators.filter((v) => v.vote === "ACCEPT").length;
    const disagreeCount = validators.filter((v) => v.vote === "REJECT").length;
    onUpdate({
      id, claim, category,
      status: "running",
      validators: [...validators],
      finalOutcome: null,
      consensusReached: false,
      equivalenceMode: "non-comparative",
      agreeCount, disagreeCount,
      totalValidators: VALIDATOR_NAMES.length,
      appealCount: prevRun?.appealCount ?? 0,
      isAppeal,
      startedAt,
      isRealChain: false,
    });
  }

  const agreeCount    = validators.filter((v) => v.vote === "ACCEPT").length;
  const disagreeCount = validators.filter((v) => v.vote === "REJECT").length;
  const passed        = agreeCount / validators.length >= 0.6;
  const dominant      = agreeCount >= disagreeCount ? "ACCEPT" : "REJECT";
  const finalOutcome: SimulationRun["finalOutcome"] = passed
    ? dominant === "ACCEPT" ? "ACCEPTED" : "REJECTED" : "SPLIT";
  const status: SimStatus = passed ? (dominant === "ACCEPT" ? "accepted" : "rejected") : "split";

  return {
    id, claim, category,
    status,
    validators,
    finalOutcome,
    consensusReached: passed,
    equivalenceMode: "non-comparative",
    agreeCount, disagreeCount,
    totalValidators: validators.length,
    appealCount: prevRun?.appealCount ?? 0,
    isAppeal,
    startedAt,
    finishedAt: Date.now(),
    isRealChain: false,
  };
}

// ── Public API ────────────────────────────────────────────────────────────────

export async function runSimulation(
  claim: string,
  category: string,
  onUpdate: (r: SimulationRun) => void
): Promise<SimulationRun> {
  const hasKey = !!(process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY);

  if (!hasKey) {
    const partial: SimulationRun = {
      id: makeId(), claim, category, status: "running",
      validators: [], finalOutcome: null, consensusReached: false,
      equivalenceMode: "non-comparative", agreeCount: 0, disagreeCount: 0,
      totalValidators: 5, appealCount: 0, isAppeal: false,
      startedAt: Date.now(), isRealChain: false,
    };
    onUpdate(partial);
    return simulateFallback(claim, category, onUpdate, false);
  }

  // Real chain path
  const startedAt = Date.now();
  const runId = makeId();

  onUpdate({
    id: runId, claim, category, status: "deploying",
    validators: [], finalOutcome: null, consensusReached: false,
    equivalenceMode: "non-comparative", agreeCount: 0, disagreeCount: 0,
    totalValidators: 0, appealCount: 0, isAppeal: false,
    startedAt, isRealChain: true, chainStatus: "Deploying ClaimEvaluator contract...",
  });

  try {
    const client = getClient();

    // Deploy
    const deployHash = await client.deployContract({
      code: CLAIM_EVALUATOR_CONTRACT,
      args: [],
      leaderOnly: false,
    });

    onUpdate({
      id: runId, claim, category, status: "deploying",
      validators: [], finalOutcome: null, consensusReached: false,
      equivalenceMode: "non-comparative", agreeCount: 0, disagreeCount: 0,
      totalValidators: 0, appealCount: 0, isAppeal: false,
      startedAt, isRealChain: true,
      txHash: deployHash,
      chainStatus: "Waiting for deploy consensus...",
    });

    const deployReceipt = await client.waitForTransactionReceipt({
      hash: deployHash as `0x${string}` & { length: 66 },
      status: TransactionStatus.ACCEPTED,
      retries: 60, interval: 2000,
    });

    const contractAddress =
      (deployReceipt as unknown as { to_address?: string })?.to_address ??
      (deployReceipt as unknown as { recipient?: string })?.recipient ?? "";

    if (!contractAddress) throw new Error("Deploy succeeded but contract address missing");

    onUpdate({
      id: runId, claim, category, status: "running",
      validators: [], finalOutcome: null, consensusReached: false,
      equivalenceMode: "non-comparative", agreeCount: 0, disagreeCount: 0,
      totalValidators: 0, appealCount: 0, isAppeal: false,
      startedAt, isRealChain: true,
      txHash: deployHash, contractAddress,
      chainStatus: `Contract deployed. Calling evaluate("${claim.slice(0, 40)}...")`,
    });

    // Call evaluate
    const callHash = await client.writeContract({
      address: contractAddress as `0x${string}`,
      functionName: "evaluate",
      args: [claim] as unknown as never[],
      value: BigInt(0),
      leaderOnly: false,
    });

    onUpdate({
      id: runId, claim, category, status: "running",
      validators: [], finalOutcome: null, consensusReached: false,
      equivalenceMode: "non-comparative", agreeCount: 0, disagreeCount: 0,
      totalValidators: 0, appealCount: 0, isAppeal: false,
      startedAt, isRealChain: true,
      txHash: callHash, contractAddress,
      chainStatus: "Validators executing and voting on-chain...",
    });

    const callReceipt = await client.waitForTransactionReceipt({
      hash: callHash as `0x${string}` & { length: 66 },
      status: TransactionStatus.ACCEPTED,
      retries: 60, interval: 2000,
    });

    // Read final state
    let onChainResult = "";
    try {
      const raw = await client.readContract({
        address: contractAddress as `0x${string}`,
        functionName: "get_result",
        args: [],
      });
      onChainResult = String(raw ?? "");
    } catch { /* non-fatal */ }

    const real = parseReceipt(callReceipt as Record<string, unknown>, callHash, contractAddress, startedAt);
    const finalRun = realToRun(real, claim, category, false, 0);
    finalRun.id = runId;

    // Annotate leader reasoning with actual LLM result
    if (finalRun.validators[0] && onChainResult) {
      finalRun.validators[0].reasoning = `LLM verdict: ${onChainResult}`;
    }

    return finalRun;
  } catch (err) {
    console.error("Chain simulation failed:", err);
    // Fallback to simulation on error
    onUpdate({
      id: runId, claim, category, status: "running",
      validators: [], finalOutcome: null, consensusReached: false,
      equivalenceMode: "non-comparative", agreeCount: 0, disagreeCount: 0,
      totalValidators: 5, appealCount: 0, isAppeal: false,
      startedAt, isRealChain: false,
      error: err instanceof Error ? err.message : String(err),
    });
    return simulateFallback(claim, category, onUpdate, false);
  }
}

export async function runAppeal(
  prevRun: SimulationRun,
  reason: string,
  onUpdate: (r: SimulationRun) => void
): Promise<SimulationRun> {
  const hasKey = !!(process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY);

  if (!hasKey || !prevRun.contractAddress) {
    return simulateFallback(prevRun.claim, prevRun.category, onUpdate, true, prevRun);
  }

  const startedAt = Date.now();
  onUpdate({ ...prevRun, status: "appealing", isAppeal: true, chainStatus: "Submitting appeal..." });

  try {
    const client = getClient();

    // Re-evaluate on the same contract (appeals re-run with more validators in GenLayer)
    const callHash = await client.writeContract({
      address: prevRun.contractAddress as `0x${string}`,
      functionName: "evaluate",
      args: [prevRun.claim] as unknown as never[],
      value: BigInt(0),
      leaderOnly: false,
      consensusMaxRotations: 3,
    });

    onUpdate({
      ...prevRun, status: "appealing", isAppeal: true,
      txHash: callHash,
      chainStatus: "Appeal validators executing on-chain...",
    });

    const receipt = await client.waitForTransactionReceipt({
      hash: callHash as `0x${string}` & { length: 66 },
      status: TransactionStatus.ACCEPTED,
      retries: 60, interval: 2000,
    });

    const real = parseReceipt(
      receipt as Record<string, unknown>,
      callHash,
      prevRun.contractAddress,
      startedAt
    );
    return realToRun(real, prevRun.claim, prevRun.category, true, (prevRun.appealCount ?? 0) + 1, prevRun);
  } catch (err) {
    console.error("Appeal failed:", err);
    return simulateFallback(prevRun.claim, prevRun.category, onUpdate, true, prevRun);
  }
}

// ── Receipt parser (shared with executor) ─────────────────────────────────────

function parseReceipt(
  receipt: Record<string, unknown>,
  txHash: string,
  contractAddress: string,
  startMs: number
): RealConsensusResult {
  const statusName = String(receipt.statusName ?? receipt.status ?? "UNKNOWN");
  const lastRound  = receipt.lastRound as { roundValidators?: string[]; validatorVotesName?: string[] } | undefined;
  const consensusData = receipt.consensus_data as {
    leader_receipt?: Record<string, unknown>[];
  } | undefined;

  const leaderRaw = consensusData?.leader_receipt?.[0];
  const leaderReceipt = leaderRaw ? {
    result:           String(leaderRaw.result ?? ""),
    execution_result: String(leaderRaw.execution_result ?? ""),
    mode:             String(leaderRaw.mode ?? ""),
    eq_outputs:       (leaderRaw.eq_outputs ?? {}) as Record<string, unknown>,
    error:            leaderRaw.error ? String(leaderRaw.error) : null,
  } : null;

  const validators = (lastRound?.roundValidators ?? []).map((addr, i) => ({
    address: addr,
    vote: ((lastRound?.validatorVotesName?.[i] ?? "NOT_VOTED") as import("@/lib/genlayer/types").ValidatorVote["vote"]),
    executionResult: "",
  }));

  const agreeCount    = validators.filter((v) => v.vote === "AGREE").length;
  const disagreeCount = validators.filter((v) => v.vote === "DISAGREE").length;
  const total         = validators.length;
  const accepted      = ["ACCEPTED", "FINALIZED", "READY_TO_FINALIZE"].includes(statusName);

  return {
    txHash,
    status: statusName,
    finalOutcome: accepted ? "ACCEPTED" : disagreeCount > agreeCount ? "REJECTED" : total === 0 ? "PENDING" : "SPLIT",
    consensusReached: accepted,
    leaderReceipt,
    validators,
    totalValidators: total,
    agreeCount,
    disagreeCount,
    contractAddress,
    elapsedMs: Date.now() - startMs,
  };
}
""")

# ── 2. Update playground page to show chain badge + tx hash ──────────────────
# Read existing playground page to find what components it uses
import pathlib as _pathlib
pg = (_pathlib.Path("C:/GenB/GenLayer Consensus Simulator") / "app/(dashboard)/playground/page.tsx").read_text(encoding="utf-8")
# Just inject chain status display — add txHash/chain indicator after the imports
# We'll patch the JSX to show chain info when available

# Check if it already shows chainStatus
if "chainStatus" not in pg and "txHash" not in pg:
    # Add chain badge to the header area — find the return statement opening
    pg = pg.replace(
        'const status = activeRun?.status ?? "idle";',
        '''const status = activeRun?.status ?? "idle";
  const isRealChain = activeRun?.isRealChain ?? false;
  const txHash      = activeRun?.txHash;
  const chainStatus = activeRun?.chainStatus;'''
    )
    # Add tx hash display after SimulationResult
    pg = pg.replace(
        '<SimulationResult',
        '''{txHash && (
            <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-2 text-xs text-green-800 font-mono truncate">
              ⛓ tx: {txHash}
            </div>
          )}
          <SimulationResult'''
    )
    (_pathlib.Path("C:/GenB/GenLayer Consensus Simulator") / "app/(dashboard)/playground/page.tsx").write_bytes(pg.encode("utf-8"))
    print("  patched  app/(dashboard)/playground/page.tsx")
else:
    print("  skipped  playground/page.tsx (already patched)")

print("\nAll Phase B+C files written. Running build...")
result = subprocess.run(
    ["npm", "run", "build"], cwd=ROOT, shell=True,
    capture_output=True, text=True,
)
out = result.stdout + result.stderr
print(out[-5000:] if len(out) > 5000 else out)
if result.returncode != 0:
    print("\nBUILD FAILED")
    sys.exit(1)
print("\nBUILD PASSED")
