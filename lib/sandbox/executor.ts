"use client";

import { LLM_MODELS } from "@/lib/llm/models";
import { parseContract, type ParsedContract } from "./parser";
import { executeOnChain, type OnProgress } from "@/lib/genlayer/executor";
import type { RealConsensusResult } from "@/lib/genlayer/types";

export type VoteOutcome = "ACCEPT" | "REJECT" | "UNCERTAIN";

export interface ValidatorExecution {
  validatorIndex: number;
  validatorName: string;
  llmModel: string;
  llmProvider: string;
  inputReceived: string;
  promptSent: string;
  llmResponse: string;
  vote: VoteOutcome;
  confidence: number;
  reasoning: string;
  executionMs: number;
  stateAfter: Record<string, string>;
  // real chain extras
  onChainAddress?: string;
  onChainVote?: string;
}

export interface EquivalenceResult {
  mode: "comparative" | "non-comparative";
  passed: boolean;
  agreeingCount: number;
  totalCount: number;
  threshold: number;
  dominantVote: VoteOutcome;
  explanation: string;
}

export interface SandboxExecutionResult {
  contractName: string;
  functionCalled: string;
  input: string;
  validators: ValidatorExecution[];
  equivalence: EquivalenceResult;
  finalOutcome: "ACCEPTED" | "REJECTED" | "SPLIT";
  consensusReached: boolean;
  totalMs: number;
  consoleLog: string[];
  parsedContract: ParsedContract;
  // real chain data
  realChain?: RealConsensusResult;
  isRealChain: boolean;
}

// ── Real-chain execution ──────────────────────────────────────────────────────

export async function executeSandboxContract(
  code: string,
  functionName: string,
  input: string,
  onProgress?: OnProgress
): Promise<SandboxExecutionResult> {
  const parsed = parseContract(code);
  const consoleLog: string[] = [];
  const startMs = Date.now();

  const privateKey = process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY;
  const useRealChain = !!privateKey && privateKey !== "PASTE_PRIVATE_KEY_HERE";

  if (useRealChain) {
    return executeReal(code, functionName, input, parsed, consoleLog, startMs, onProgress);
  }
  return executeSimulated(code, functionName, input, parsed, consoleLog, startMs);
}

// ── Real chain path ───────────────────────────────────────────────────────────

