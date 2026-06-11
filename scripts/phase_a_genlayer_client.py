"""Phase A — Wire genlayer-js Studio Net client + real sandbox executor."""
import pathlib, subprocess, sys

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

def write(rel, code):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(code.encode("utf-8"))
    print(f"  wrote  {rel}")

# ── 1. lib/genlayer/client.ts ──────────────────────────────────────────────────
write("lib/genlayer/client.ts", """\
import { createClient, createAccount } from "genlayer-js";
import { chains } from "genlayer-js/chains";

// Studio Net runs locally at localhost:4000
// All calls are client-side (browser → localhost) — never call from server components
export function getGenLayerClient() {
  const privateKey = process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY as `0x${string}`;
  if (!privateKey) throw new Error("NEXT_PUBLIC_GENLAYER_PRIVATE_KEY is not set");

  const account = createAccount(privateKey);
  return createClient({
    chain: chains.studionet,
    account,
  });
}

// Singleton for client-side use
let _client: ReturnType<typeof getGenLayerClient> | null = null;

export function getClient() {
  if (!_client) _client = getGenLayerClient();
  return _client;
}
""")

# ── 2. lib/genlayer/types.ts ───────────────────────────────────────────────────
write("lib/genlayer/types.ts", """\
export interface ValidatorVote {
  address: string;
  vote: "AGREE" | "DISAGREE" | "TIMEOUT" | "NOT_VOTED" | "DETERMINISTIC_VIOLATION";
  executionResult: string;
}

export interface RealConsensusResult {
  txHash: string;
  status: string;
  finalOutcome: "ACCEPTED" | "REJECTED" | "SPLIT" | "PENDING";
  consensusReached: boolean;
  leaderReceipt: {
    result: string;
    execution_result: string;
    mode: string;
    eq_outputs: Record<string, unknown>;
    error: string | null;
  } | null;
  validators: ValidatorVote[];
  totalValidators: number;
  agreeCount: number;
  disagreeCount: number;
  contractAddress?: string;
  elapsedMs: number;
}
""")

