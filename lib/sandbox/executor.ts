import { LLM_MODELS } from "@/lib/llm/models";
import { parseContract, type ParsedContract } from "./parser";

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
}

const VALIDATOR_NAMES = [
  "Alice (Leader)",
  "Bob",
  "Carol",
  "Dave",
  "Eve",
];

const REASONING_TEMPLATES: Record<string, string[]> = {
  YES: [
    "Based on my analysis of the provided information, the answer is clearly affirmative. The evidence strongly supports a positive determination.",
    "My evaluation concludes this meets the specified criteria. The submitted information aligns with the requirements upon careful review.",
    "After thorough consideration, I find sufficient evidence to answer in the affirmative. The conditions appear to be satisfied.",
  ],
  NO: [
    "Upon careful evaluation, I cannot confirm the affirmative. The available evidence does not sufficiently support a positive determination.",
    "My analysis indicates this does not meet the required criteria. There are notable gaps between the requirements and what was presented.",
    "After review, I find the evidence inconclusive or insufficient to support a YES determination. A negative finding is warranted.",
  ],
  UNCERTAIN: [
    "The information provided is ambiguous. I cannot make a definitive determination with the available context.",
    "My analysis reveals conflicting signals. Without additional context, I must classify this as uncertain.",
    "The available information is insufficient for a confident determination in either direction.",
  ],
};

function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 4294967296;
  };
}

function pickReasoning(vote: VoteOutcome, rng: () => number): string {
  const pool = REASONING_TEMPLATES[vote] ?? REASONING_TEMPLATES.UNCERTAIN;
  return pool[Math.floor(rng() * pool.length)];
}

function simulateValidatorVote(
  validatorIdx: number,
  input: string,
  functionName: string,
  seed: number
): { vote: VoteOutcome; confidence: number; llmResponse: string; reasoning: string; promptSent: string } {
  const rng = seededRandom(seed + validatorIdx * 7919);

  // Bias per validator to show disagreement
  const biases = [0.75, 0.65, 0.70, 0.60, 0.68];
  const bias = biases[validatorIdx] ?? 0.65;

  const roll = rng();
  let vote: VoteOutcome;
  let confidence: number;
  let llmResponse: string;

  if (roll < bias) {
    vote = "ACCEPT";
    confidence = 0.70 + rng() * 0.25;
    llmResponse = "YES";
  } else if (roll < bias + 0.15) {
    vote = "UNCERTAIN";
    confidence = 0.40 + rng() * 0.25;
    llmResponse = "UNCERTAIN";
  } else {
    vote = "REJECT";
    confidence = 0.55 + rng() * 0.30;
    llmResponse = "NO";
  }

  const promptSent = `[Sandbox simulation — ${functionName}]\nInput: "${input}"\nEvaluate and respond with YES, NO, or UNCERTAIN.`;
  const reasoning = pickReasoning(vote, rng);

  return { vote, confidence, llmResponse, reasoning, promptSent };
}

export async function executeSandboxContract(
  code: string,
  functionName: string,
  input: string
): Promise<SandboxExecutionResult> {
  const parsed = parseContract(code);
  const consoleLog: string[] = [];
  const seed = Date.now() % 100000;

  consoleLog.push(`[sandbox] Parsing contract source...`);
  consoleLog.push(`[sandbox] Contract: ${parsed.name || "Unknown"}`);
  consoleLog.push(`[sandbox] Write functions: ${parsed.writeCount}, View functions: ${parsed.viewCount}`);
  consoleLog.push(`[sandbox] Calling: ${functionName}("${input}")`);
  consoleLog.push(`[sandbox] Dispatching to ${VALIDATOR_NAMES.length} validators...`);

  const startMs = Date.now();
  const validators: ValidatorExecution[] = [];

  for (let i = 0; i < VALIDATOR_NAMES.length; i++) {
    const model = LLM_MODELS[i % LLM_MODELS.length];
    const execStart = Date.now();
    const latency = model.latencyMs.min + Math.random() * (model.latencyMs.max - model.latencyMs.min);

    await new Promise((r) => setTimeout(r, latency));

    const sim = simulateValidatorVote(i, input, functionName, seed);
    const execMs = Date.now() - execStart;

    const stateAfter: Record<string, string> = {};
    for (const sv of parsed.stateVars) {
      if (sv.type === "str") stateAfter[sv.name] = `"${sim.llmResponse}"`;
      else if (sv.type === "bool") stateAfter[sv.name] = sim.vote === "ACCEPT" ? "True" : "False";
      else if (sv.type === "int") stateAfter[sv.name] = String(Math.floor(Math.random() * 100));
      else stateAfter[sv.name] = `<${sv.type}>`;
    }

    consoleLog.push(`[validator:${i}] ${VALIDATOR_NAMES[i]} (${model.name}) → ${sim.vote} (${Math.round(sim.confidence * 100)}%)`);

    validators.push({
      validatorIndex: i,
      validatorName: VALIDATOR_NAMES[i],
      llmModel: model.name,
      llmProvider: model.provider,
      inputReceived: input,
      promptSent: sim.promptSent,
      llmResponse: sim.llmResponse,
      vote: sim.vote,
      confidence: sim.confidence,
      reasoning: sim.reasoning,
      executionMs: execMs,
      stateAfter,
    });
  }

  // Equivalence check
  const voteCounts = { ACCEPT: 0, REJECT: 0, UNCERTAIN: 0 };
  for (const v of validators) voteCounts[v.vote]++;

  const total = validators.length;
  const threshold = 0.6;
  const dominantVote = (Object.entries(voteCounts).sort((a, b) => b[1] - a[1])[0][0]) as VoteOutcome;
  const agreeingCount = voteCounts[dominantVote];
  const passed = agreeingCount / total >= threshold;

  const equivalence: EquivalenceResult = {
    mode: "non-comparative",
    passed,
    agreeingCount,
    totalCount: total,
    threshold,
    dominantVote,
    explanation: passed
      ? `${agreeingCount}/${total} validators (${Math.round(agreeingCount / total * 100)}%) voted ${dominantVote} — exceeds the 60% threshold. Consensus reached.`
      : `No single outcome reached 60% agreement. Highest: ${dominantVote} with ${agreeingCount}/${total} (${Math.round(agreeingCount / total * 100)}%). Consensus failed — appeal may be triggered.`,
  };

  const finalOutcome: "ACCEPTED" | "REJECTED" | "SPLIT" = passed
    ? dominantVote === "ACCEPT" ? "ACCEPTED" : "REJECTED"
    : "SPLIT";

  consoleLog.push(`[equivalence] Mode: non-comparative | Dominant: ${dominantVote} | Threshold: 60%`);
  consoleLog.push(`[equivalence] Result: ${equivalence.passed ? "PASSED" : "FAILED"} (${agreeingCount}/${total} agree)`);
  consoleLog.push(`[consensus] Final outcome: ${finalOutcome}`);

  const totalMs = Date.now() - startMs;

  return {
    contractName: parsed.name,
    functionCalled: functionName,
    input,
    validators,
    equivalence,
    finalOutcome,
    consensusReached: passed,
    totalMs,
    consoleLog,
    parsedContract: parsed,
  };
}