async function executeReal(
  code: string,
  functionName: string,
  input: string,
  parsed: ParsedContract,
  consoleLog: string[],
  startMs: number,
  onProgress?: OnProgress
): Promise<SandboxExecutionResult> {
  consoleLog.push(`[chain] Connecting to Studio Net...`);
  consoleLog.push(`[chain] Deploying contract: ${parsed.name || "Contract"}`);

  try {
    const result = await executeOnChain(
      code,
      functionName,
      [input],
      (status, detail) => {
        consoleLog.push(`[chain:${status}] ${detail ?? ""}`);
        onProgress?.(status, detail);
      }
    );

    // Map real chain validators to our display format
    const validators: ValidatorExecution[] = result.validators.length > 0
      ? result.validators.map((v, i) => {
          const model = LLM_MODELS[i % LLM_MODELS.length];
          const vote: VoteOutcome = v.vote === "AGREE" ? "ACCEPT"
            : v.vote === "DISAGREE" ? "REJECT"
            : "UNCERTAIN";
          return {
            validatorIndex: i,
            validatorName: `Validator ${i === 0 ? "(Leader) " : ""}${v.address.slice(0, 8)}...`,
            llmModel: model.name,
            llmProvider: model.provider,
            inputReceived: input,
            promptSent: `[on-chain] ${functionName}("${input}")`,
            llmResponse: v.vote,
            vote,
            confidence: v.vote === "AGREE" ? 0.9 : v.vote === "DISAGREE" ? 0.85 : 0.5,
            reasoning: `On-chain validator vote: ${v.vote}`,
            executionMs: Math.round(result.elapsedMs / Math.max(result.validators.length, 1)),
            stateAfter: {},
            onChainAddress: v.address,
            onChainVote: v.vote,
          };
        })
      : [{
          validatorIndex: 0,
          validatorName: "Leader",
          llmModel: LLM_MODELS[0].name,
          llmProvider: LLM_MODELS[0].provider,
          inputReceived: input,
          promptSent: `[on-chain] ${functionName}("${input}")`,
          llmResponse: result.leaderReceipt?.result ?? "",
          vote: result.finalOutcome === "ACCEPTED" ? "ACCEPT" : result.finalOutcome === "REJECTED" ? "REJECT" : "UNCERTAIN",
          confidence: 0.9,
          reasoning: result.leaderReceipt?.error ?? `Leader result: ${result.leaderReceipt?.result}`,
          executionMs: result.elapsedMs,
          stateAfter: {},
        }];

    const agreeingCount = validators.filter((v) => v.vote === "ACCEPT").length;
    const total = validators.length;
    const dominantVote: VoteOutcome = agreeingCount > total / 2 ? "ACCEPT" : "REJECT";
    const passed = result.finalOutcome === "ACCEPTED";

    const equivalence: EquivalenceResult = {
      mode: "non-comparative",
      passed,
      agreeingCount,
      totalCount: total,
      threshold: 0.6,
      dominantVote,
      explanation: passed
        ? `On-chain consensus ACCEPTED — tx ${result.txHash.slice(0, 18)}...`
        : `On-chain consensus: ${result.finalOutcome} — tx ${result.txHash.slice(0, 18)}...`,
    };

    consoleLog.push(`[consensus] Final: ${result.finalOutcome} | tx: ${result.txHash}`);

    return {
      contractName: parsed.name,
      functionCalled: functionName,
      input,
      validators,
      equivalence,
      finalOutcome: result.finalOutcome === "ACCEPTED" ? "ACCEPTED"
        : result.finalOutcome === "REJECTED" ? "REJECTED" : "SPLIT",
      consensusReached: passed,
      totalMs: Date.now() - startMs,
      consoleLog,
      parsedContract: parsed,
      realChain: result,
      isRealChain: true,
    };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    consoleLog.push(`[chain:error] ${msg}`);
    consoleLog.push(`[chain] Falling back to simulation...`);
    return executeSimulated(
      "", functionName, input, parsed, consoleLog, startMs
    );
  }
}

// ── Simulation fallback (original logic) ─────────────────────────────────────

const VALIDATOR_NAMES = ["Alice (Leader)", "Bob", "Carol", "Dave", "Eve"];

const REASONING_TEMPLATES: Record<string, string[]> = {
  YES: [
    "Based on my analysis of the provided information, the answer is clearly affirmative.",
    "My evaluation concludes this meets the specified criteria.",
    "After thorough consideration, I find sufficient evidence to answer in the affirmative.",
  ],
  NO: [
    "Upon careful evaluation, I cannot confirm the affirmative.",
    "My analysis indicates this does not meet the required criteria.",
    "After review, I find the evidence insufficient to support a YES determination.",
  ],
  UNCERTAIN: [
    "The information provided is ambiguous. I cannot make a definitive determination.",
    "My analysis reveals conflicting signals. Without additional context, I must classify this as uncertain.",
    "The available information is insufficient for a confident determination.",
  ],
};

function seededRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 4294967296;
  };
}

