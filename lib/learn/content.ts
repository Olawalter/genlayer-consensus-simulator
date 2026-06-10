// ─── Types ───────────────────────────────────────────────────────────────────

export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface CodeBlock {
  lang: string;
  code: string;
}

export interface Callout {
  type: "info" | "warning" | "success" | "error" | "tip";
  text: string;
}

export interface LessonSection {
  heading?: string;
  body?: string;
  keyPoints?: string[];
  codeBlock?: CodeBlock;
  callout?: Callout;
}

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
  xpReward: number;
  relatedIds: string[];
  sections: LessonSection[];
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
  id: string;
  term: string;
  definition: string;
  category: string;
  relatedTerms: string[];
}

// ─── Content ─────────────────────────────────────────────────────────────────

export const LESSONS: Lesson[] = [
  {
    id: "l1",
    slug: "what-is-genlayer",
    title: "What is GenLayer?",
    subtitle: "The AI-native Layer-1 blockchain",
    difficulty: "beginner",
    estimatedMinutes: 5,
    module: "Foundations",
    order: 1,
    icon: "L",
    xpReward: 50,
    relatedIds: ["l2", "l3"],
    sections: [
      {
        heading: "The problem GenLayer solves",
        body: "Traditional blockchains cannot access real-world information or reason about subjective questions. A smart contract cannot answer: Is this freelancer's work satisfactory? Did the weather in Paris exceed 30°C yesterday? GenLayer solves this by embedding AI directly into the consensus mechanism.",
      },
      {
        heading: "AI-native consensus",
        body: "GenLayer is a Layer-1 blockchain where validators are not just nodes — they are AI agents. Each validator runs a Python-based smart contract (an Intelligent Contract) and calls its assigned LLM to reason about real-world information during execution.",
        callout: {
          type: "info",
          text: "GenLayer validators each run a different LLM (GPT-4o, Claude, Llama, etc.), so no single AI model controls the outcome.",
        },
      },
      {
        heading: "The GenVM",
        body: "GenLayer runs on the GenVM — the GenLayer Virtual Machine. It executes Python-based Intelligent Contracts in a sandboxed environment. Each validator runs its own GenVM instance, which is why validators can reach different results when LLM calls return different outputs.",
        codeBlock: {
          lang: "python",
          code: `# { "Depends": "py-genlayer:test" }
from genlayer import *

class MyContract(gl.Contract):
    result: str

    @gl.public.write
    def evaluate(self, question: str) -> None:
        # This calls the validator's assigned LLM
        answer = gl.exec_prompt(f"Answer YES or NO: {question}")
        self.result = answer.strip()`,
        },
      },
      {
        heading: "Key properties",
        keyPoints: [
          "Python-based smart contracts (no Solidity required)",
          "Validators re-execute contracts independently with their own LLMs",
          "Non-deterministic outputs are resolved via the Equivalence Principle",
          "Appeals system handles disputes without centralized arbitration",
          "Optimistic Democracy governs state finality",
        ],
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
    icon: "I",
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
          "@gl.public.view -- Read-only. Runs on one node. No consensus required. Like Ethereum view functions.",
          "@gl.public.write -- State-changing. Triggers Optimistic Democracy. All validators re-execute independently.",
        ],
        codeBlock: {
          lang: "python",
          code: `class FreelanceEscrow(gl.Contract):
    payments: dict

    @gl.public.view
    def get_balance(self, client: str) -> int:
        # No consensus needed — read only
        return self.payments.get(client, 0)

    @gl.public.write
    def approve_work(self, client: str, work_desc: str) -> None:
        # Triggers Optimistic Democracy — all validators evaluate
        verdict = gl.exec_prompt(
            f"Is this work satisfactory? Work: {work_desc}. Reply YES or NO."
        )
        if "YES" in verdict.upper():
            self.payments[client] = self.payments.get(client, 0) + 100`,
        },
      },
      {
        heading: "gl.exec_prompt()",
        body: "The gl.exec_prompt() function is the core primitive of Intelligent Contracts. It sends a prompt to the validator's assigned LLM and returns the response as a string. Because each validator has a different LLM, results may differ — this is expected and handled by the Equivalence Principle.",
        callout: {
          type: "warning",
          text: "gl.exec_prompt() is non-deterministic. Two validators with different LLMs may return different answers to the same prompt. Design your contracts to tolerate this.",
        },
      },
    ],
  },
  {
    id: "l3",
    slug: "optimistic-democracy",
    title: "Optimistic Democracy",
    subtitle: "How GenLayer reaches consensus",
    difficulty: "intermediate",
    estimatedMinutes: 8,
    module: "Consensus",
    order: 3,
    icon: "O",
    xpReward: 75,
    relatedIds: ["l1", "l4", "l5"],
    sections: [
      {
        heading: "The governance model",
        body: "Optimistic Democracy is GenLayer's consensus mechanism. Instead of all validators voting simultaneously, a leader (the transaction proposer) executes the contract first and proposes an outcome. Other validators then independently verify that outcome.",
      },
      {
        heading: "The five stages",
        keyPoints: [
          "1. PROPOSED: Leader executes the contract and proposes a result",
          "2. VALIDATOR REVIEW: Other validators re-execute and compare results",
          "3. EQUIVALENCE CHECK: Results are compared using the Equivalence Principle",
          "4. FINALITY WINDOW: A time window during which results can be appealed",
          "5. FINALIZED: Outcome is written to the blockchain",
        ],
        callout: {
          type: "info",
          text: "The finality window is key: it gives network participants time to challenge outcomes they believe are wrong before they become permanent.",
        },
      },
      {
        heading: "Why Optimistic?",
        body: "The system is optimistic because it assumes the leader's proposed outcome is correct and only triggers full re-execution if validators disagree. This is more efficient than requiring all validators to execute every contract upfront.",
      },
    ],
  },
  {
    id: "l4",
    slug: "equivalence-principle",
    title: "The Equivalence Principle",
    subtitle: "Resolving non-deterministic AI outputs",
    difficulty: "intermediate",
    estimatedMinutes: 9,
    module: "Consensus",
    order: 4,
    icon: "E",
    xpReward: 80,
    relatedIds: ["l3", "l5", "l6"],
    sections: [
      {
        heading: "The non-determinism problem",
        body: "When 5 validators each call a different LLM with the same prompt, they may return slightly different answers. One may say YES with 90% confidence, another YES with 70%, and a third UNCERTAIN. Traditional blockchains require identical results — but GenLayer cannot demand that from AI models.",
      },
      {
        heading: "Two equivalence modes",
        keyPoints: [
          "Comparative: Are the numeric outputs within an acceptable margin of each other?",
          "Non-comparative: Does each output independently satisfy the required criteria?",
        ],
      },
      {
        heading: "Comparative equivalence",
        body: "In comparative mode, validator outputs are treated as numeric values on a scale. If enough validators (the threshold, typically 60%) produce outputs within a defined margin (the tolerance band), the outputs are considered equivalent and consensus is reached.",
        codeBlock: {
          lang: "python",
          code: `# Comparative equivalence example
# Validator outputs: [0.87, 0.82, 0.91, 0.79, 0.85]
# Tolerance: 0.15, Threshold: 60%
# Mean: 0.848
# All values within [0.698, 0.998] — band of 0.15 around mean
# 5/5 validators within band = 100% >= 60% threshold
# Result: EQUIVALENT (consensus reached)`,
        },
      },
      {
        heading: "Non-comparative equivalence",
        body: "In non-comparative mode, each validator output is evaluated independently against a boolean criterion (e.g., did the output contain YES?). If enough validators independently satisfy the criterion, consensus is reached without comparing outputs to each other.",
        callout: {
          type: "success",
          text: "Non-comparative mode is ideal for YES/NO decisions where exact phrasing may differ but the core answer is the same.",
        },
      },
    ],
  },
  {
    id: "l5",
    slug: "appeals-process",
    title: "The Appeals Process",
    subtitle: "Challenging outcomes in GenLayer",
    difficulty: "intermediate",
    estimatedMinutes: 7,
    module: "Consensus",
    order: 5,
    icon: "A",
    xpReward: 70,
    relatedIds: ["l3", "l4", "l6"],
    sections: [
      {
        heading: "When appeals are triggered",
        body: "An appeal can be triggered during the finality window when a transaction participant believes the proposed outcome is incorrect. Appeals re-open consensus with an expanded validator set to get a broader opinion on the disputed outcome.",
      },
      {
        heading: "Appeal rounds",
        body: "Each appeal round adds 3 new validators to the set. Original validators keep their votes frozen (they already voted), while new validators execute the contract fresh and contribute new votes. This continues until consensus is reached or the maximum round limit is hit.",
        keyPoints: [
          "Round 1: 5 original validators (frozen votes)",
          "Round 2: 5 original + 3 new = 8 validators",
          "Round 3: 8 original + 3 new = 11 validators",
          "Max rounds: typically 3-5 before forced resolution",
        ],
      },
      {
        heading: "Appeal cost and incentives",
        body: "Appealing costs GEN tokens. If the appeal succeeds (outcome reverses), the appealer is refunded plus rewarded. If the appeal fails, the cost is distributed to validators as compensation for the extra work. This prevents frivolous appeals.",
        callout: {
          type: "warning",
          text: "Appeal costs scale with round number. Round 1 appeals are cheap; later rounds are expensive. This discourages infinite appeal chains.",
        },
      },
    ],
  },
  {
    id: "l6",
    slug: "validator-nodes",
    title: "Validator Nodes",
    subtitle: "The AI agents securing GenLayer",
    difficulty: "beginner",
    estimatedMinutes: 6,
    module: "Network",
    order: 6,
    icon: "V",
    xpReward: 55,
    relatedIds: ["l1", "l4", "l7"],
    sections: [
      {
        heading: "What validators do",
        body: "GenLayer validators are network nodes that execute Intelligent Contracts, produce LLM-powered votes, and participate in consensus. Unlike Bitcoin miners or Ethereum validators, GenLayer validators must run an LLM to function — AI capability is a core requirement.",
      },
      {
        heading: "Validator configuration",
        keyPoints: [
          "Each validator is assigned one primary LLM (e.g., GPT-4o, Claude 3.5, Llama 3)",
          "Validators have an accept threshold: the confidence above which they vote ACCEPT",
          "Validators have an uncertainty range: the band where they vote UNCERTAIN",
          "Validators stake GEN tokens as collateral for honest participation",
        ],
      },
      {
        heading: "Validator selection",
        body: "For each transaction, a subset of validators is selected to form the consensus committee. The leader (first validator) is chosen based on stake weight. The remaining validators are selected pseudo-randomly. More stake = higher chance of selection.",
        callout: {
          type: "info",
          text: "The randomness in validator selection ensures no single entity can predict and manipulate which validators will evaluate a specific transaction.",
        },
      },
    ],
  },
  {
    id: "l7",
    slug: "writing-intelligent-contracts",
    title: "Writing Intelligent Contracts",
    subtitle: "Practical guide to GenLayer development",
    difficulty: "advanced",
    estimatedMinutes: 12,
    module: "Development",
    order: 7,
    icon: "W",
    xpReward: 100,
    relatedIds: ["l2", "l6"],
    sections: [
      {
        heading: "Project structure",
        body: "A GenLayer project is a Python file with a contract class inheriting from gl.Contract. State variables are declared as class attributes with type annotations. Public functions use the @gl.public.view or @gl.public.write decorators.",
        codeBlock: {
          lang: "python",
          code: `# { "Depends": "py-genlayer:test" }
from genlayer import *

class PredictionMarket(gl.Contract):
    # State variables — persisted on-chain
    question: str
    resolution: str
    resolved: bool
    stakes: dict  # address -> amount

    def __init__(self, question: str) -> None:
        self.question = question
        self.resolution = ""
        self.resolved = False
        self.stakes = {}`,
        },
      },
      {
        heading: "Adding write functions",
        body: "Write functions change state and trigger Optimistic Democracy. They should call gl.exec_prompt() when they need AI reasoning, and use the result to make state transitions. Keep prompts clear and unambiguous.",
        codeBlock: {
          lang: "python",
          code: `@gl.public.write
def resolve(self) -> None:
    # Validate we have not already resolved
    assert not self.resolved, "Already resolved"

    # Ask the validator's LLM to evaluate the question
    prompt = (
        f"Question: {self.question}\\n"
        f"Based on publicly available information, did this event occur?\\n"
        f"Reply with exactly YES or NO."
    )
    answer = gl.exec_prompt(prompt)

    self.resolution = answer.strip().upper()
    self.resolved = True`,
        },
      },
      {
        heading: "Best practices",
        keyPoints: [
          "Keep prompts short and unambiguous — LLMs perform better with clear instructions",
          "Use assert statements to validate preconditions before LLM calls",
          "Design for non-determinism: your contract logic should handle UNCERTAIN votes gracefully",
          "Test with multiple validators locally using the GenLayer Studio before deploying",
          "Avoid embedding dynamic data (timestamps, prices) directly in prompts — use state variables",
        ],
        callout: {
          type: "warning",
          text: "Never rely on a specific LLM's output format. Always use .strip().upper() and check for substrings rather than exact equality.",
        },
      },
    ],
  },
];

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: "q1",
    lessonId: "l1",
    question: "What is the primary innovation of GenLayer compared to traditional blockchains?",
    options: [
      "Faster transaction speeds",
      "AI-powered validators that can reason about real-world information",
      "Lower gas fees",
      "Better smart contract languages",
    ],
    correctIndex: 1,
    explanation: "GenLayer's core innovation is embedding AI directly into the consensus mechanism, allowing validators to reason about subjective, real-world information that traditional blockchains cannot access.",
  },
  {
    id: "q2",
    lessonId: "l1",
    question: "What does GenVM stand for and what does it execute?",
    options: [
      "General Virtual Machine — executes any bytecode",
      "GenLayer Virtual Machine — executes Python-based Intelligent Contracts",
      "Generative Virtual Machine — executes AI model inference",
      "Governance Virtual Machine — executes voting contracts",
    ],
    correctIndex: 1,
    explanation: "GenVM is the GenLayer Virtual Machine. It executes Python-based Intelligent Contracts in a sandboxed environment, with each validator running its own GenVM instance.",
  },
  {
    id: "q3",
    lessonId: "l2",
    question: "Which decorator triggers Optimistic Democracy in a GenLayer contract?",
    options: [
      "@gl.public.view",
      "@gl.public.read",
      "@gl.public.write",
      "@gl.public.execute",
    ],
    correctIndex: 2,
    explanation: "@gl.public.write marks state-changing functions that trigger Optimistic Democracy. All validators re-execute the function independently when a write transaction is submitted.",
  },
  {
    id: "q4",
    lessonId: "l2",
    question: "What does gl.exec_prompt() do?",
    options: [
      "Executes a SQL query against the blockchain state",
      "Sends a prompt to the validator's assigned LLM and returns the response",
      "Broadcasts a transaction to the network",
      "Validates the caller's signature",
    ],
    correctIndex: 1,
    explanation: "gl.exec_prompt() is the core primitive of Intelligent Contracts. It sends a prompt to the validator's assigned LLM and returns the response as a string.",
  },
  {
    id: "q5",
    lessonId: "l3",
    question: "In Optimistic Democracy, who executes the contract first?",
    options: [
      "All validators simultaneously",
      "A randomly selected validator",
      "The leader (transaction proposer)",
      "The contract deployer",
    ],
    correctIndex: 2,
    explanation: "The leader (transaction proposer) executes the contract first and proposes an outcome. Other validators then independently verify that proposed outcome.",
  },
  {
    id: "q6",
    lessonId: "l3",
    question: "What is the purpose of the finality window in Optimistic Democracy?",
    options: [
      "To allow validators to rest between transactions",
      "To give participants time to appeal outcomes before they become permanent",
      "To batch multiple transactions together",
      "To calculate validator rewards",
    ],
    correctIndex: 1,
    explanation: "The finality window gives network participants time to challenge outcomes they believe are wrong before they are written permanently to the blockchain.",
  },
  {
    id: "q7",
    lessonId: "l4",
    question: "What is the key difference between Comparative and Non-comparative equivalence?",
    options: [
      "Comparative requires more validators",
      "Comparative checks outputs against each other; Non-comparative checks each output against a criterion independently",
      "Non-comparative is faster",
      "Comparative only works with numeric outputs",
    ],
    correctIndex: 1,
    explanation: "Comparative equivalence checks if outputs are within an acceptable margin of each other. Non-comparative equivalence checks if each output independently satisfies a boolean criterion, without comparing outputs to each other.",
  },
  {
    id: "q8",
    lessonId: "l5",
    question: "How many new validators are added per appeal round?",
    options: ["1", "2", "3", "5"],
    correctIndex: 2,
    explanation: "Each appeal round adds 3 new validators to the consensus committee. Original validators keep their votes frozen while new validators execute the contract fresh.",
  },
  {
    id: "q9",
    lessonId: "l5",
    question: "What happens to appeal costs as rounds increase?",
    options: [
      "They stay the same",
      "They decrease to encourage more appeals",
      "They scale up to discourage infinite appeal chains",
      "They are always free",
    ],
    correctIndex: 2,
    explanation: "Appeal costs scale with round number. This economic design discourages frivolous appeals and infinite appeal chains while still allowing legitimate challenges.",
  },
  {
    id: "q10",
    lessonId: "l6",
    question: "What unique requirement do GenLayer validators have compared to traditional blockchain validators?",
    options: [
      "They must have a physical data center",
      "They must run an LLM as AI capability is a core network requirement",
      "They must hold a specific cryptocurrency",
      "They must pass a certification exam",
    ],
    correctIndex: 1,
    explanation: "GenLayer validators must run an LLM to function — AI capability is a core requirement of the network, unlike Bitcoin miners or Ethereum validators that only need compute power.",
  },
  {
    id: "q11",
    lessonId: "l7",
    question: "What is the recommended way to check an LLM response for YES/NO answers?",
    options: [
      'if answer == "YES"',
      'if answer.strip().upper() == "YES" or check for substring',
      "if answer.startswith('Y')",
      "if len(answer) == 3",
    ],
    correctIndex: 1,
    explanation: "Never rely on exact output format from LLMs. Always use .strip().upper() and check for substrings rather than exact equality, as different LLMs may format responses slightly differently.",
  },
  {
    id: "q12",
    lessonId: "l7",
    question: "When should you use assert statements in an Intelligent Contract?",
    options: [
      "Never — they are not supported in GenLayer",
      "Only in @gl.public.view functions",
      "To validate preconditions before LLM calls and state transitions",
      "Only when deploying to mainnet",
    ],
    correctIndex: 2,
    explanation: "Assert statements should validate preconditions before LLM calls and state transitions. This prevents wasted LLM calls when basic conditions are not met and makes contracts more robust.",
  },
];

