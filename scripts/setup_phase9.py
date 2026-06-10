"""Phase 9: Learning Center — structured lessons, concept cards, interactive quizzes, progress tracking, glossary."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  WROTE  {rel}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Learning content data — lessons, concepts, glossary, quizzes
# ─────────────────────────────────────────────────────────────────────────────
w("lib/learn/content.ts", '''\
export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface Lesson {
  id: string;
  slug: string;
  title: string;
  subtitle: string;
  difficulty: Difficulty;
  estimatedMinutes: number;
  module: string;
  order: number;
  icon: string;
  sections: LessonSection[];
  relatedIds: string[];
  xpReward: number;
}

export interface LessonSection {
  heading: string;
  body: string;           // markdown-ish plain text
  codeBlock?: { lang: string; code: string };
  callout?: { type: "info" | "tip" | "warning"; text: string };
  keyPoints?: string[];
}

export interface QuizQuestion {
  id: string;
  lessonId: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface GlossaryTerm {
  term: string;
  definition: string;
  category: string;
  relatedTerms: string[];
}

// ── Lessons ──────────────────────────────────────────────────────────────────

export const LESSONS: Lesson[] = [
  {
    id: "l1",
    slug: "what-is-genlayer",
    title: "What is GenLayer?",
    subtitle: "AI-native Layer-1 blockchain fundamentals",
    difficulty: "beginner",
    estimatedMinutes: 5,
    module: "Foundations",
    order: 1,
    icon: "⚡",
    xpReward: 50,
    relatedIds: ["l2", "l3"],
    sections: [
      {
        heading: "GenLayer in one sentence",
        body: "GenLayer is an AI-native Layer-1 blockchain that lets developers write smart contracts — called Intelligent Contracts — in plain Python, with the ability to call LLMs directly from within contract code to resolve subjective on-chain decisions.",
        callout: { type: "info", text: "Unlike traditional smart contracts that can only execute deterministic logic, GenLayer contracts can ask questions to AI models and use the answers to drive on-chain state changes." },
      },
      {
        heading: "Why is this different?",
        body: "Traditional blockchains (Ethereum, Solana, etc.) require every node to execute the exact same deterministic computation and reach the exact same result. This works for token transfers and simple logic, but breaks down for subjective questions like:\n\n• Did the freelancer deliver quality work?\n• Is this product review authentic?\n• Was the event organised as promised?\n\nGenLayer solves this by turning subjective evaluation into a consensus problem across multiple AI validators.",
        keyPoints: [
          "Smart contracts are written in Python (not Solidity)",
          "Contracts can call LLMs via gl.exec_prompt()",
          "Multiple validators re-run the contract independently",
          "Disagreement is resolved by the Equivalence Principle",
        ],
      },
      {
        heading: "The GenVM",
        body: "GenLayer runs on the GenVM — the GenLayer Virtual Machine. It executes Python-based Intelligent Contracts in a sandboxed environment. Each validator runs its own GenVM instance, which is why validators can reach different results when LLM calls return different outputs.",
        codeBlock: {
          lang: "python",
          code: '# { "Depends": "py-genlayer:test" }\nfrom genlayer import *\n\nclass MyContract(gl.Contract):\n    result: str\n\n    @gl.public.write\n    def evaluate(self, question: str) -> None:\n        # This calls the validator\'s assigned LLM\n        answer = gl.exec_prompt(f"Answer YES or NO: {question}")\n        self.result = answer.strip()',
        },
      },
    ],
  },
  {
    id: "l2",
    slug: "intelligent-contracts",
    title: "Intelligent Contracts",
    subtitle: "Python contracts that reason with AI",
    difficulty: "beginner",
    estimatedMinutes: 7,
    module: "Foundations",
    order: 2,
    icon: "🧠",
    xpReward: 60,
    relatedIds: ["l1", "l3", "l4"],
    sections: [
      {
        heading: "What makes a contract Intelligent?",
        body: "An Intelligent Contract is a GenLayer smart contract that uses gl.exec_prompt() to invoke its validator's assigned LLM during execution. The result of that LLM call can alter contract state, making the contract capable of reasoning about subjective real-world information.",
      },
      {
        heading: "The two decorator types",
        body: "Every public function in an Intelligent Contract must use one of two decorators that determine how the function is executed and whether it triggers Optimistic Democracy:",
        keyPoints: [
          "@gl.public.view — Read-only. Runs on one node. No consensus required. Like Ethereum's view functions.",
          "@gl.public.write — State-changing. Triggers Optimistic Democracy. All validators re-execute independently.",
        ],
        codeBlock: {
          lang: "python",
          code: 'class FreelanceEscrow(gl.Contract):\n    payments: dict\n\n    @gl.public.view\n    def get_payment(self, job_id: str) -> dict:\n        # Read-only: just returns data, no consensus needed\n        return self.payments.get(job_id, {})\n\n    @gl.public.write\n    def evaluate_delivery(self, job_id: str, evidence: str) -> None:\n        # Write: triggers Optimistic Democracy\n        verdict = gl.exec_prompt(\n            f"Was this job completed as agreed?\\nEvidence: {evidence}\\nAnswer: ACCEPT or REJECT"\n        )\n        self.payments[job_id] = {"verdict": verdict.strip()}',
        },
      },
      {
        heading: "gl.exec_prompt() in depth",
        body: "gl.exec_prompt() is the core primitive that makes contracts Intelligent. It sends a prompt to the validator's assigned LLM and returns the response as a string. The response is then used in contract logic to determine state changes.\n\nKey behaviours:\n• Each validator calls its own LLM (Atlas → GPT-4o, Nova → Claude, etc.)\n• The same prompt can produce different responses from different LLMs\n• These differences are reconciled by the Equivalence Principle\n• Responses should be prompted to return structured output (ACCEPT/REJECT, a number, a score) for reliable parsing",
        callout: { type: "tip", text: "Always design your prompt to return a parseable output. Ask for 'ACCEPT or REJECT' rather than free text. The contract will need to process the response programmatically." },
      },
    ],
  },
  {
    id: "l3",
    slug: "optimistic-democracy",
    title: "Optimistic Democracy",
    subtitle: "How GenLayer reaches consensus on subjective claims",
    difficulty: "beginner",
    estimatedMinutes: 8,
    module: "Consensus",
    order: 3,
    icon: "🗳️",
    xpReward: 75,
    relatedIds: ["l2", "l4", "l5"],
    sections: [
      {
        heading: "The core idea",
        body: "Optimistic Democracy is GenLayer's consensus mechanism for write transactions. It works like a mini-democracy: a leader proposes a result, other validators confirm or reject it, and the Equivalence Principle determines whether consensus is reached. If no one objects during the finality window, the result is accepted optimistically.",
        callout: { type: "info", text: "The name combines two ideas: Optimistic (assume transactions are valid, challenge if not — like Optimistic Rollups) and Democracy (majority-based agreement with appeal rights)." },
      },
      {
        heading: "The five stages",
        body: "Every @gl.public.write transaction goes through five lifecycle stages:",
        keyPoints: [
          "1. Proposed — The leader validator executes the contract and submits a result",
          "2. Validator Review — All other validators independently re-execute the same contract",
          "3. Equivalence Check — Validator outputs are compared using the Equivalence Principle",
          "4. Finality Window — A challenge period opens (typically 5–10 blocks)",
          "5. Finalized — If no valid challenge arrives, the result is committed to the state tree",
        ],
      },
      {
        heading: "Leader selection",
        body: "The leader validator is selected deterministically for each transaction using a VRF (Verifiable Random Function). This prevents any single validator from always being the leader and ensures the selection is unpredictable but verifiable by all nodes.",
        callout: { type: "tip", text: "The leader's result is the proposed outcome. Other validators act as a check — they confirm the leader reached an equivalent conclusion using their own LLM." },
      },
    ],
  },
  {
    id: "l4",
    slug: "equivalence-principle",
    title: "The Equivalence Principle",
    subtitle: "Mathematical consensus for LLM outputs",
    difficulty: "intermediate",
    estimatedMinutes: 10,
    module: "Consensus",
    order: 4,
    icon: "⚖️",
    xpReward: 90,
    relatedIds: ["l3", "l5"],
    sections: [
      {
        heading: "Why not just compare strings?",
        body: "Different LLMs produce slightly different outputs even when asked the same question. GPT-4o might say \"ACCEPT\" and Claude might say \"Accept.\" — these are semantically identical but string-unequal. The Equivalence Principle handles this by comparing the semantic meaning and numerical closeness of outputs, not raw strings.",
      },
      {
        heading: "Comparative Equivalence",
        body: "Used when outputs are numerical or can be mapped to a 0–1 scale (confidence scores, price estimates, percentages). Validators' outputs must cluster within a defined margin around the mean. If enough validators fall within the band, equivalence is achieved.",
        keyPoints: [
          "Mean of all validator outputs is computed",
          "An equivalence band (margin) is defined by the contract",
          "Outputs within the band are considered equivalent",
          "If ≥60% of outputs are within the band, equivalence passes",
        ],
      },
      {
        heading: "Non-Comparative Equivalence",
        body: "Used when outputs are categorical (ACCEPT/REJECT, YES/NO, a label). Each validator independently checks whether their output meets the contract-defined criteria. No cross-validator comparison is needed — only a majority criterion match.",
        codeBlock: {
          lang: "python",
          code: '# Non-comparative: each validator checks independently\n@gl.public.write\ndef verify_review(self, review_text: str) -> None:\n    result = gl.exec_prompt(\n        f"""Is this product review genuine?\nReview: {review_text}\nAnswer GENUINE or FAKE only."""\n    )\n    # Each validator answers independently.\n    # If 3+ of 5 say GENUINE, equivalence passes.\n    self.verified = result.strip() == "GENUINE"',
        },
        callout: { type: "info", text: "The contract author chooses which equivalence mode to use by structuring their gl.exec_prompt() to return numerical scores (comparative) or categorical labels (non-comparative)." },
      },
    ],
  },
  {
    id: "l5",
    slug: "appeals-process",
    title: "The Appeals Process",
    subtitle: "What happens when validators can't agree",
    difficulty: "intermediate",
    estimatedMinutes: 8,
    module: "Consensus",
    order: 5,
    icon: "⚖️",
    xpReward: 80,
    relatedIds: ["l3", "l4", "l6"],
    sections: [
      {
        heading: "When equivalence fails",
        body: "If the Equivalence Principle check fails — meaning less than 60% of validators reached equivalent conclusions — an appeal is automatically triggered. The system does not simply reject the transaction; instead, it brings in more validators to re-evaluate.",
        callout: { type: "warning", text: "Appeals are not a sign of failure — they are a feature. Genuine ambiguity in a claim should produce genuine disagreement, and the appeals process ensures more perspectives are heard." },
      },
      {
        heading: "Validator expansion",
        body: "Each appeal round adds 3 new validators to the pool. Their votes are pooled with all previous rounds. The Equivalence Principle is re-applied across the full expanded set. This continues until consensus is reached or a maximum number of rounds is hit.",
        keyPoints: [
          "Round 1: 5 validators (initial set)",
          "Round 2: 5 + 3 = 8 validators",
          "Round 3: 5 + 3 + 3 = 11 validators",
          "Each round expands coverage and reduces the impact of any single outlier",
        ],
      },
      {
        heading: "Appeal staking",
        body: "In production GenLayer, appeals require a stake deposit from the challenging party. If the appeal succeeds (the outcome changes), the challenger is rewarded and the original validators who were wrong are slashed. This economic mechanism prevents frivolous appeals while protecting against genuine mistakes.",
        callout: { type: "tip", text: "In the simulator, appeals are free — we're focused on the mechanics rather than the economics. In production, you'd need to stake GEN tokens to trigger an appeal." },
      },
    ],
  },
  {
    id: "l6",
    slug: "validator-nodes",
    title: "Validator Nodes",
    subtitle: "The network participants who power consensus",
    difficulty: "intermediate",
    estimatedMinutes: 6,
    module: "Network",
    order: 6,
    icon: "🖥️",
    xpReward: 70,
    relatedIds: ["l3", "l5", "l7"],
    sections: [
      {
        heading: "What validators do",
        body: "Validators are the nodes that power the GenLayer network. Each validator:\n\n• Runs a GenVM instance to execute Intelligent Contracts\n• Is assigned a specific LLM (GPT-4o, Claude, Llama 3, etc.)\n• Participates in Optimistic Democracy for every write transaction\n• Earns staking rewards for correct, timely validation",
      },
      {
        heading: "LLM assignment",
        body: "Every validator is assigned a specific LLM model. This assignment is part of their stake registration. The diversity of LLM assignments across the validator network is what makes the Equivalence Principle meaningful — different models bring different perspectives, and consensus across them is a stronger signal than a single model's verdict.",
        keyPoints: [
          "Atlas → GPT-4o (OpenAI) — Analytical, methodical",
          "Nova → Claude 3.5 Sonnet (Anthropic) — Contextual, nuanced",
          "Orion → Llama 3 70B (Meta) — Strict, consistent",
          "Lyra → Mistral Large (Mistral AI) — Lenient, fast",
          "Zephyr → Gemini 1.5 Pro (Google) — Balanced, broad context",
        ],
      },
      {
        heading: "Staking and slashing",
        body: "Validators must stake GEN tokens to participate. Honest validators who reach correct consensus earn rewards. Validators who consistently disagree with the final outcome (outliers) are slashed. This economic incentive aligns validator behaviour with network accuracy.",
        callout: { type: "info", text: "The simulator uses the same 5 validator personas but simulates their behaviour deterministically. In production, real validators run real LLMs on real hardware with real economic stakes." },
      },
    ],
  },
  {
    id: "l7",
    slug: "writing-intelligent-contracts",
    title: "Writing Intelligent Contracts",
    subtitle: "Practical guide to building with GenLayer",
    difficulty: "advanced",
    estimatedMinutes: 15,
    module: "Development",
    order: 7,
    icon: "💻",
    xpReward: 120,
    relatedIds: ["l2", "l4", "l6"],
    sections: [
      {
        heading: "Contract structure",
        body: "Every Intelligent Contract follows the same structure: a dependency header comment, an import of the genlayer module, a class that inherits from gl.Contract, typed state variables as class attributes, and methods decorated with @gl.public.view or @gl.public.write.",
        codeBlock: {
          lang: "python",
          code: '# { "Depends": "py-genlayer:test" }\nfrom genlayer import *\n\nclass ConsensusSimulator(gl.Contract):\n    # Typed state variables\n    simulations: dict\n    total_count: int\n\n    def __init__(self):\n        self.simulations = {}\n        self.total_count = 0\n\n    @gl.public.view\n    def get_simulation(self, sim_id: str) -> dict:\n        return self.simulations.get(sim_id, {})\n\n    @gl.public.write\n    def evaluate_claim(self, sim_id: str, claim: str) -> None:\n        verdict = gl.exec_prompt(\n            f"Evaluate this claim and answer ACCEPT or REJECT only.\\n"\n            f"Claim: {claim}\\n"\n            f"Answer:"\n        )\n        self.simulations[sim_id] = {\n            "verdict": verdict.strip(),\n            "claim": claim\n        }\n        self.total_count += 1',
        },
      },
      {
        heading: "Designing prompts for consensus",
        body: "Prompt design is the most critical skill in Intelligent Contract development. Your prompt must:\n\n1. Produce output that can be parsed by contract code\n2. Be specific enough that different LLMs reach equivalent conclusions\n3. Include all relevant context (not just the claim, but the evaluation criteria)\n4. Specify the exact output format",
        keyPoints: [
          "Bad: 'What do you think of this freelancer's work?'",
          "Good: 'Did this freelancer meet all contract requirements? Answer ACCEPT or REJECT only.'",
          "Include the contract's success criteria in the prompt",
          "Test your prompt across multiple LLMs before deploying",
        ],
        callout: { type: "tip", text: "The more specific your prompt, the narrower the range of valid responses, and the more likely different LLMs will reach equivalent conclusions." },
      },
      {
        heading: "Deploying to GenLayer Studio",
        body: "GenLayer Studio is the browser-based IDE for Intelligent Contract development. You write, test, and deploy contracts entirely in the browser — no local toolchain required. The Studio runs on the Asimov Testnet, which uses the same validator logic as mainnet.",
        keyPoints: [
          "Visit studio.genlayer.com",
          "Write your contract in the Python editor",
          "Use the built-in simulator to test across validator nodes",
          "Deploy to the Asimov Testnet with one click",
          "Interact with deployed contracts via the transaction panel",
        ],
      },
    ],
  },
];

// ── Quiz Questions ────────────────────────────────────────────────────────────

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  { id: "q1", lessonId: "l1", question: "What language are GenLayer Intelligent Contracts written in?", options: ["Solidity", "Rust", "Python", "JavaScript"], correctIndex: 2, explanation: "GenLayer Intelligent Contracts are written in Python and executed by the GenVM (GenLayer Virtual Machine)." },
  { id: "q2", lessonId: "l1", question: "What does gl.exec_prompt() do?", options: ["Deploys a contract", "Calls the validator's assigned LLM", "Transfers tokens", "Signs a transaction"], correctIndex: 1, explanation: "gl.exec_prompt() sends a prompt to the validator's assigned LLM and returns the response as a string." },
  { id: "q3", lessonId: "l2", question: "Which decorator triggers Optimistic Democracy?", options: ["@gl.public.view", "@gl.public.write", "@gl.public.call", "@gl.public.query"], correctIndex: 1, explanation: "@gl.public.write triggers Optimistic Democracy because it changes contract state — all validators must independently verify the result." },
  { id: "q4", lessonId: "l2", question: "How many validators re-execute a @gl.public.write function?", options: ["Only the leader", "Two validators", "All active validators", "A random sample"], correctIndex: 2, explanation: "All active validators independently re-execute @gl.public.write functions to ensure consensus." },
  { id: "q5", lessonId: "l3", question: "What is the default minimum agreement threshold in Optimistic Democracy?", options: ["50%", "60%", "75%", "100%"], correctIndex: 1, explanation: "The Equivalence Principle requires at least 60% of validators to agree for consensus to pass." },
  { id: "q6", lessonId: "l3", question: "What happens during the Finality Window?", options: ["Validators vote", "LLMs generate responses", "Anyone can challenge the outcome", "The contract is deployed"], correctIndex: 2, explanation: "During the finality window, any stakeholder can challenge the outcome. If no valid challenge arrives, the result is committed." },
  { id: "q7", lessonId: "l4", question: "When is Comparative Equivalence used?", options: ["When outputs are text", "When outputs are numerical or scalable", "When outputs are images", "When there is only one validator"], correctIndex: 1, explanation: "Comparative Equivalence is used when outputs can be mapped to a numerical scale and compared by closeness." },
  { id: "q8", lessonId: "l4", question: "In Non-Comparative Equivalence, how are outputs evaluated?", options: ["Compared to the mean", "Compared to each other", "Each output independently checks criteria", "Only the leader's output counts"], correctIndex: 2, explanation: "In Non-Comparative mode, each validator independently checks if its output meets the contract-defined criteria." },
  { id: "q9", lessonId: "l5", question: "How many new validators are added per appeal round?", options: ["1", "2", "3", "5"], correctIndex: 2, explanation: "Each appeal round adds 3 new validators to the pool, expanding coverage and reducing any single model's influence." },
  { id: "q10", lessonId: "l5", question: "What happens to validators who consistently disagree with the final outcome?", options: ["They earn a bonus", "They are removed from the network", "They are slashed", "Nothing happens"], correctIndex: 2, explanation: "Validators who consistently disagree with the network consensus are slashed — they lose a portion of their stake." },
  { id: "q11", lessonId: "l6", question: "Which LLM does the Atlas validator use?", options: ["Claude 3.5 Sonnet", "GPT-4o", "Llama 3 70B", "Gemini 1.5 Pro"], correctIndex: 1, explanation: "Atlas uses GPT-4o from OpenAI for its methodical, data-driven analytical evaluation style." },
  { id: "q12", lessonId: "l7", question: "What should a well-designed gl.exec_prompt() return?", options: ["Free-form prose", "Structured parseable output", "JSON objects only", "Numeric values only"], correctIndex: 1, explanation: "Prompts should be designed to return structured, parseable output (like ACCEPT/REJECT or a score) so contract code can process it reliably." },
];

// ── Glossary ──────────────────────────────────────────────────────────────────

export const GLOSSARY_TERMS: GlossaryTerm[] = [
  { term: "Intelligent Contract", definition: "A GenLayer smart contract written in Python that can call LLMs via gl.exec_prompt() to perform subjective reasoning as part of its on-chain logic.", category: "Core Concepts", relatedTerms: ["GenVM", "gl.exec_prompt()", "Optimistic Democracy"] },
  { term: "Optimistic Democracy", definition: "GenLayer's consensus mechanism for write transactions. Assumes validity optimistically, runs independent validator checks, and opens a challenge window before finalizing.", category: "Consensus", relatedTerms: ["Equivalence Principle", "Finality Window", "Leader Validator"] },
  { term: "Equivalence Principle", definition: "The mathematical rule that determines whether different LLM outputs from different validators are considered 'equivalent enough' to constitute consensus.", category: "Consensus", relatedTerms: ["Comparative Equivalence", "Non-Comparative Equivalence", "Agreement Threshold"] },
  { term: "Comparative Equivalence", definition: "Equivalence mode for numerical outputs. Validators' outputs must cluster within a defined margin around the mean.", category: "Consensus", relatedTerms: ["Equivalence Principle", "Non-Comparative Equivalence"] },
  { term: "Non-Comparative Equivalence", definition: "Equivalence mode for categorical outputs. Each validator independently checks if its output meets contract-defined criteria.", category: "Consensus", relatedTerms: ["Equivalence Principle", "Comparative Equivalence"] },
  { term: "gl.exec_prompt()", definition: "The GenLayer built-in function that sends a prompt to the validator's assigned LLM and returns the response as a string.", category: "Development", relatedTerms: ["Intelligent Contract", "GenVM", "Validator Node"] },
  { term: "GenVM", definition: "The GenLayer Virtual Machine — a sandboxed Python runtime that executes Intelligent Contracts on each validator node.", category: "Core Concepts", relatedTerms: ["Intelligent Contract", "Validator Node"] },
  { term: "Leader Validator", definition: "The validator selected to propose the initial result for a write transaction. Selected deterministically via VRF for each transaction.", category: "Network", relatedTerms: ["Validator Node", "Optimistic Democracy", "VRF"] },
  { term: "Finality Window", definition: "A period of blocks after validators reach consensus during which any stakeholder can challenge the outcome before it is committed.", category: "Consensus", relatedTerms: ["Optimistic Democracy", "Appeal"] },
  { term: "Appeal", definition: "A mechanism to re-open consensus when the Equivalence Principle fails. Adds 3 new validators per round until consensus is reached.", category: "Consensus", relatedTerms: ["Finality Window", "Equivalence Principle", "Validator Expansion"] },
  { term: "Staking", definition: "Validators must lock GEN tokens as collateral to participate in validation. Honest validators earn rewards; dishonest ones are slashed.", category: "Economics", relatedTerms: ["Slashing", "Validator Node", "GEN Token"] },
  { term: "Slashing", definition: "The process of reducing a validator's stake when it consistently disagrees with network consensus or behaves dishonestly.", category: "Economics", relatedTerms: ["Staking", "Validator Node"] },
  { term: "Asimov Testnet", definition: "GenLayer's public testnet (GenLayer Studio Net). Used for developing and testing Intelligent Contracts before mainnet deployment.", category: "Network", relatedTerms: ["GenLayer Studio", "Intelligent Contract"] },
  { term: "GenLayer Studio", definition: "The browser-based IDE for Intelligent Contract development. Provides a Python editor, simulator, and one-click deployment to Asimov Testnet.", category: "Development", relatedTerms: ["Asimov Testnet", "Intelligent Contract"] },
  { term: "VRF", definition: "Verifiable Random Function — used in GenLayer to select the leader validator deterministically and unpredictably for each transaction.", category: "Network", relatedTerms: ["Leader Validator", "Validator Node"] },
  { term: "genlayer-js", definition: "The TypeScript/JavaScript SDK for interacting with deployed GenLayer contracts from frontend applications.", category: "Development", relatedTerms: ["GenLayer Studio", "Intelligent Contract"] },
];
''')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Learn progress store
# ─────────────────────────────────────────────────────────────────────────────
w("store/learnStore.ts", '''\
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface LearnStore {
  completedLessonIds: string[];
  quizResults: Record<string, { score: number; total: number; completedAt: number }>;
  totalXp: number;

  markLessonComplete: (id: string, xpReward: number) => void;
  saveQuizResult: (lessonId: string, score: number, total: number) => void;
  isLessonComplete: (id: string) => boolean;
  getQuizResult: (lessonId: string) => { score: number; total: number; completedAt: number } | null;
  resetProgress: () => void;
}

export const useLearnStore = create<LearnStore>()(
  persist(
    (set, get) => ({
      completedLessonIds: [],
      quizResults: {},
      totalXp: 0,

      markLessonComplete: (id, xpReward) =>
        set((s) => {
          if (s.completedLessonIds.includes(id)) return s;
          return {
            completedLessonIds: [...s.completedLessonIds, id],
            totalXp: s.totalXp + xpReward,
          };
        }),

      saveQuizResult: (lessonId, score, total) =>
        set((s) => ({
          quizResults: { ...s.quizResults, [lessonId]: { score, total, completedAt: Date.now() } },
        })),

      isLessonComplete: (id) => get().completedLessonIds.includes(id),

      getQuizResult: (lessonId) => get().quizResults[lessonId] ?? null,

      resetProgress: () => set({ completedLessonIds: [], quizResults: {}, totalXp: 0 }),
    }),
    { name: "learn-progress-store" }
  )
);
''')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Lesson Card component
# ─────────────────────────────────────────────────────────────────────────────
w("components/learn/LessonCard.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { Clock, Star, CheckCircle2, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { Lesson, Difficulty } from "@/lib/learn/content";

interface LessonCardProps {
  lesson: Lesson;
  isComplete: boolean;
  quizScore: number | null;
  isLocked?: boolean;
  onClick: () => void;
  index: number;
}

const DIFF_CFG: Record<Difficulty, { label: string; cls: string }> = {
  beginner:     { label: "Beginner",     cls: "bg-green-100 text-green-700" },
  intermediate: { label: "Intermediate", cls: "bg-amber-100 text-amber-700" },
  advanced:     { label: "Advanced",     cls: "bg-red-100 text-red-700" },
};

export function LessonCard({ lesson, isComplete, quizScore, isLocked, onClick, index }: LessonCardProps) {
  const diff = DIFF_CFG[lesson.difficulty];

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      onClick={!isLocked ? onClick : undefined}
      className={cn(
        "rounded-xl border-2 p-5 transition-all duration-200",
        isLocked  ? "border-[#e8e4da] bg-white/30 opacity-60 cursor-not-allowed" :
        isComplete ? "border-green-200 bg-green-50/50 cursor-pointer hover:shadow-md" :
                    "border-[#d8d4c8] bg-white/60 cursor-pointer hover:border-[#b8b4a8] hover:shadow-sm"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{lesson.icon}</span>
          <div>
            <h3 className="text-sm font-bold text-[#1a1a1a] leading-tight">{lesson.title}</h3>
            <p className="text-xs text-[#6b6560] mt-0.5">{lesson.subtitle}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0 ml-2">
          {isLocked    && <Lock className="h-4 w-4 text-[#d8d4c8]" />}
          {isComplete  && <CheckCircle2 className="h-5 w-5 text-green-500" />}
        </div>
      </div>

      {/* Badges */}
      <div className="flex items-center gap-2 flex-wrap mb-3">
        <span className={cn("text-[10px] font-semibold px-2 py-0.5 rounded-full", diff.cls)}>
          {diff.label}
        </span>
        <span className="text-[10px] text-[#6b6560] flex items-center gap-1">
          <Clock className="h-2.5 w-2.5" /> {lesson.estimatedMinutes} min
        </span>
        <span className="text-[10px] text-[#6b6560] flex items-center gap-1">
          <Star className="h-2.5 w-2.5 text-amber-400" /> {lesson.xpReward} XP
        </span>
        <Badge variant="secondary" className="text-[9px] px-1.5 py-0">{lesson.module}</Badge>
      </div>

      {/* Quiz score */}
      {quizScore !== null && (
        <div className="mt-2 pt-2 border-t border-[#e8e4da]">
          <p className="text-[10px] text-[#6b6560]">
            Quiz: <span className={cn("font-semibold", quizScore >= 0.7 ? "text-green-600" : "text-amber-600")}>
              {Math.round(quizScore * 100)}%
            </span>
          </p>
        </div>
      )}
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Lesson Viewer (full lesson with sections)
# ─────────────────────────────────────────────────────────────────────────────
w("components/learn/LessonViewer.tsx", '''\
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, CheckCircle2, Star, Clock, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useLearnStore } from "@/store/learnStore";
import { QuizPanel } from "./QuizPanel";
import { QUIZ_QUESTIONS, type Lesson } from "@/lib/learn/content";

interface LessonViewerProps {
  lesson: Lesson;
  onBack: () => void;
}

export function LessonViewer({ lesson, onBack }: LessonViewerProps) {
  const { markLessonComplete, isLessonComplete } = useLearnStore();
  const [showQuiz, setShowQuiz] = useState(false);
  const [readSection, setReadSection] = useState(0);

  const lessonQuestions = QUIZ_QUESTIONS.filter((q) => q.lessonId === lesson.id);
  const isComplete = isLessonComplete(lesson.id);

  function handleSectionComplete() {
    if (readSection < lesson.sections.length - 1) {
      setReadSection(readSection + 1);
    } else if (lessonQuestions.length > 0) {
      setShowQuiz(true);
    } else {
      markLessonComplete(lesson.id, lesson.xpReward);
    }
  }

  if (showQuiz) {
    return (
      <QuizPanel
        lesson={lesson}
        questions={lessonQuestions}
        onComplete={() => {
          markLessonComplete(lesson.id, lesson.xpReward);
          setShowQuiz(false);
        }}
        onBack={() => setShowQuiz(false)}
      />
    );
  }

  const section = lesson.sections[readSection];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="max-w-2xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Button variant="ghost" size="sm" className="h-8 px-2" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-lg">{lesson.icon}</span>
            <h2 className="text-base font-bold text-[#1a1a1a] truncate">{lesson.title}</h2>
            {isComplete && <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />}
          </div>
          <div className="flex items-center gap-3 text-[11px] text-[#6b6560]">
            <span className="flex items-center gap-1"><Clock className="h-2.5 w-2.5" />{lesson.estimatedMinutes} min</span>
            <span className="flex items-center gap-1"><Star className="h-2.5 w-2.5 text-amber-400" />{lesson.xpReward} XP</span>
            <Badge variant="secondary" className="text-[9px] px-1.5 py-0">{lesson.module}</Badge>
          </div>
        </div>
      </div>

      {/* Section progress dots */}
      <div className="flex items-center gap-1.5 mb-6">
        {lesson.sections.map((_, i) => (
          <div key={i} className={cn(
            "h-1.5 rounded-full transition-all duration-300",
            i < readSection  ? "bg-[#2d2a26] flex-1" :
            i === readSection ? "bg-[#2d2a26] flex-[2]" :
                                "bg-[#e8e4da] flex-1"
          )} />
        ))}
      </div>

      {/* Section content */}
      <motion.div
        key={readSection}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-5"
      >
        <h3 className="text-lg font-bold text-[#1a1a1a]">{section.heading}</h3>

        <p className="text-sm text-[#1a1a1a] leading-relaxed whitespace-pre-line">{section.body}</p>

        {section.callout && (
          <div className={cn(
            "rounded-xl border-l-4 px-4 py-3 text-sm leading-relaxed",
            section.callout.type === "info"    && "border-blue-400 bg-blue-50 text-blue-800",
            section.callout.type === "tip"     && "border-green-400 bg-green-50 text-green-800",
            section.callout.type === "warning" && "border-amber-400 bg-amber-50 text-amber-800",
          )}>
            <span className="font-semibold">
              {section.callout.type === "info" ? "ℹ️ " : section.callout.type === "tip" ? "💡 " : "⚠️ "}
            </span>
            {section.callout.text}
          </div>
        )}

        {section.keyPoints && (
          <ul className="space-y-2">
            {section.keyPoints.map((point, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-[#1a1a1a]">
                <span className="h-5 w-5 rounded-full bg-[#2d2a26] text-[#efece4] text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                {point}
              </li>
            ))}
          </ul>
        )}

        {section.codeBlock && (
          <div className="rounded-xl bg-[#1a1a1a] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 bg-[#2d2a26]">
              <span className="text-[11px] text-[#efece4]/60 font-mono">{section.codeBlock.lang}</span>
              <span className="text-[11px] text-[#efece4]/40">Intelligent Contract Example</span>
            </div>
            <pre className="px-4 py-4 text-xs text-[#efece4] overflow-x-auto leading-relaxed font-mono">
              {section.codeBlock.code}
            </pre>
          </div>
        )}
      </motion.div>

      <Separator className="my-6" />

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-[#6b6560]">
          Section {readSection + 1} of {lesson.sections.length}
        </span>
        <Button onClick={handleSectionComplete} className="gap-2">
          {readSection < lesson.sections.length - 1 ? (
            <><ChevronRight className="h-4 w-4" /> Next section</>
          ) : lessonQuestions.length > 0 ? (
            <><Star className="h-4 w-4" /> Take quiz ({lesson.xpReward} XP)</>
          ) : (
            <><CheckCircle2 className="h-4 w-4" /> Complete lesson</>
          )}
        </Button>
      </div>
    </motion.div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 5. Quiz Panel
# ─────────────────────────────────────────────────────────────────────────────
w("components/learn/QuizPanel.tsx", '''\
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, ArrowLeft, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useLearnStore } from "@/store/learnStore";
import type { Lesson, QuizQuestion } from "@/lib/learn/content";

interface QuizPanelProps {
  lesson: Lesson;
  questions: QuizQuestion[];
  onComplete: () => void;
  onBack: () => void;
}

export function QuizPanel({ lesson, questions, onComplete, onBack }: QuizPanelProps) {
  const { saveQuizResult } = useLearnStore();
  const [current, setCurrent]   = useState(0);
  const [answers, setAnswers]   = useState<(number | null)[]>(Array(questions.length).fill(null));
  const [revealed, setRevealed] = useState(false);
  const [finished, setFinished] = useState(false);

  const q = questions[current];
  const selected = answers[current];

  function handleSelect(idx: number) {
    if (revealed) return;
    setAnswers((prev) => { const n = [...prev]; n[current] = idx; return n; });
  }

  function handleReveal() { setRevealed(true); }

  function handleNext() {
    if (current < questions.length - 1) {
      setCurrent(current + 1);
      setRevealed(false);
    } else {
      const score = answers.filter((a, i) => a === questions[i].correctIndex).length;
      saveQuizResult(lesson.id, score, questions.length);
      setFinished(true);
    }
  }

  if (finished) {
    const score = answers.filter((a, i) => a === questions[i].correctIndex).length;
    const pct   = Math.round((score / questions.length) * 100);
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg mx-auto text-center py-12"
      >
        <Trophy className={cn("h-14 w-14 mx-auto mb-4", pct >= 70 ? "text-amber-400" : "text-[#d8d4c8]")} />
        <h2 className="text-2xl font-bold text-[#1a1a1a] mb-2">
          {pct >= 90 ? "Excellent!" : pct >= 70 ? "Well done!" : "Keep studying!"}
        </h2>
        <p className="text-4xl font-bold text-[#1a1a1a] my-4">{pct}%</p>
        <p className="text-sm text-[#6b6560] mb-6">
          {score}/{questions.length} correct · {lesson.xpReward} XP earned
        </p>
        <div className="space-y-2">
          {questions.map((q, i) => {
            const correct = answers[i] === q.correctIndex;
            return (
              <div key={q.id} className={cn(
                "flex items-start gap-2 text-left rounded-lg p-3 text-xs",
                correct ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"
              )}>
                {correct ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0 mt-0.5" /> : <XCircle className="h-3.5 w-3.5 text-red-500 shrink-0 mt-0.5" />}
                <div>
                  <p className="font-medium text-[#1a1a1a]">{q.question}</p>
                  {!correct && <p className="text-[#6b6560] mt-0.5">{q.explanation}</p>}
                </div>
              </div>
            );
          })}
        </div>
        <Button className="mt-6 w-full" onClick={onComplete}>
          <CheckCircle2 className="h-4 w-4 mr-2" /> Complete Lesson
        </Button>
      </motion.div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Button variant="ghost" size="sm" className="h-8 px-2" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider">Quiz · {lesson.title}</p>
          <p className="text-xs text-[#6b6560]">Question {current + 1} of {questions.length}</p>
        </div>
      </div>

      {/* Progress */}
      <div className="flex gap-1 mb-6">
        {questions.map((_, i) => (
          <div key={i} className={cn("h-1 flex-1 rounded-full", i < current ? "bg-[#2d2a26]" : i === current ? "bg-[#2d2a26]/50" : "bg-[#e8e4da]")} />
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={current}
          initial={{ opacity: 0, x: 16 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -16 }}
          className="space-y-5"
        >
          <h3 className="text-base font-semibold text-[#1a1a1a] leading-relaxed">{q.question}</h3>

          <div className="space-y-2">
            {q.options.map((opt, i) => {
              const isSelected = selected === i;
              const isCorrect  = i === q.correctIndex;
              return (
                <button key={i} onClick={() => handleSelect(i)}
                  className={cn(
                    "w-full text-left rounded-xl border-2 px-4 py-3 text-sm transition-all",
                    !revealed && isSelected && "border-[#2d2a26] bg-[#2d2a26] text-[#efece4]",
                    !revealed && !isSelected && "border-[#d8d4c8] bg-white/60 hover:border-[#b8b4a8]",
                    revealed  && isCorrect  && "border-green-400 bg-green-50 text-green-800",
                    revealed  && isSelected && !isCorrect && "border-red-400 bg-red-50 text-red-800",
                    revealed  && !isSelected && !isCorrect && "border-[#e8e4da] bg-white/30 text-[#6b6560]",
                  )}
                >
                  <span className="font-medium mr-2">{String.fromCharCode(65 + i)}.</span>
                  {opt}
                </button>
              );
            })}
          </div>

          {revealed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-xs text-blue-800 leading-relaxed"
            >
              <span className="font-semibold">Explanation: </span>{q.explanation}
            </motion.div>
          )}

          <div className="flex gap-2">
            {selected !== null && !revealed && (
              <Button variant="outline" className="flex-1" onClick={handleReveal}>Check Answer</Button>
            )}
            {revealed && (
              <Button className="flex-1" onClick={handleNext}>
                {current < questions.length - 1 ? "Next Question" : "See Results"}
              </Button>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Glossary component
# ─────────────────────────────────────────────────────────────────────────────
w("components/learn/Glossary.tsx", '''\
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { GLOSSARY_TERMS } from "@/lib/learn/content";

export function Glossary() {
  const [query,    setQuery]    = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  const categories = [...new Set(GLOSSARY_TERMS.map((t) => t.category))].sort();
  const filtered   = GLOSSARY_TERMS.filter((t) =>
    !query || t.term.toLowerCase().includes(query.toLowerCase()) || t.definition.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#6b6560]" />
        <input
          type="text"
          placeholder="Search terms…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-[#d8d4c8] bg-white/60 text-sm text-[#1a1a1a] placeholder:text-[#6b6560] focus:outline-none focus:ring-2 focus:ring-[#2d2a26]/20"
        />
      </div>

      {/* Terms by category */}
      {(query ? ["Search Results"] : categories).map((cat) => {
        const terms = query
          ? filtered
          : filtered.filter((t) => t.category === cat);
        if (terms.length === 0) return null;

        return (
          <div key={cat}>
            {!query && (
              <p className="text-[10px] font-semibold text-[#6b6560] uppercase tracking-wider mb-2">{cat}</p>
            )}
            <div className="space-y-1.5">
              {terms.map((term) => (
                <div key={term.term} className="rounded-xl border border-[#d8d4c8] bg-white/60 overflow-hidden">
                  <button
                    onClick={() => setExpanded(expanded === term.term ? null : term.term)}
                    className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-[#f5f2ec] transition-colors"
                  >
                    <span className="text-sm font-semibold text-[#1a1a1a]">{term.term}</span>
                    <ChevronDown className={cn("h-4 w-4 text-[#6b6560] transition-transform shrink-0", expanded === term.term && "rotate-180")} />
                  </button>
                  <AnimatePresence>
                    {expanded === term.term && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: "auto" }}
                        exit={{ height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="px-4 pb-4 border-t border-[#e8e4da] pt-3">
                          <p className="text-xs text-[#6b6560] leading-relaxed">{term.definition}</p>
                          {term.relatedTerms.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-1.5">
                              <span className="text-[10px] text-[#6b6560]">Related:</span>
                              {term.relatedTerms.map((r) => (
                                <button key={r} onClick={() => setExpanded(r)}
                                  className="text-[10px] text-indigo-600 hover:underline">{r}</button>
                              ))}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 7. Progress Bar component
# ─────────────────────────────────────────────────────────────────────────────
w("components/learn/ProgressBar.tsx", '''\
"use client";

import { motion } from "framer-motion";
import { Star, BookOpen, Trophy } from "lucide-react";
import { LESSONS } from "@/lib/learn/content";
import { useLearnStore } from "@/store/learnStore";

export function LearningProgress() {
  const { completedLessonIds, totalXp, quizResults } = useLearnStore();
  const total     = LESSONS.length;
  const completed = completedLessonIds.length;
  const pct       = Math.round((completed / total) * 100);
  const quizCount = Object.keys(quizResults).length;

  const maxXp = LESSONS.reduce((s, l) => s + l.xpReward, 0);
  const level  = Math.floor(totalXp / 100) + 1;

  return (
    <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-sm font-bold text-[#1a1a1a]">Your Progress</p>
          <p className="text-xs text-[#6b6560]">Level {level} learner</p>
        </div>
        <div className="flex items-center gap-1.5 bg-amber-50 border border-amber-200 rounded-full px-3 py-1">
          <Star className="h-3.5 w-3.5 text-amber-500" />
          <span className="text-xs font-bold text-amber-700">{totalXp} XP</span>
        </div>
      </div>

      {/* Overall progress */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-[#6b6560] mb-1.5">
          <span>Lessons completed</span>
          <span className="font-semibold text-[#1a1a1a]">{completed}/{total}</span>
        </div>
        <div className="h-3 rounded-full bg-[#e8e4da] overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="h-full rounded-full bg-[#2d2a26]"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          { icon: BookOpen, label: "Completed",    value: completed },
          { icon: Star,     label: "Quizzes done", value: quizCount },
          { icon: Trophy,   label: "Total XP",     value: totalXp },
        ].map((s) => (
          <div key={s.label} className="rounded-lg bg-[#f5f2ec] p-2.5">
            <s.icon className="h-4 w-4 text-[#6b6560] mx-auto mb-1" />
            <p className="text-sm font-bold text-[#1a1a1a]">{s.value}</p>
            <p className="text-[10px] text-[#6b6560]">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 8. Learning Center Page
# ─────────────────────────────────────────────────────────────────────────────
w("app/(dashboard)/learn/page.tsx", '''\
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LESSONS } from "@/lib/learn/content";
import { useLearnStore } from "@/store/learnStore";
import { LessonCard } from "@/components/learn/LessonCard";
import { LessonViewer } from "@/components/learn/LessonViewer";
import { Glossary } from "@/components/learn/Glossary";
import { LearningProgress } from "@/components/learn/ProgressBar";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-react";

const MODULES = [...new Set(LESSONS.map((l) => l.module))];

export default function LearnPage() {
  const { isLessonComplete, getQuizResult, resetProgress, completedLessonIds } = useLearnStore();
  const [activeLessonId, setActiveLessonId] = useState<string | null>(null);
  const [moduleFilter,   setModuleFilter]   = useState<string>("All");

  const activeLesson = LESSONS.find((l) => l.id === activeLessonId) ?? null;

  if (activeLesson) {
    return (
      <div className="min-h-screen bg-[#efece4]">
        <div className="mx-auto max-w-3xl px-6 py-8">
          <LessonViewer lesson={activeLesson} onBack={() => setActiveLessonId(null)} />
        </div>
      </div>
    );
  }

  const filteredLessons = moduleFilter === "All"
    ? LESSONS
    : LESSONS.filter((l) => l.module === moduleFilter);

  return (
    <div className="min-h-screen bg-[#efece4]">
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#1a1a1a] tracking-tight mb-2">Learning Center</h1>
          <p className="text-[#6b6560] text-sm max-w-2xl leading-relaxed">
            Master GenLayer, Intelligent Contracts, Optimistic Democracy, and the Equivalence Principle
            through structured lessons, code examples, and interactive quizzes.
          </p>
        </div>

        <Tabs defaultValue="lessons">
          <TabsList className="mb-6">
            <TabsTrigger value="lessons">Lessons</TabsTrigger>
            <TabsTrigger value="glossary">Glossary</TabsTrigger>
            <TabsTrigger value="progress">My Progress</TabsTrigger>
          </TabsList>

          {/* ── Lessons tab ── */}
          <TabsContent value="lessons">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

              {/* Sidebar */}
              <div className="lg:col-span-1 space-y-4">
                <LearningProgress />

                {/* Module filter */}
                <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-4">
                  <p className="text-xs font-semibold text-[#6b6560] uppercase tracking-wider mb-3">Filter by Module</p>
                  <div className="space-y-1">
                    {["All", ...MODULES].map((mod) => (
                      <button key={mod} onClick={() => setModuleFilter(mod)}
                        className={`w-full text-left text-xs px-3 py-2 rounded-lg transition-all ${
                          moduleFilter === mod
                            ? "bg-[#2d2a26] text-[#efece4] font-medium"
                            : "text-[#6b6560] hover:bg-[#e8e4da]"
                        }`}>
                        {mod}
                      </button>
                    ))}
                  </div>
                </div>

                {completedLessonIds.length > 0 && (
                  <Button variant="ghost" size="sm" className="w-full text-xs text-[#6b6560] hover:text-red-500 h-8"
                    onClick={resetProgress}>
                    <RotateCcw className="h-3 w-3 mr-1" /> Reset Progress
                  </Button>
                )}
              </div>

              {/* Lesson grid */}
              <div className="lg:col-span-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {filteredLessons.map((lesson, i) => {
                    const qr = getQuizResult(lesson.id);
                    return (
                      <LessonCard
                        key={lesson.id}
                        lesson={lesson}
                        isComplete={isLessonComplete(lesson.id)}
                        quizScore={qr ? qr.score / qr.total : null}
                        onClick={() => setActiveLessonId(lesson.id)}
                        index={i}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
          </TabsContent>

          {/* ── Glossary tab ── */}
          <TabsContent value="glossary">
            <div className="max-w-2xl">
              <Glossary />
            </div>
          </TabsContent>

          {/* ── Progress tab ── */}
          <TabsContent value="progress">
            <div className="max-w-lg space-y-5">
              <LearningProgress />

              <div className="rounded-xl border border-[#d8d4c8] bg-white/60 p-5">
                <p className="text-sm font-semibold text-[#1a1a1a] mb-4">Lesson Completion</p>
                <div className="space-y-2">
                  {LESSONS.map((lesson) => {
                    const done = isLessonComplete(lesson.id);
                    const qr   = getQuizResult(lesson.id);
                    return (
                      <div key={lesson.id} className="flex items-center justify-between py-2 border-b border-[#e8e4da] last:border-0">
                        <div className="flex items-center gap-2">
                          <span className="text-base">{lesson.icon}</span>
                          <div>
                            <p className="text-xs font-medium text-[#1a1a1a]">{lesson.title}</p>
                            <p className="text-[10px] text-[#6b6560]">{lesson.module} · {lesson.xpReward} XP</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-[10px]">
                          {qr && (
                            <span className={qr.score / qr.total >= 0.7 ? "text-green-600 font-semibold" : "text-amber-600"}>
                              Quiz: {Math.round((qr.score / qr.total) * 100)}%
                            </span>
                          )}
                          <span className={done ? "text-green-600 font-semibold" : "text-[#6b6560]"}>
                            {done ? "✓ Done" : "—"}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
''')

print("\nPhase 9 setup complete. All files written.\n")