# ── 3. lib/genlayer/executor.ts — real on-chain executor ──────────────────────
write("lib/genlayer/executor.ts", """\
"use client";

import { getClient } from "./client";
import type { RealConsensusResult } from "./types";
import { TransactionStatus } from "genlayer-js/types";

export type OnProgress = (status: string, detail?: string) => void;

/**
 * Deploy a GenLayer Intelligent Contract and call its first write method.
 * Returns real validator votes and consensus result from Studio Net.
 */
export async function executeOnChain(
  contractCode: string,
  functionName: string,
  args: unknown[],
  onProgress?: OnProgress
): Promise<RealConsensusResult> {
  const client = getClient();
  const startMs = Date.now();

  // Step 1 — Deploy
  onProgress?.("deploying", "Deploying contract to Studio Net...");
  const deployHash = await client.deployContract({
    code: contractCode,
    args: [],
    leaderOnly: false,
  });
  onProgress?.("deploy_submitted", `Deploy tx: ${deployHash}`);

  // Step 2 — Wait for deploy to be accepted
  onProgress?.("waiting_deploy", "Waiting for deploy consensus...");
  const deployReceipt = await client.waitForTransactionReceipt({
    hash: deployHash as `0x${string}` & { length: 66 },
    status: TransactionStatus.ACCEPTED,
    retries: 60,
    interval: 2000,
  });

  const contractAddress = (deployReceipt as unknown as { to_address?: string })?.to_address
    ?? (deployReceipt as unknown as { recipient?: string })?.recipient
    ?? "";

  onProgress?.("deployed", `Contract at ${contractAddress}`);

  if (!contractAddress) {
    throw new Error("Could not determine deployed contract address from receipt");
  }

  // Step 3 — Call the write function
  onProgress?.("calling", `Calling ${functionName}(${args.map(String).join(", ")})...`);
  const callHash = await client.writeContract({
    address: contractAddress as `0x${string}`,
    functionName,
    args: args as import("genlayer-js").CalldataEncodable[],
    value: BigInt(0),
    leaderOnly: false,
  });
  onProgress?.("call_submitted", `Call tx: ${callHash}`);

  // Step 4 — Wait for call consensus
  onProgress?.("waiting_consensus", "Validators executing and voting...");
  const callReceipt = await client.waitForTransactionReceipt({
    hash: callHash as `0x${string}` & { length: 66 },
    status: TransactionStatus.ACCEPTED,
    retries: 60,
    interval: 2000,
  });

  onProgress?.("finalized", "Consensus reached");

  // Step 5 — Parse receipt into our result shape
  return parseReceipt(callReceipt, callHash, contractAddress, startMs);
}

/**
 * Call a write method on an already-deployed contract.
 */
export async function callOnChain(
  contractAddress: string,
  functionName: string,
  args: unknown[],
  onProgress?: OnProgress
): Promise<RealConsensusResult> {
  const client = getClient();
  const startMs = Date.now();

  onProgress?.("calling", `Calling ${functionName} on ${contractAddress.slice(0, 10)}...`);

  const callHash = await client.writeContract({
    address: contractAddress as `0x${string}`,
    functionName,
    args: args as import("genlayer-js").CalldataEncodable[],
    value: BigInt(0),
    leaderOnly: false,
  });

  onProgress?.("waiting_consensus", "Validators executing and voting...");

  const receipt = await client.waitForTransactionReceipt({
    hash: callHash as `0x${string}` & { length: 66 },
    status: TransactionStatus.ACCEPTED,
    retries: 60,
    interval: 2000,
  });

  onProgress?.("finalized", "Consensus reached");
  return parseReceipt(receipt, callHash, contractAddress, startMs);
}

/**
 * Read contract state (no consensus needed).
 */
export async function readOnChain(
  contractAddress: string,
  functionName: string,
  args: unknown[] = []
): Promise<unknown> {
  const client = getClient();
  return client.readContract({
    address: contractAddress as `0x${string}`,
    functionName,
    args: args as import("genlayer-js").CalldataEncodable[],
  });
}

// ── helpers ───────────────────────────────────────────────────────────────────

function parseReceipt(
  receipt: Record<string, unknown>,
  txHash: string,
  contractAddress: string,
  startMs: number
): RealConsensusResult {
  const statusName = (receipt.statusName ?? receipt.status ?? "UNKNOWN") as string;
  const consensusData = receipt.consensus_data as {
    final?: boolean;
    leader_receipt?: Record<string, unknown>[];
    validators?: Record<string, unknown>[];
    votes?: Record<string, string>;
  } | undefined;

  const leaderReceiptRaw = consensusData?.leader_receipt?.[0];
  const leaderReceipt = leaderReceiptRaw ? {
    result:           String(leaderReceiptRaw.result ?? ""),
    execution_result: String(leaderReceiptRaw.execution_result ?? ""),
    mode:             String(leaderReceiptRaw.mode ?? ""),
    eq_outputs:       (leaderReceiptRaw.eq_outputs ?? {}) as Record<string, unknown>,
    error:            leaderReceiptRaw.error ? String(leaderReceiptRaw.error) : null,
  } : null;

  // Build per-validator vote list from lastRound
  const lastRound = receipt.lastRound as {
    roundValidators?: string[];
    validatorVotesName?: string[];
  } | undefined;

  const validators: ValidatorVote[] = [];
  if (lastRound?.roundValidators) {
    lastRound.roundValidators.forEach((addr, i) => {
      validators.push({
        address: addr,
        vote: (lastRound.validatorVotesName?.[i] ?? "NOT_VOTED") as ValidatorVote["vote"],
        executionResult: "",
      });
    });
  }

  const agreeCount   = validators.filter((v) => v.vote === "AGREE").length;
  const disagreeCount = validators.filter((v) => v.vote === "DISAGREE").length;
  const total = validators.length;

  const accepted = ["ACCEPTED", "FINALIZED", "READY_TO_FINALIZE"].includes(statusName);
  const rejected = statusName === "UNDETERMINED" || disagreeCount > agreeCount;

  const finalOutcome: RealConsensusResult["finalOutcome"] = accepted
    ? "ACCEPTED"
    : rejected
    ? "REJECTED"
    : total === 0
    ? "PENDING"
    : "SPLIT";

  return {
    txHash,
    status: statusName,
    finalOutcome,
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

# ── 4. lib/genlayer/contracts.ts — standard contract templates ────────────────
write("lib/genlayer/contracts.ts", """\
// Standard Intelligent Contract used by the Playground claim simulator
export const CLAIM_EVALUATOR_CONTRACT = `# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

class ClaimEvaluator(gl.Contract):
    result: str
    claim: str
    reasoning: str

    def __init__(self) -> None:
        self.result = ""
        self.claim = ""
        self.reasoning = ""

    @gl.public.view
    def get_result(self) -> str:
        return self.result

    @gl.public.view
    def get_claim(self) -> str:
        return self.claim

    @gl.public.write
    def evaluate(self, claim: str) -> None:
        self.claim = claim
        response = gl.exec_prompt(
            f"You are a fact-checking validator on the GenLayer blockchain. "
            f"Evaluate the following claim and respond with ONLY 'YES' if it is accurate/valid, "
            f"or 'NO' if it is not accurate/valid. Claim: {claim}"
        )
        self.result = response.strip().upper()[:3]
`;
""")

# ── 5. Update .env.local with the private key ─────────────────────────────────
env_path = ROOT / ".env.local"
env = env_path.read_text(encoding="utf-8")

if "NEXT_PUBLIC_GENLAYER_PRIVATE_KEY" not in env:
    env += "\n# -- GenLayer Studio Net -------------------------------------------------\n"
    env += "NEXT_PUBLIC_GENLAYER_PRIVATE_KEY=0x78c31f4f26d022683cf6edfae1e368a246d9cf5ecca32ab6729f6dfa9c68409f\n"
    env += "NEXT_PUBLIC_GENLAYER_RPC_URL=http://localhost:4000/api\n"
    env_path.write_bytes(env.encode("utf-8"))
    print("  updated .env.local")
else:
    print("  .env.local already has NEXT_PUBLIC_GENLAYER_PRIVATE_KEY")

# ── 6. Update sandbox executor to use real chain with simulation fallback ──────
write("lib/sandbox/executor.ts", """\
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
      promptSent: `[Simulation — ${functionName}]\nInput: "${input}"\nRespond YES, NO, or UNCERTAIN.`,
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
""")

# ── 7. Add chain mode badge to SandboxConsole ─────────────────────────────────
# Update sandbox page to pass onProgress + show chain indicator
write("app/(dashboard)/sandbox/page.tsx", """\
"use client";

import { useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { CONTRACT_TEMPLATES } from "@/lib/sandbox/templates";
import { executeSandboxContract } from "@/lib/sandbox/executor";
import { parseContract } from "@/lib/sandbox/parser";
import { useSandboxStore } from "@/store/sandboxStore";
import { CodeEditor } from "@/components/sandbox/CodeEditor";
import { TemplateSelector } from "@/components/sandbox/TemplateSelector";
import { ContractInspector } from "@/components/sandbox/ContractInspector";
import { ExecutionPanel } from "@/components/sandbox/ExecutionPanel";
import { SandboxConsole } from "@/components/sandbox/SandboxConsole";

const DEFAULT_CODE  = CONTRACT_TEMPLATES[0].code;
const DEFAULT_INPUT = CONTRACT_TEMPLATES[0].defaultInput;

export default function SandboxPage() {
  const {
    code, activeTemplateId, functionInput, isRunning, currentResult,
    setCode, setActiveTemplate, setFunctionInput, setIsRunning, setCurrentResult,
  } = useSandboxStore();

  const [consoleLines, setConsoleLines] = useState<string[]>([]);
  const [chainStatus, setChainStatus]   = useState<string>("");

  const effectiveCode  = code  || DEFAULT_CODE;
  const effectiveInput = functionInput || DEFAULT_INPUT;
  const parsed         = useMemo(() => parseContract(effectiveCode), [effectiveCode]);
  const writeFn        = parsed.functions.find((f) => f.decorator === "@gl.public.write");

  const isRealChain = !!(process.env.NEXT_PUBLIC_GENLAYER_PRIVATE_KEY);

  async function handleRun() {
    if (!writeFn) return;
    setIsRunning(true);
    setConsoleLines([]);
    setChainStatus("");

    try {
      const result = await executeSandboxContract(
        effectiveCode,
        writeFn.name,
        effectiveInput,
        (status, detail) => {
          setChainStatus(detail ?? status);
          setConsoleLines((prev) => [...prev, `[${status}] ${detail ?? ""}`]);
        }
      );
      setCurrentResult(result);
      setConsoleLines(result.consoleLog);
    } catch (err) {
      setConsoleLines([`[ERROR] ${String(err)}`]);
    } finally {
      setIsRunning(false);
      setChainStatus("");
    }
  }

  function handleSelectTemplate(t: typeof CONTRACT_TEMPLATES[0]) {
    setCode(t.code);
    setFunctionInput(t.defaultInput);
    setActiveTemplate(t.id);
    setCurrentResult(null);
    setConsoleLines([]);
  }

  function handleReset() {
    setCode("");
    setFunctionInput("");
    setActiveTemplate(null);
    setCurrentResult(null);
    setConsoleLines([]);
    setIsRunning(false);
  }

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8 space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#1a1a1a]">Contract Sandbox</h1>
            <p className="text-sm text-[#6b6560] mt-1">
              Write and execute Intelligent Contracts on GenLayer
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Chain mode indicator */}
            <div className={cn(
              "flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium",
              isRealChain
                ? "border-green-300 bg-green-50 text-green-700"
                : "border-amber-300 bg-amber-50 text-amber-700"
            )}>
              {isRealChain
                ? <><Wifi className="h-3 w-3" /> Studio Net</>
                : <><WifiOff className="h-3 w-3" /> Simulated</>
              }
            </div>
            <Button variant="ghost" size="sm" onClick={handleReset} className="gap-1.5 text-xs h-8">
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </Button>
          </div>
        </div>

        {/* Template selector */}
        <TemplateSelector
          templates={CONTRACT_TEMPLATES}
          activeId={activeTemplateId}
          onSelect={handleSelectTemplate}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: editor + inspector */}
          <div className="space-y-4">
            <CodeEditor
              value={effectiveCode}
              onChange={setCode}
            />
            <ContractInspector parsed={parsed} />
          </div>

          {/* Right: run panel + console */}
          <div className="space-y-4">
            <div className="rounded-xl border border-[#d8d4c8] bg-white p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-xs font-medium text-[#1a1a1a]">
                    Function: <code className="text-[#6b6560]">{writeFn?.name ?? "—"}</code>
                  </p>
                  <p className="text-xs text-[#6b6560]">Input argument</p>
                </div>
                <Button
                  onClick={handleRun}
                  disabled={isRunning || !writeFn}
                  size="sm"
                  className="gap-1.5 text-xs h-8 bg-[#2d2a26] text-[#efece4] hover:bg-[#1a1a1a]"
                >
                  <Play className="h-3.5 w-3.5" />
                  {isRunning ? (isRealChain ? "On-chain..." : "Simulating...") : "Run"}
                </Button>
              </div>

              <input
                type="text"
                value={effectiveInput}
                onChange={(e) => setFunctionInput(e.target.value)}
                placeholder="Enter input for the write function..."
                className="w-full rounded-lg border border-[#d8d4c8] bg-[#f8f6f0] px-3 py-2 text-sm text-[#1a1a1a] placeholder:text-[#9e9891] focus:outline-none focus:ring-2 focus:ring-[#2d2a26]/20"
              />

              {/* Chain status during execution */}
              <AnimatePresence>
                {isRunning && chainStatus && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="rounded-lg bg-blue-50 border border-blue-200 px-3 py-2 text-xs text-blue-700"
                  >
                    <span className="font-medium">
                      {isRealChain ? "⛓ On-chain: " : "⚙ "}
                    </span>
                    {chainStatus}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Real chain tx link */}
              {currentResult?.realChain && (
                <div className="rounded-lg bg-green-50 border border-green-200 px-3 py-2 text-xs text-green-800 space-y-1">
                  <p className="font-medium">On-chain result</p>
                  <p>Status: <span className="font-mono">{currentResult.realChain.status}</span></p>
                  <p className="font-mono truncate">Tx: {currentResult.realChain.txHash}</p>
                  {currentResult.realChain.contractAddress && (
                    <p className="font-mono truncate">Contract: {currentResult.realChain.contractAddress}</p>
                  )}
                </div>
              )}
            </div>

            <AnimatePresence mode="wait">
              {currentResult && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                >
                  <ExecutionPanel result={currentResult} />
                </motion.div>
              )}
            </AnimatePresence>

            <SandboxConsole lines={consoleLines} isRunning={isRunning} />
          </div>
        </div>
      </div>
    </div>
  );
}
""")

print("\nAll files written. Running build...")
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
