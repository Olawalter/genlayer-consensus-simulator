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