export const GLOSSARY_TERMS: GlossaryTerm[] = [
  {
    id: "g1",
    term: "GenLayer",
    definition: "An AI-native Layer-1 blockchain where validators use LLMs to execute Intelligent Contracts and reach consensus on subjective real-world information.",
    category: "Core",
    relatedTerms: ["g2", "g3", "g5"],
  },
  {
    id: "g2",
    term: "Intelligent Contract",
    definition: "A Python-based smart contract on GenLayer that uses gl.exec_prompt() to call the validator's assigned LLM during execution, enabling reasoning about real-world data.",
    category: "Core",
    relatedTerms: ["g1", "g6", "g7"],
  },
  {
    id: "g3",
    term: "Optimistic Democracy",
    definition: "GenLayer's consensus mechanism where a leader proposes an outcome and other validators verify it, with a finality window for appeals before the result is written on-chain.",
    category: "Consensus",
    relatedTerms: ["g4", "g8", "g9"],
  },
  {
    id: "g4",
    term: "Equivalence Principle",
    definition: "The mathematical framework GenLayer uses to determine if non-deterministic LLM outputs from different validators are equivalent enough to constitute consensus.",
    category: "Consensus",
    relatedTerms: ["g10", "g11", "g3"],
  },
  {
    id: "g5",
    term: "GenVM",
    definition: "The GenLayer Virtual Machine that executes Python-based Intelligent Contracts in a sandboxed environment. Each validator runs its own GenVM instance.",
    category: "Core",
    relatedTerms: ["g1", "g2"],
  },
  {
    id: "g6",
    term: "gl.exec_prompt()",
    definition: "The built-in GenLayer function that sends a prompt string to the validator's assigned LLM and returns the response. The core primitive of Intelligent Contracts.",
    category: "Development",
    relatedTerms: ["g2", "g7", "g12"],
  },
  {
    id: "g7",
    term: "@gl.public.write",
    definition: "Decorator for state-changing contract functions that trigger Optimistic Democracy. All validators re-execute the function independently when called.",
    category: "Development",
    relatedTerms: ["g13", "g3", "g6"],
  },
  {
    id: "g8",
    term: "Finality Window",
    definition: "A time period after a transaction outcome is proposed during which network participants can submit appeals before the result becomes permanently finalized on-chain.",
    category: "Consensus",
    relatedTerms: ["g9", "g3"],
  },
  {
    id: "g9",
    term: "Appeal",
    definition: "A challenge submitted during the finality window that re-opens consensus on a transaction with an expanded validator set (+3 validators per round).",
    category: "Consensus",
    relatedTerms: ["g8", "g3", "g14"],
  },
  {
    id: "g10",
    term: "Comparative Equivalence",
    definition: "An equivalence check mode where validator numeric outputs are compared against each other. Consensus is reached if enough outputs fall within a defined tolerance margin.",
    category: "Consensus",
    relatedTerms: ["g11", "g4"],
  },
  {
    id: "g11",
    term: "Non-comparative Equivalence",
    definition: "An equivalence check mode where each validator output is evaluated independently against a boolean criterion, without comparing outputs to each other.",
    category: "Consensus",
    relatedTerms: ["g10", "g4"],
  },
  {
    id: "g12",
    term: "Validator",
    definition: "A GenLayer network node that executes Intelligent Contracts, runs an LLM for reasoning, stakes GEN tokens, and participates in Optimistic Democracy consensus.",
    category: "Network",
    relatedTerms: ["g1", "g6", "g15"],
  },
  {
    id: "g13",
    term: "@gl.public.view",
    definition: "Decorator for read-only contract functions that run on a single node without triggering consensus. Equivalent to Ethereum view functions.",
    category: "Development",
    relatedTerms: ["g7", "g2"],
  },
  {
    id: "g14",
    term: "Appeal Round",
    definition: "A single iteration of the appeals process where 3 new validators are added to the committee. Original validators keep their frozen votes; new validators execute fresh.",
    category: "Consensus",
    relatedTerms: ["g9", "g12"],
  },
  {
    id: "g15",
    term: "Validator Stake",
    definition: "GEN tokens locked by a validator as collateral for honest participation. Higher stake increases the probability of being selected for consensus committees.",
    category: "Network",
    relatedTerms: ["g12"],
  },
  {
    id: "g16",
    term: "Leader",
    definition: "The first validator selected for a consensus committee. The leader executes the Intelligent Contract first and proposes the initial outcome in Optimistic Democracy.",
    category: "Consensus",
    relatedTerms: ["g3", "g12"],
  },
];
