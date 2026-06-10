"""Phase 10 — Developer Sandbox (/sandbox)
Writes every file for the in-browser Intelligent Contract editor
with live validator simulation, contract inspector, and console log.
"""
import pathlib, subprocess, sys

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

# ── helpers ──────────────────────────────────────────────────────────────────
def write(rel: str, code: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(code.encode("utf-8"))
    print(f"  wrote  {rel}")

def npm(*args) -> None:
    subprocess.run(["npm", *args], cwd=ROOT, check=True, shell=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. lib/sandbox/templates.ts
# ─────────────────────────────────────────────────────────────────────────────
write("lib/sandbox/templates.ts", r'''
export interface ContractTemplate {
  id: string;
  name: string;
  description: string;
  category: "Finance" | "Oracle" | "Governance" | "Social";
  difficulty: "beginner" | "intermediate" | "advanced";
  icon: string;
  defaultInput: string;
  code: string;
}

export const CONTRACT_TEMPLATES: ContractTemplate[] = [
  {
    id: "hello",
    name: "Hello GenLayer",
    description: "The simplest possible Intelligent Contract — a yes/no question answered by the validator's LLM.",
    category: "Social",
    difficulty: "beginner",
    icon: "👋",
    defaultInput: "Is the sky blue?",
    code: `# { "Depends": "py-genlayer:test" }
from genlayer import *

class HelloGenLayer(gl.Contract):
    answer: str

    def __init__(self) -> None:
        self.answer = ""

    @gl.public.view
    def get_answer(self) -> str:
        return self.answer

    @gl.public.write
    def ask(self, question: str) -> None:
        """Ask the validator's LLM a yes/no question."""
        result = gl.exec_prompt(
            f"Answer this question with YES or NO only: {question}"
        )
        self.answer = result.strip().upper()
`,
  },
  {
    id: "prediction",
    name: "Prediction Market",
    description: "A market where the validator's LLM resolves whether a real-world event occurred.",
    category: "Finance",
    difficulty: "intermediate",
    icon: "📈",
    defaultInput: "Did the price of Bitcoin exceed $100,000 in 2024?",
    code: `# { "Depends": "py-genlayer:test" }
from genlayer import *

class PredictionMarket(gl.Contract):
    question: str
    resolution: str
    resolved: bool

    def __init__(self, question: str) -> None:
        self.question = question
        self.resolution = ""
        self.resolved = False

    @gl.public.view
    def get_result(self) -> dict:
        return {
            "question": self.question,
            "resolution": self.resolution,
            "resolved": self.resolved,
        }

    @gl.public.write
    def resolve(self) -> None:
        """Resolve the market using the validator's LLM."""
        assert not self.resolved, "Market already resolved"

        verdict = gl.exec_prompt(
            f"Based on publicly available information, did this event occur? "
            f"Event: {self.question} "
            f"Reply with YES if it occurred, NO if it did not, or UNCERTAIN if you cannot determine."
        )

        v = verdict.strip().upper()
        if "YES" in v:
            self.resolution = "YES"
        elif "NO" in v:
            self.resolution = "NO"
        else:
            self.resolution = "UNCERTAIN"
        self.resolved = True
`,
  },
  {
    id: "escrow",
    name: "Freelance Escrow",
    description: "Escrow contract where an LLM evaluates whether freelance work meets the agreed requirements.",
    category: "Finance",
    difficulty: "intermediate",
    icon: "🤝",
    defaultInput: "Built a responsive React dashboard with authentication, data visualization, and mobile support as specified.",
    code: `# { "Depends": "py-genlayer:test" }
from genlayer import *

class FreelanceEscrow(gl.Contract):
    client: str
    requirements: str
    approved: bool
    rejection_reason: str

    def __init__(self, client: str, requirements: str) -> None:
        self.client = client
        self.requirements = requirements
        self.approved = False
        self.rejection_reason = ""

    @gl.public.view
    def get_status(self) -> dict:
        return {
            "client": self.client,
            "requirements": self.requirements,
            "approved": self.approved,
            "rejection_reason": self.rejection_reason,
        }

    @gl.public.write
    def submit_work(self, work_description: str) -> None:
        """Evaluate submitted work against requirements."""
        verdict = gl.exec_prompt(
            f"You are evaluating freelance work delivery.\\n"
            f"Requirements: {self.requirements}\\n"
            f"Submitted work: {work_description}\\n"
            f"Does the submitted work satisfy the requirements? "
            f"Reply YES if satisfied, NO if not satisfied."
        )

        if "YES" in verdict.strip().upper():
            self.approved = True
        else:
            self.approved = False
            self.rejection_reason = verdict.strip()
`,
  },
  {
    id: "weather",
    name: "Weather Oracle",
    description: "An oracle contract that determines whether weather conditions meet a specified threshold.",
    category: "Oracle",
    difficulty: "beginner",
    icon: "🌤️",
    defaultInput: "Paris, France on June 15, 2024 — was temperature above 25°C?",
    code: `# { "Depends": "py-genlayer:test" }
from genlayer import *

class WeatherOracle(gl.Contract):
    last_query: str
    last_result: str
    query_count: int

    def __init__(self) -> None:
        self.last_query = ""
        self.last_result = ""
        self.query_count = 0

    @gl.public.view
    def get_last_result(self) -> dict:
        return {
            "query": self.last_query,
            "result": self.last_result,
            "total_queries": self.query_count,
        }

    @gl.public.write
    def check_weather(self, query: str) -> None:
        """Check a weather condition using the validator's LLM."""
        result = gl.exec_prompt(
            f"Weather oracle query: {query}\\n"
            f"Based on historical weather data and your knowledge, "
            f"answer YES if the condition was met, NO if not, "
            f"or UNCERTAIN if you cannot determine with confidence."
        )

        self.last_query = query
        self.last_result = result.strip()
        self.query_count += 1
`,
  },
  {
    id: "moderation",
    name: "Content Moderation",
    description: "AI-powered content moderation where validators reach consensus on whether content violates policy.",
    category: "Governance",
    difficulty: "advanced",
    icon: "🛡️",
    defaultInput: "This product is absolutely terrible and the company should be ashamed of themselves.",
    code: `# { "Depends": "py-genlayer:test" }
from genlayer import *

class ContentModerator(gl.Contract):
    policy: str
    decisions: dict
    total_reviewed: int
    total_flagged: int

    def __init__(self, policy: str) -> None:
        self.policy = policy
        self.decisions = {}
        self.total_reviewed = 0
        self.total_flagged = 0

    @gl.public.view
    def get_stats(self) -> dict:
        return {
            "total_reviewed": self.total_reviewed,
            "total_flagged": self.total_flagged,
            "flag_rate": (
                self.total_flagged / self.total_reviewed
                if self.total_reviewed > 0 else 0
            ),
        }

    @gl.public.write
    def review_content(self, content_id: str, content: str) -> None:
        """Review content against the moderation policy."""
        verdict = gl.exec_prompt(
            f"Content Moderation Policy: {self.policy}\\n"
            f"Content to review: {content}\\n"
            f"Does this content violate the policy? "
            f"Reply VIOLATES if it does, COMPLIANT if it does not. "
            f"Be consistent and objective."
        )

        v = verdict.strip().upper()
        flagged = "VIOLATES" in v

        self.decisions[content_id] = {
            "flagged": flagged,
            "verdict": verdict.strip(),
        }
        self.total_reviewed += 1
        if flagged:
            self.total_flagged += 1
`,
  },
];
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 2. lib/sandbox/parser.ts
# ─────────────────────────────────────────────────────────────────────────────
write("lib/sandbox/parser.ts", r'''
export interface ParsedStateVar {
  name: string;
  type: string;
}

export interface ParsedFunction {
  name: string;
  decorator: "@gl.public.view" | "@gl.public.write" | "constructor";
  params: string[];
  docstring: string;
  returnsType: string;
}

export interface ParsedContract {
  name: string;
  stateVars: ParsedStateVar[];
  functions: ParsedFunction[];
  hasExecPrompt: boolean;
  writeCount: number;
  viewCount: number;
  errors: string[];
}

export function parseContract(code: string): ParsedContract {
  const errors: string[] = [];
  const lines = code.split("\n");

  // Contract name
  const nameMatch = code.match(/class\s+(\w+)\s*\(gl\.Contract\)/);
  const name = nameMatch ? nameMatch[1] : "";
  if (!name) errors.push("No class inheriting gl.Contract found");

  // State variables (typed class attributes before __init__)
  const stateVars: ParsedStateVar[] = [];
  const statePattern = /^\s{4}(\w+):\s*([^\s=][^\n]*?)(?:\s*$)/gm;
  let m: RegExpExecArray | null;
  while ((m = statePattern.exec(code)) !== null) {
    const vname = m[1];
    const vtype = m[2].trim();
    if (vname !== "def" && !vname.startsWith("@") && vname !== "return") {
      stateVars.push({ name: vname, type: vtype });
    }
  }

  // Functions
  const functions: ParsedFunction[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Constructor
    if (/^\s+def __init__/.test(line)) {
      const paramMatch = line.match(/def __init__\(self(?:,\s*([^)]*))?\)/);
      const params = paramMatch?.[1]
        ? paramMatch[1].split(",").map((p) => p.trim()).filter(Boolean)
        : [];
      let docstring = "";
      if (lines[i + 1]?.trim().startsWith('"""')) {
        docstring = lines[i + 1].trim().replace(/"""/g, "").trim();
      }
      functions.push({
        name: "__init__",
        decorator: "constructor",
        params,
        docstring,
        returnsType: "None",
      });
      continue;
    }

    // Public functions
    const decorLine = line.trim();
    if (decorLine === "@gl.public.view" || decorLine === "@gl.public.write") {
      const decorator = decorLine as "@gl.public.view" | "@gl.public.write";
      const defLine = lines[i + 1] ?? "";
      const defMatch = defLine.match(/def\s+(\w+)\(self(?:,\s*([^)]*))?\)(?:\s*->\s*([^:]+))?/);
      if (defMatch) {
        const fname = defMatch[1];
        const rawParams = defMatch[2] ?? "";
        const params = rawParams
          .split(",")
          .map((p) => p.trim())
          .filter(Boolean);
        const returnsType = defMatch[3]?.trim() ?? "None";
        let docstring = "";
        const docLine = lines[i + 2]?.trim() ?? "";
        if (docLine.startsWith('"""')) {
          docstring = docLine.replace(/"""/g, "").trim();
        }
        functions.push({ name: fname, decorator, params, docstring, returnsType });
      }
    }
  }

  const hasExecPrompt = code.includes("gl.exec_prompt(");
  const writeCount = functions.filter((f) => f.decorator === "@gl.public.write").length;
  const viewCount = functions.filter((f) => f.decorator === "@gl.public.view").length;

  if (!hasExecPrompt && writeCount > 0) {
    errors.push("Write function found but no gl.exec_prompt() call — validators have nothing to reason about");
  }

  return { name, stateVars, functions, hasExecPrompt, writeCount, viewCount, errors };
}
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 3. lib/sandbox/executor.ts
# ─────────────────────────────────────────────────────────────────────────────
write("lib/sandbox/executor.ts", r'''
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
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 4. store/sandboxStore.ts
# ─────────────────────────────────────────────────────────────────────────────
write("store/sandboxStore.ts", r'''
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SandboxExecutionResult } from "@/lib/sandbox/executor";

interface SandboxStore {
  code: string;
  activeTemplateId: string | null;
  functionInput: string;
  isRunning: boolean;
  currentResult: SandboxExecutionResult | null;
  history: SandboxExecutionResult[];
  selectedValidatorIndex: number | null;

  setCode: (code: string) => void;
  setActiveTemplate: (id: string | null) => void;
  setFunctionInput: (input: string) => void;
  setIsRunning: (v: boolean) => void;
  setCurrentResult: (result: SandboxExecutionResult) => void;
  selectValidator: (index: number | null) => void;
  clearHistory: () => void;
}

export const useSandboxStore = create<SandboxStore>()(
  persist(
    (set) => ({
      code: "",
      activeTemplateId: null,
      functionInput: "",
      isRunning: false,
      currentResult: null,
      history: [],
      selectedValidatorIndex: null,

      setCode: (code) => set({ code }),
      setActiveTemplate: (id) => set({ activeTemplateId: id }),
      setFunctionInput: (input) => set({ functionInput: input }),
      setIsRunning: (v) => set({ isRunning: v }),
      setCurrentResult: (result) =>
        set((s) => ({
          currentResult: result,
          history: [result, ...s.history].slice(0, 20),
          selectedValidatorIndex: null,
        })),
      selectValidator: (index) => set({ selectedValidatorIndex: index }),
      clearHistory: () => set({ history: [] }),
    }),
    {
      name: "sandbox-store",
      partialize: (s) => ({
        code: s.code,
        activeTemplateId: s.activeTemplateId,
        functionInput: s.functionInput,
      }),
    }
  )
);
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 5. components/sandbox/CodeEditor.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("components/sandbox/CodeEditor.tsx", r'''
"use client";

import { useRef, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";

interface CodeEditorProps {
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
}

export function CodeEditor({ value, onChange, disabled }: CodeEditorProps) {
  const taRef = useRef<HTMLTextAreaElement>(null);
  const linesRef = useRef<HTMLDivElement>(null);

  const lines = value.split("\n");

  // Sync scroll between textarea and line numbers
  const syncScroll = useCallback(() => {
    if (taRef.current && linesRef.current) {
      linesRef.current.scrollTop = taRef.current.scrollTop;
    }
  }, []);

  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.addEventListener("scroll", syncScroll);
    return () => ta.removeEventListener("scroll", syncScroll);
  }, [syncScroll]);

  // Tab key support
  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Tab") {
      e.preventDefault();
      const ta = taRef.current!;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const newVal = value.slice(0, start) + "    " + value.slice(end);
      onChange(newVal);
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + 4;
      });
    }
  }

  return (
    <div className="relative flex rounded-xl border border-[#2d2a26] overflow-hidden bg-[#1a1a1a] font-mono text-xs leading-6 h-full">
      {/* Line numbers */}
      <div
        ref={linesRef}
        className="select-none overflow-hidden bg-[#141414] text-[#5a5550] text-right pr-3 pl-3 pt-4 pb-4 min-w-[3rem] border-r border-[#2d2a26]"
        style={{ overflowY: "hidden" }}
        aria-hidden
      >
        {lines.map((_, i) => (
          <div key={i} className="leading-6">{i + 1}</div>
        ))}
      </div>

      {/* Editable area */}
      <textarea
        ref={taRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onScroll={syncScroll}
        disabled={disabled}
        spellCheck={false}
        autoCapitalize="off"
        autoCorrect="off"
        className={cn(
          "flex-1 resize-none outline-none bg-transparent text-[#e8e4da] caret-[#efece4]",
          "px-4 py-4 leading-6 whitespace-pre overflow-auto",
          disabled && "opacity-50 cursor-not-allowed"
        )}
        style={{ fontFamily: "ui-monospace, 'Cascadia Code', 'Fira Code', Consolas, monospace" }}
      />
    </div>
  );
}
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 6. components/sandbox/TemplateSelector.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("components/sandbox/TemplateSelector.tsx", r'''
"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { CONTRACT_TEMPLATES, type ContractTemplate } from "@/lib/sandbox/templates";

interface TemplateSelectorProps {
  activeId: string | null;
  onSelect: (t: ContractTemplate) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  Finance:    "bg-green-100 text-green-700",
  Oracle:     "bg-blue-100 text-blue-700",
  Governance: "bg-purple-100 text-purple-700",
  Social:     "bg-amber-100 text-amber-700",
};

const DIFF_COLORS: Record<string, string> = {
  beginner:     "text-green-600",
  intermediate: "text-amber-600",
  advanced:     "text-red-600",
};

export function TemplateSelector({ activeId, onSelect }: TemplateSelectorProps) {
  return (
    <div className="space-y-1.5">
      <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">
        Contract Templates
      </p>
      {CONTRACT_TEMPLATES.map((t, i) => (
        <motion.button
          key={t.id}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          onClick={() => onSelect(t)}
          className={cn(
            "w-full text-left rounded-lg border px-3 py-2.5 transition-all duration-150 group",
            activeId === t.id
              ? "border-[#2d2a26] bg-[#2d2a26] text-white"
              : "border-[#e8e4da] bg-white/60 hover:border-[#b8b4a8] hover:bg-white/80"
          )}
        >
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-base leading-none">{t.icon}</span>
            <span className={cn(
              "text-xs font-semibold truncate",
              activeId === t.id ? "text-white" : "text-[#1a1a1a]"
            )}>
              {t.name}
            </span>
          </div>
          <div className="flex items-center gap-1.5 mt-1">
            <span className={cn(
              "text-[9px] font-semibold px-1.5 py-0.5 rounded-full",
              activeId === t.id ? "bg-white/20 text-white" : CATEGORY_COLORS[t.category]
            )}>
              {t.category}
            </span>
            <span className={cn(
              "text-[9px] font-medium capitalize",
              activeId === t.id ? "text-white/60" : DIFF_COLORS[t.difficulty]
            )}>
              {t.difficulty}
            </span>
          </div>
        </motion.button>
      ))}
    </div>
  );
}
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 7. components/sandbox/ContractInspector.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("components/sandbox/ContractInspector.tsx", r'''
"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { parseContract } from "@/lib/sandbox/parser";
import { AlertTriangle, Eye, Edit3, Cpu, Database } from "lucide-react";

interface ContractInspectorProps {
  code: string;
}

export function ContractInspector({ code }: ContractInspectorProps) {
  const parsed = useMemo(() => parseContract(code), [code]);

  if (!parsed.name) {
    return (
      <div className="text-center py-6 text-[#6b6560] text-xs">
        No valid GenLayer contract detected.<br />
        Class must inherit <code className="bg-[#e8e4da] px-1 rounded">gl.Contract</code>.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Contract name */}
      <div>
        <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5">Contract</p>
        <div className="flex items-center gap-2 bg-[#2d2a26] rounded-lg px-3 py-2">
          <Cpu className="h-3.5 w-3.5 text-[#efece4]/60 shrink-0" />
          <span className="text-xs font-bold text-[#efece4] font-mono">{parsed.name}</span>
          {parsed.hasExecPrompt && (
            <span className="ml-auto text-[9px] bg-purple-500/30 text-purple-200 px-1.5 py-0.5 rounded-full font-semibold">
              AI-powered
            </span>
          )}
        </div>
      </div>

      {/* Errors */}
      {parsed.errors.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 space-y-1">
          {parsed.errors.map((e, i) => (
            <div key={i} className="flex items-start gap-1.5 text-xs text-amber-800">
              <AlertTriangle className="h-3 w-3 mt-0.5 shrink-0" />
              {e}
            </div>
          ))}
        </div>
      )}

      {/* State variables */}
      {parsed.stateVars.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5 flex items-center gap-1">
            <Database className="h-3 w-3" /> State ({parsed.stateVars.length})
          </p>
          <div className="space-y-1">
            {parsed.stateVars.map((sv) => (
              <div key={sv.name} className="flex items-center justify-between bg-[#f5f2ea] rounded px-2.5 py-1.5">
                <span className="text-xs font-mono text-[#1a1a1a] font-medium">{sv.name}</span>
                <span className="text-[10px] font-mono text-[#6b6560] bg-[#e8e4da] px-1.5 rounded">{sv.type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Functions */}
      {parsed.functions.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5">
            Functions ({parsed.functions.length})
          </p>
          <div className="space-y-1.5">
            {parsed.functions.map((fn, i) => (
              <motion.div
                key={fn.name}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn(
                  "rounded-lg border px-2.5 py-2",
                  fn.decorator === "@gl.public.write"
                    ? "border-purple-200 bg-purple-50"
                    : fn.decorator === "@gl.public.view"
                    ? "border-blue-200 bg-blue-50"
                    : "border-[#e8e4da] bg-[#f5f2ea]"
                )}
              >
                <div className="flex items-center gap-1.5 mb-0.5">
                  {fn.decorator === "@gl.public.write" ? (
                    <Edit3 className="h-3 w-3 text-purple-500 shrink-0" />
                  ) : fn.decorator === "@gl.public.view" ? (
                    <Eye className="h-3 w-3 text-blue-500 shrink-0" />
                  ) : null}
                  <span className="text-xs font-mono font-bold text-[#1a1a1a]">{fn.name}()</span>
                  <span className="ml-auto text-[9px] font-mono text-[#6b6560]">→ {fn.returnsType}</span>
                </div>
                {fn.decorator !== "constructor" && (
                  <div className={cn(
                    "text-[9px] font-semibold px-1.5 py-0.5 rounded-full w-fit",
                    fn.decorator === "@gl.public.write"
                      ? "bg-purple-100 text-purple-700"
                      : "bg-blue-100 text-blue-700"
                  )}>
                    {fn.decorator}
                  </div>
                )}
                {fn.params.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {fn.params.map((p) => (
                      <span key={p} className="text-[9px] font-mono bg-white/70 border border-[#d8d4c8] px-1.5 py-0.5 rounded text-[#6b6560]">
                        {p}
                      </span>
                    ))}
                  </div>
                )}
                {fn.docstring && (
                  <p className="text-[10px] text-[#6b6560] mt-1 leading-snug">{fn.docstring}</p>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 8. components/sandbox/ExecutionPanel.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("components/sandbox/ExecutionPanel.tsx", r'''
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import type { SandboxExecutionResult, ValidatorExecution } from "@/lib/sandbox/executor";
import { CheckCircle2, XCircle, AlertCircle, Zap, Clock } from "lucide-react";
import { useSandboxStore } from "@/store/sandboxStore";

const VOTE_CONFIG = {
  ACCEPT:    { cls: "bg-green-100 text-green-700 border-green-200",  icon: CheckCircle2, dot: "bg-green-500" },
  REJECT:    { cls: "bg-red-100 text-red-700 border-red-200",        icon: XCircle,      dot: "bg-red-500" },
  UNCERTAIN: { cls: "bg-amber-100 text-amber-700 border-amber-200",  icon: AlertCircle,  dot: "bg-amber-500" },
};

const OUTCOME_CONFIG = {
  ACCEPTED: { cls: "border-green-300 bg-green-50",  label: "ACCEPTED",       icon: "✅" },
  REJECTED: { cls: "border-red-300 bg-red-50",      label: "REJECTED",       icon: "❌" },
  SPLIT:    { cls: "border-amber-300 bg-amber-50",   label: "SPLIT / APPEAL", icon: "⚡" },
};

interface ValidatorCardProps {
  v: ValidatorExecution;
  isSelected: boolean;
  onClick: () => void;
  index: number;
}

function ValidatorCard({ v, isSelected, onClick, index }: ValidatorCardProps) {
  const cfg = VOTE_CONFIG[v.vote];
  const Icon = cfg.icon;
  return (
    <motion.button
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      onClick={onClick}
      className={cn(
        "w-full text-left rounded-xl border-2 p-3 transition-all duration-200",
        isSelected ? "border-[#2d2a26] shadow-md" : "border-[#e8e4da] hover:border-[#b8b4a8]",
        "bg-white/70"
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <p className="text-xs font-bold text-[#1a1a1a] leading-tight">{v.validatorName}</p>
          <p className="text-[10px] text-[#6b6560]">{v.llmModel}</p>
        </div>
        <div className={cn("flex items-center gap-1 px-2 py-0.5 rounded-full border text-[10px] font-bold shrink-0", cfg.cls)}>
          <Icon className="h-3 w-3" />
          {v.vote}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-[#e8e4da] rounded-full overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all", cfg.dot)}
            style={{ width: `${Math.round(v.confidence * 100)}%` }}
          />
        </div>
        <span className="text-[10px] text-[#6b6560] shrink-0">{Math.round(v.confidence * 100)}%</span>
      </div>
      <div className="flex items-center gap-3 mt-2 text-[10px] text-[#6b6560]">
        <span className="flex items-center gap-0.5"><Clock className="h-2.5 w-2.5" />{v.executionMs}ms</span>
        <span className="flex items-center gap-0.5"><Zap className="h-2.5 w-2.5" />{v.llmProvider}</span>
      </div>
    </motion.button>
  );
}

interface ExecutionPanelProps {
  result: SandboxExecutionResult;
}

export function ExecutionPanel({ result }: ExecutionPanelProps) {
  const { selectedValidatorIndex, selectValidator } = useSandboxStore();
  const selected = selectedValidatorIndex !== null ? result.validators[selectedValidatorIndex] : null;
  const outCfg = OUTCOME_CONFIG[result.finalOutcome];

  return (
    <div className="space-y-4 h-full overflow-y-auto pr-1">
      {/* Final outcome banner */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className={cn("rounded-xl border-2 px-4 py-3 flex items-center justify-between", outCfg.cls)}
      >
        <div>
          <p className="text-xs font-bold text-[#1a1a1a]">
            {outCfg.icon} {outCfg.label}
          </p>
          <p className="text-[11px] text-[#6b6560] mt-0.5">
            {result.contractName}.{result.functionCalled}("{result.input.slice(0, 40)}{result.input.length > 40 ? "…" : ""}")
          </p>
        </div>
        <div className="text-right shrink-0">
          <p className="text-[10px] text-[#6b6560]">{result.totalMs}ms total</p>
          <p className="text-[10px] text-[#6b6560]">{result.validators.length} validators</p>
        </div>
      </motion.div>

      {/* Equivalence result */}
      <div className="rounded-xl border border-[#d8d4c8] bg-white/60 px-4 py-3">
        <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-1.5">Equivalence Check</p>
        <div className="flex items-center gap-2 mb-2">
          <div className="flex-1 h-2 bg-[#e8e4da] rounded-full overflow-hidden">
            <div
              className={cn("h-full rounded-full", result.equivalence.passed ? "bg-green-500" : "bg-amber-500")}
              style={{ width: `${Math.round(result.equivalence.agreeingCount / result.equivalence.totalCount * 100)}%` }}
            />
          </div>
          <span className="text-xs font-bold text-[#1a1a1a]">
            {Math.round(result.equivalence.agreeingCount / result.equivalence.totalCount * 100)}%
          </span>
          <span className={cn("text-[10px] font-bold px-2 py-0.5 rounded-full", result.equivalence.passed ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700")}>
            {result.equivalence.passed ? "PASSED" : "FAILED"}
          </span>
        </div>
        {/* 60% threshold marker */}
        <div className="relative h-0 mb-1">
          <div className="absolute left-[60%] -translate-x-1/2 -top-5 text-[9px] text-[#6b6560]">60%</div>
          <div className="absolute left-[60%] -translate-x-1/2 -top-3 w-px h-3 bg-[#6b6560]/40" />
        </div>
        <p className="text-[11px] text-[#6b6560] leading-snug mt-1">{result.equivalence.explanation}</p>
      </div>

      {/* Validator cards grid */}
      <div>
        <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">Validator Votes</p>
        <div className="grid grid-cols-1 gap-2">
          {result.validators.map((v, i) => (
            <ValidatorCard
              key={i}
              v={v}
              index={i}
              isSelected={selectedValidatorIndex === i}
              onClick={() => selectValidator(selectedValidatorIndex === i ? null : i)}
            />
          ))}
        </div>
      </div>

      {/* Selected validator detail */}
      <AnimatePresence>
        {selected && (
          <motion.div
            key={selected.validatorIndex}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="rounded-xl border-2 border-[#2d2a26] bg-[#1a1a1a] p-4 space-y-3">
              <p className="text-xs font-bold text-[#efece4]">{selected.validatorName} — Detail</p>

              <div>
                <p className="text-[10px] text-[#5a5550] mb-1 font-mono">PROMPT SENT</p>
                <p className="text-[11px] text-[#d8d4c8] font-mono leading-snug bg-[#2d2a26] rounded px-2 py-2">
                  {selected.promptSent}
                </p>
              </div>

              <div>
                <p className="text-[10px] text-[#5a5550] mb-1 font-mono">LLM RESPONSE</p>
                <p className="text-xs text-green-400 font-mono">{selected.llmResponse}</p>
              </div>

              <div>
                <p className="text-[10px] text-[#5a5550] mb-1 font-mono">REASONING</p>
                <p className="text-[11px] text-[#c8c4bc] leading-snug">{selected.reasoning}</p>
              </div>

              {Object.keys(selected.stateAfter).length > 0 && (
                <div>
                  <p className="text-[10px] text-[#5a5550] mb-1 font-mono">STATE AFTER</p>
                  <div className="space-y-1">
                    {Object.entries(selected.stateAfter).map(([k, v]) => (
                      <div key={k} className="flex items-center gap-2 text-[11px] font-mono">
                        <span className="text-[#8080ff]">{k}</span>
                        <span className="text-[#5a5550]">=</span>
                        <span className="text-[#d8d4c8]">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 9. components/sandbox/SandboxConsole.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("components/sandbox/SandboxConsole.tsx", r'''
"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface SandboxConsoleProps {
  lines: string[];
  isRunning: boolean;
}

function colorize(line: string): string {
  return line; // passed as text, color via className logic
}

function getLineStyle(line: string): string {
  if (line.includes("[consensus]"))   return "text-purple-400";
  if (line.includes("[equivalence]")) return "text-blue-400";
  if (line.includes("[validator:"))   return "text-green-400";
  if (line.includes("[sandbox]"))     return "text-[#efece4]/80";
  if (line.includes("ERROR"))         return "text-red-400";
  return "text-[#8a8680]";
}

export function SandboxConsole({ lines, isRunning }: SandboxConsoleProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div className="h-full bg-[#141414] rounded-xl border border-[#2d2a26] overflow-hidden flex flex-col">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-[#2d2a26] bg-[#1a1a1a]">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-[#ff5f57]" />
          <div className="h-3 w-3 rounded-full bg-[#febc2e]" />
          <div className="h-3 w-3 rounded-full bg-[#28c840]" />
        </div>
        <span className="text-[11px] text-[#5a5550] font-mono ml-2">GenLayer Sandbox Console</span>
        {isRunning && (
          <span className="ml-auto flex items-center gap-1.5 text-[10px] text-green-400 font-mono">
            <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" />
            executing...
          </span>
        )}
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-3 font-mono text-[11px] leading-5 space-y-0.5">
        {lines.length === 0 ? (
          <p className="text-[#3a3530]">$ waiting for execution...</p>
        ) : (
          lines.map((line, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.03 }}
              className={cn("whitespace-pre-wrap break-all", getLineStyle(line))}
            >
              {line}
            </motion.div>
          ))
        )}
        {isRunning && (
          <div className="text-green-400 animate-pulse">▋</div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
'''.lstrip())

# ─────────────────────────────────────────────────────────────────────────────
# 10. app/(dashboard)/sandbox/page.tsx
# ─────────────────────────────────────────────────────────────────────────────
write("app/(dashboard)/sandbox/page.tsx", r'''
"use client";

import { useState, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { CONTRACT_TEMPLATES } from "@/lib/sandbox/templates";
import { executeSandboxContract } from "@/lib/sandbox/executor";
import { parseContract } from "@/lib/sandbox/parser";
import { useSandboxStore } from "@/store/sandboxStore";
import { CodeEditor } from "@/components/sandbox/CodeEditor";
import { TemplateSelector } from "@/components/sandbox/TemplateSelector";
import { ContractInspector } from "@/components/sandbox/ContractInspector";
import { ExecutionPanel } from "@/components/sandbox/ExecutionPanel";
import { SandboxConsole } from "@/components/sandbox/SandboxConsole";

const DEFAULT_CODE = CONTRACT_TEMPLATES[0].code;
const DEFAULT_INPUT = CONTRACT_TEMPLATES[0].defaultInput;

export default function SandboxPage() {
  const {
    code, activeTemplateId, functionInput, isRunning, currentResult, selectedValidatorIndex,
    setCode, setActiveTemplate, setFunctionInput, setIsRunning, setCurrentResult,
  } = useSandboxStore();

  const [consoleLines, setConsoleLines] = useState<string[]>([]);

  const effectiveCode = code || DEFAULT_CODE;
  const effectiveInput = functionInput || DEFAULT_INPUT;

  const parsed = useMemo(() => parseContract(effectiveCode), [effectiveCode]);

  // First write function (the one we execute)
  const writeFn = parsed.functions.find((f) => f.decorator === "@gl.public.write");

  async function handleRun() {
    if (!writeFn) return;
    setIsRunning(true);
    setConsoleLines([]);

    try {
      const result = await executeSandboxContract(
        effectiveCode,
        writeFn.name,
        effectiveInput
      );
      setCurrentResult(result);
      setConsoleLines(result.consoleLog);
    } catch (err) {
      setConsoleLines([`[ERROR] ${String(err)}`]);
    } finally {
      setIsRunning(false);
    }
  }

  function handleSelectTemplate(t: typeof CONTRACT_TEMPLATES[0]) {
    setCode(t.code);
    setFunctionInput(t.defaultInput);
    setActiveTemplate(t.id);
  }

  function handleReset() {
    setCode("");
    setFunctionInput("");
    setActiveTemplate(null);
    setConsoleLines([]);
  }

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-[1600px] px-4 py-6">

        {/* Header */}
        <div className="flex items-start justify-between mb-5">
          <div>
            <h1 className="text-2xl font-bold text-[#1a1a1a] tracking-tight mb-1">Developer Sandbox</h1>
            <p className="text-sm text-[#6b6560] max-w-xl leading-relaxed">
              Write Intelligent Contracts in Python, execute them through a simulated 5-validator
              GenLayer consensus, and watch the Equivalence Principle resolve non-deterministic LLM outputs in real time.
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0 ml-4">
            <Button variant="outline" size="sm" onClick={handleReset} className="gap-1.5">
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </Button>
            <Button
              size="sm"
              onClick={handleRun}
              disabled={isRunning || !writeFn}
              className="gap-1.5 bg-[#2d2a26] hover:bg-[#1a1a1a] text-[#efece4] min-w-[120px]"
            >
              {isRunning ? (
                <><span className="h-3.5 w-3.5 border-2 border-[#efece4]/40 border-t-[#efece4] rounded-full animate-spin" /> Running...</>
              ) : (
                <><Play className="h-3.5 w-3.5" /> Run Contract</>
              )}
            </Button>
          </div>
        </div>

        {/* Main layout: sidebar | editor | results */}
        <div className="grid grid-cols-[220px_1fr_380px] gap-4 h-[calc(100vh-160px)] min-h-[600px]">

          {/* LEFT — Template selector + Inspector */}
          <div className="flex flex-col gap-4 overflow-y-auto pr-1">
            <TemplateSelector
              activeId={activeTemplateId}
              onSelect={handleSelectTemplate}
            />
            <div className="border-t border-[#d8d4c8] pt-4">
              <p className="text-[11px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">Inspector</p>
              <ContractInspector code={effectiveCode} />
            </div>
          </div>

          {/* CENTER — Code editor + input bar */}
          <div className="flex flex-col gap-3 min-h-0">
            {/* Input bar */}
            <div className="flex items-center gap-2 bg-white/60 border border-[#d8d4c8] rounded-xl px-3 py-2">
              <div className="flex items-center gap-1.5 shrink-0">
                <span className="text-[10px] font-mono text-[#6b6560] bg-[#e8e4da] px-2 py-0.5 rounded">
                  {writeFn ? `${writeFn.name}(` : "no @write fn"}
                </span>
              </div>
              <input
                type="text"
                value={effectiveInput}
                onChange={(e) => setFunctionInput(e.target.value)}
                placeholder="Function input string..."
                disabled={isRunning}
                className="flex-1 text-xs bg-transparent outline-none text-[#1a1a1a] placeholder:text-[#b8b4a8] font-mono"
              />
              {writeFn && (
                <span className="text-[10px] font-mono text-[#6b6560] shrink-0">)</span>
              )}
              {!writeFn && (
                <span className="text-[10px] text-amber-600 shrink-0">
                  Add a @gl.public.write function to enable execution
                </span>
              )}
            </div>

            {/* Editor */}
            <div className="flex-1 min-h-0">
              <CodeEditor
                value={effectiveCode}
                onChange={setCode}
                disabled={isRunning}
              />
            </div>
          </div>

          {/* RIGHT — Results + Console */}
          <div className="flex flex-col min-h-0">
            <Tabs defaultValue="results" className="flex flex-col h-full">
              <TabsList className="mb-3 shrink-0">
                <TabsTrigger value="results">Results</TabsTrigger>
                <TabsTrigger value="console">Console</TabsTrigger>
              </TabsList>

              <TabsContent value="results" className="flex-1 overflow-hidden">
                {currentResult ? (
                  <ExecutionPanel result={currentResult} />
                ) : (
                  <div className="h-full rounded-xl border-2 border-dashed border-[#d8d4c8] flex flex-col items-center justify-center text-center px-6 py-12">
                    <div className="text-4xl mb-4">⚡</div>
                    <h3 className="text-sm font-bold text-[#1a1a1a] mb-2">No execution yet</h3>
                    <p className="text-xs text-[#6b6560] max-w-xs leading-relaxed">
                      Select a template or write your own contract, then click
                      <strong> Run Contract</strong> to see all 5 validators
                      execute and reach consensus.
                    </p>
                    <div className="mt-5 flex flex-col gap-1.5 text-left w-full max-w-[220px]">
                      {["5 validators execute in parallel", "Each calls its assigned LLM", "Equivalence Principle resolves votes", "Final outcome written on-chain"].map((step, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-[#6b6560]">
                          <span className="h-5 w-5 rounded-full bg-[#e8e4da] text-[10px] flex items-center justify-center font-bold shrink-0">{i + 1}</span>
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="console" className="flex-1 overflow-hidden">
                <SandboxConsole lines={consoleLines} isRunning={isRunning} />
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Educational callout */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          {[
            {
              icon: "🐍",
              title: "Python-native",
              body: "Write contracts in standard Python. The GenVM executes them with full access to the gl module — no Solidity or new languages to learn.",
            },
            {
              icon: "🤖",
              title: "gl.exec_prompt()",
              body: "Every call to gl.exec_prompt() reaches the validator's assigned LLM. Five validators = five independent AI calls, each potentially returning a different answer.",
            },
            {
              icon: "⚖️",
              title: "Equivalence resolves disagreements",
              body: "When validators disagree, the Equivalence Principle determines whether the spread of votes is acceptable. If not, an appeal is triggered automatically.",
            },
          ].map((card) => (
            <div key={card.title} className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
              <div className="text-2xl mb-2">{card.icon}</div>
              <h3 className="text-sm font-bold text-[#1a1a1a] mb-1">{card.title}</h3>
              <p className="text-xs text-[#6b6560] leading-relaxed">{card.body}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
'''.lstrip())

print("\nAll Phase 10 files written. Running build...\n")
result = subprocess.run(["npm", "run", "build"], cwd=ROOT, shell=True, capture_output=True, text=True)
print(result.stdout[-4000:] if len(result.stdout) > 4000 else result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
    sys.exit(1)
else:
    print("BUILD PASSED")