async function executeSimulated(
  _code: string,
  functionName: string,
  input: string,
  parsed: ParsedContract,
  consoleLog: string[],
  startMs: number
): Promise<SandboxExecutionResult> {
  const seed = Date.now() % 100000;

  consoleLog.push(`[sim] Parsing contract source...`);
  consoleLog.push(`[sim] Contract: ${parsed.name || "Unknown"}`);
  consoleLog.push(`[sim] Calling: ${functionName}("${input}")`);
  consoleLog.push(`[sim] Dispatching to ${VALIDATOR_NAMES.length} simulated validators...`);

  const validators: ValidatorExecution[] = [];

  for (let i = 0; i < VALIDATOR_NAMES.length; i++) {
    const model = LLM_MODELS[i % LLM_MODELS.length];
    const latency = model.latencyMs.min + Math.random() * (model.latencyMs.max - model.latencyMs.min);
    await new Promise((r) => setTimeout(r, latency));

    const rng = seededRandom(seed + i * 7919);
    const biases = [0.75, 0.65, 0.70, 0.60, 0.68];
    const roll = rng();
    let vote: VoteOutcome;
    let confidence: number;
    let llmResponse: string;

    if (roll < biases[i]) {
      vote = "ACCEPT"; confidence = 0.70 + rng() * 0.25; llmResponse = "YES";
    } else if (roll < biases[i] + 0.15) {
      vote = "UNCERTAIN"; confidence = 0.40 + rng() * 0.25; llmResponse = "UNCERTAIN";
    } else {
      vote = "REJECT"; confidence = 0.55 + rng() * 0.30; llmResponse = "NO";
    }

    const reasoningPool = REASONING_TEMPLATES[llmResponse === "YES" ? "YES" : llmResponse === "NO" ? "NO" : "UNCERTAIN"];
    const reasoning = reasoningPool[Math.floor(rng() * reasoningPool.length)];

    const stateAfter: Record<string, string> = {};
    for (const sv of parsed.stateVars) {
      if (sv.type === "str") stateAfter[sv.name] = `"${llmResponse}"`;
      else if (sv.type === "bool") stateAfter[sv.name] = vote === "ACCEPT" ? "True" : "False";
      else stateAfter[sv.name] = `<${sv.type}>`;
    }

    consoleLog.push(`[sim:${i}] ${VALIDATOR_NAMES[i]} (${model.name}) → ${vote} (${Math.round(confidence * 100)}%)`);

    validators.push({
      validatorIndex: i,
      validatorName: VALIDATOR_NAMES[i],
      llmModel: model.name,
      llmProvider: model.provider,
      inputReceived: input,
      promptSent: `[Simulation — ${functionName}]
Input: "${input}"
Respond YES, NO, or UNCERTAIN.`,
      llmResponse,
      vote,
      confidence,
      reasoning,
      executionMs: Math.round(latency),
      stateAfter,
    });
  }

  const voteCounts = { ACCEPT: 0, REJECT: 0, UNCERTAIN: 0 };
  for (const v of validators) voteCounts[v.vote]++;
  const total = validators.length;
  const dominantVote = (Object.entries(voteCounts).sort((a, b) => b[1] - a[1])[0][0]) as VoteOutcome;
  const agreeingCount = voteCounts[dominantVote];
  const passed = agreeingCount / total >= 0.6;

  const equivalence: EquivalenceResult = {
    mode: "non-comparative",
    passed,
    agreeingCount,
    totalCount: total,
    threshold: 0.6,
    dominantVote,
    explanation: passed
      ? `${agreeingCount}/${total} validators voted ${dominantVote} — exceeds 60% threshold. [Simulated]`
      : `No single outcome reached 60% agreement. Highest: ${dominantVote} at ${agreeingCount}/${total}. [Simulated]`,
  };

  const finalOutcome: "ACCEPTED" | "REJECTED" | "SPLIT" = passed
    ? dominantVote === "ACCEPT" ? "ACCEPTED" : "REJECTED"
    : "SPLIT";

  consoleLog.push(`[sim:equivalence] ${equivalence.passed ? "PASSED" : "FAILED"} (${agreeingCount}/${total})`);
  consoleLog.push(`[sim:consensus] Final: ${finalOutcome}`);

  return {
    contractName: parsed.name,
    functionCalled: functionName,
    input,
    validators,
    equivalence,
    finalOutcome,
    consensusReached: passed,
    totalMs: Date.now() - startMs,
    consoleLog,
    parsedContract: parsed,
    isRealChain: false,
  };
}
