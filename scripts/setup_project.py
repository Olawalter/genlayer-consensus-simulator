import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
DIRS = [
    "app/(auth)/login",
    "app/(auth)/register",
    "app/(dashboard)/playground",
    "app/(dashboard)/validator-lab",
    "app/(dashboard)/appeals",
    "app/(dashboard)/equivalence",
    "app/(dashboard)/democracy",
    "app/(dashboard)/llm-compare",
    "app/(dashboard)/learn",
    "app/(dashboard)/sandbox",
    "app/api/simulate",
    "app/api/appeal",
    "app/api/validators",
    "app/api/consensus",
    "app/api/analytics",
    "components/ui",
    "components/consensus",
    "components/validators",
    "components/appeals",
    "components/equivalence",
    "components/democracy",
    "components/llm",
    "components/learn",
    "components/layout",
    "components/shared",
    "hooks",
    "lib/genlayer",
    "lib/supabase",
    "lib/validators",
    "services",
    "store",
    "types",
    "contracts",
    "supabase/migrations",
    "supabase/functions/simulate-consensus",
    "supabase/functions/trigger-appeal",
    "supabase/functions/sync-chain-state",
    "scripts",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "docs",
    "config",
    "public/fonts",
    "public/images",
    "monitoring",
    "security",
    "analytics",
]

# ---------------------------------------------------------------------------
# SQL Schema
# ---------------------------------------------------------------------------
SQL_SCHEMA = """\
-- GenLayer Consensus Simulator: Initial Schema
-- Migration 001

CREATE TABLE profiles (
  id           UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username     TEXT UNIQUE NOT NULL,
  role         TEXT NOT NULL DEFAULT 'learner',
  xp           INTEGER NOT NULL DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE claims (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID REFERENCES profiles(id) ON DELETE SET NULL,
  content      TEXT NOT NULL,
  category     TEXT NOT NULL,
  metadata     JSONB,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE simulations (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id           UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  user_id            UUID REFERENCES profiles(id) ON DELETE SET NULL,
  status             TEXT NOT NULL DEFAULT 'pending',
  validator_count    INTEGER NOT NULL DEFAULT 5,
  consensus_reached  BOOLEAN,
  final_verdict      TEXT,
  contract_address   TEXT,
  tx_hash            TEXT,
  chain_data         JSONB,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at       TIMESTAMPTZ
);

CREATE TABLE validators (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL,
  model        TEXT NOT NULL,
  persona      TEXT NOT NULL,
  bias_profile JSONB,
  is_active    BOOLEAN NOT NULL DEFAULT true,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE validator_votes (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id     UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
  validator_id      UUID NOT NULL REFERENCES validators(id),
  role              TEXT NOT NULL DEFAULT 'validator',
  vote              TEXT NOT NULL,
  confidence        NUMERIC(4,3),
  reasoning         TEXT,
  raw_llm_output    TEXT,
  equivalence_score NUMERIC(4,3),
  voted_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE consensus_results (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id     UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
  round             INTEGER NOT NULL DEFAULT 1,
  accept_count      INTEGER NOT NULL DEFAULT 0,
  reject_count      INTEGER NOT NULL DEFAULT 0,
  uncertain_count   INTEGER NOT NULL DEFAULT 0,
  consensus_type    TEXT,
  equivalence_pass  BOOLEAN,
  outcome           TEXT,
  computed_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE appeals (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id         UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
  initiated_by          UUID REFERENCES profiles(id) ON DELETE SET NULL,
  reason                TEXT NOT NULL,
  status                TEXT NOT NULL DEFAULT 'open',
  additional_validators INTEGER NOT NULL DEFAULT 3,
  original_outcome      TEXT NOT NULL,
  final_outcome         TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at           TIMESTAMPTZ
);

CREATE TABLE appeal_rounds (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  appeal_id   UUID NOT NULL REFERENCES appeals(id) ON DELETE CASCADE,
  round       INTEGER NOT NULL,
  outcome     TEXT,
  votes_data  JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE analytics_events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES profiles(id) ON DELETE SET NULL,
  event_type  TEXT NOT NULL,
  payload     JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES profiles(id) ON DELETE SET NULL,
  action      TEXT NOT NULL,
  table_name  TEXT,
  record_id   UUID,
  diff        JSONB,
  ip_address  INET,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_simulations_user_id   ON simulations(user_id);
CREATE INDEX idx_simulations_status    ON simulations(status);
CREATE INDEX idx_validator_votes_sim   ON validator_votes(simulation_id);
CREATE INDEX idx_claims_user_id        ON claims(user_id);
CREATE INDEX idx_appeals_simulation_id ON appeals(simulation_id);
CREATE INDEX idx_analytics_user_event  ON analytics_events(user_id, event_type);
CREATE INDEX idx_audit_logs_user_id    ON audit_logs(user_id);

-- Row Level Security
ALTER TABLE profiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims             ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations        ENABLE ROW LEVEL SECURITY;
ALTER TABLE validator_votes    ENABLE ROW LEVEL SECURITY;
ALTER TABLE consensus_results  ENABLE ROW LEVEL SECURITY;
ALTER TABLE appeals            ENABLE ROW LEVEL SECURITY;
ALTER TABLE appeal_rounds      ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events   ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs         ENABLE ROW LEVEL SECURITY;

CREATE POLICY "profiles_own"         ON profiles         FOR ALL    USING (auth.uid() = id);
CREATE POLICY "claims_own_insert"    ON claims           FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "claims_own_select"    ON claims           FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "simulations_own"      ON simulations      FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "votes_auth_read"      ON validator_votes  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "consensus_auth_read"  ON consensus_results FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "appeals_auth_read"    ON appeals          FOR SELECT USING (auth.role() = 'authenticated');
"""

# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------
FILES = {
    # App Router pages
    "app/layout.tsx": (
        'export default function RootLayout({ children }: { children: React.ReactNode }) {\n'
        '  return <html lang="en"><body>{children}</body></html>;\n'
        '}\n'
    ),
    "app/globals.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n",
    "app/not-found.tsx": "export default function NotFound() {\n  return <div>404 - Not Found</div>;\n}\n",
    "app/(auth)/login/page.tsx": "export default function LoginPage() {\n  return <div>Login</div>;\n}\n",
    "app/(auth)/register/page.tsx": "export default function RegisterPage() {\n  return <div>Register</div>;\n}\n",
    "app/(dashboard)/layout.tsx": (
        "export default function DashboardLayout({ children }: { children: React.ReactNode }) {\n"
        "  return <div>{children}</div>;\n"
        "}\n"
    ),
    "app/(dashboard)/page.tsx": "export default function DashboardPage() {\n  return <div>Dashboard</div>;\n}\n",
    "app/(dashboard)/playground/page.tsx": "export default function PlaygroundPage() {\n  return <div>Consensus Playground</div>;\n}\n",
    "app/(dashboard)/validator-lab/page.tsx": "export default function ValidatorLabPage() {\n  return <div>Validator Lab</div>;\n}\n",
    "app/(dashboard)/appeals/page.tsx": "export default function AppealsPage() {\n  return <div>Appeals Arena</div>;\n}\n",
    "app/(dashboard)/equivalence/page.tsx": "export default function EquivalencePage() {\n  return <div>Equivalence Explorer</div>;\n}\n",
    "app/(dashboard)/democracy/page.tsx": "export default function DemocracyPage() {\n  return <div>Optimistic Democracy Dashboard</div>;\n}\n",
    "app/(dashboard)/llm-compare/page.tsx": "export default function LLMComparePage() {\n  return <div>LLM Comparison Center</div>;\n}\n",
    "app/(dashboard)/learn/page.tsx": "export default function LearnPage() {\n  return <div>Learning Center</div>;\n}\n",
    "app/(dashboard)/sandbox/page.tsx": "export default function SandboxPage() {\n  return <div>Developer Sandbox</div>;\n}\n",

    # API routes
    "app/api/simulate/route.ts": "export async function POST() {\n  return Response.json({ status: 'ok' });\n}\n",
    "app/api/appeal/route.ts": "export async function POST() {\n  return Response.json({ status: 'ok' });\n}\n",
    "app/api/validators/route.ts": "export async function GET() {\n  return Response.json({ validators: [] });\n}\n",
    "app/api/consensus/route.ts": "export async function GET() {\n  return Response.json({ consensus: null });\n}\n",
    "app/api/analytics/route.ts": "export async function POST() {\n  return Response.json({ status: 'ok' });\n}\n",

    # Components
    "components/consensus/ConsensusPlayground.tsx": "export function ConsensusPlayground() {\n  return <div>Consensus Playground Component</div>;\n}\n",
    "components/consensus/ConsensusTimeline.tsx": "export function ConsensusTimeline() {\n  return <div>Consensus Timeline</div>;\n}\n",
    "components/consensus/ConsensusGraph.tsx": "export function ConsensusGraph() {\n  return <div>Consensus Graph</div>;\n}\n",
    "components/consensus/ConsensusStatus.tsx": "export function ConsensusStatus() {\n  return <div>Consensus Status</div>;\n}\n",
    "components/validators/ValidatorCard.tsx": "export function ValidatorCard() {\n  return <div>Validator Card</div>;\n}\n",
    "components/validators/ValidatorPanel.tsx": "export function ValidatorPanel() {\n  return <div>Validator Panel</div>;\n}\n",
    "components/validators/ValidatorVote.tsx": "export function ValidatorVote() {\n  return <div>Validator Vote</div>;\n}\n",
    "components/validators/ValidatorReasoning.tsx": "export function ValidatorReasoning() {\n  return <div>Validator Reasoning</div>;\n}\n",
    "components/appeals/AppealsArena.tsx": "export function AppealsArena() {\n  return <div>Appeals Arena</div>;\n}\n",
    "components/appeals/AppealTrigger.tsx": "export function AppealTrigger() {\n  return <div>Appeal Trigger</div>;\n}\n",
    "components/appeals/AppealTimeline.tsx": "export function AppealTimeline() {\n  return <div>Appeal Timeline</div>;\n}\n",
    "components/equivalence/EquivalenceExplorer.tsx": "export function EquivalenceExplorer() {\n  return <div>Equivalence Explorer</div>;\n}\n",
    "components/equivalence/EquivalenceRange.tsx": "export function EquivalenceRange() {\n  return <div>Equivalence Range</div>;\n}\n",
    "components/democracy/DemocracyDashboard.tsx": "export function DemocracyDashboard() {\n  return <div>Democracy Dashboard</div>;\n}\n",
    "components/democracy/VoteDistribution.tsx": "export function VoteDistribution() {\n  return <div>Vote Distribution</div>;\n}\n",
    "components/llm/LLMCompareCenter.tsx": "export function LLMCompareCenter() {\n  return <div>LLM Compare Center</div>;\n}\n",
    "components/llm/LLMOutputCard.tsx": "export function LLMOutputCard() {\n  return <div>LLM Output Card</div>;\n}\n",
    "components/learn/ConceptCard.tsx": "export function ConceptCard() {\n  return <div>Concept Card</div>;\n}\n",
    "components/learn/InteractiveTutorial.tsx": "export function InteractiveTutorial() {\n  return <div>Interactive Tutorial</div>;\n}\n",
    "components/learn/GlossaryPanel.tsx": "export function GlossaryPanel() {\n  return <div>Glossary Panel</div>;\n}\n",
    "components/layout/Navbar.tsx": "export function Navbar() {\n  return <nav>Navbar</nav>;\n}\n",
    "components/layout/Sidebar.tsx": "export function Sidebar() {\n  return <aside>Sidebar</aside>;\n}\n",
    "components/layout/Footer.tsx": "export function Footer() {\n  return <footer>Footer</footer>;\n}\n",
    "components/shared/AnimatedBadge.tsx": "export function AnimatedBadge() {\n  return <span>Badge</span>;\n}\n",
    "components/shared/LoadingSpinner.tsx": "export function LoadingSpinner() {\n  return <div>Loading...</div>;\n}\n",
    "components/shared/StatusIndicator.tsx": "export function StatusIndicator() {\n  return <div>Status</div>;\n}\n",

    # Hooks
    "hooks/useConsensus.ts": "export function useConsensus() {\n  return {};\n}\n",
    "hooks/useValidators.ts": "export function useValidators() {\n  return {};\n}\n",
    "hooks/useAppeal.ts": "export function useAppeal() {\n  return {};\n}\n",
    "hooks/useSimulation.ts": "export function useSimulation() {\n  return {};\n}\n",
    "hooks/useEquivalence.ts": "export function useEquivalence() {\n  return {};\n}\n",
    "hooks/useAuth.ts": "export function useAuth() {\n  return {};\n}\n",

    # Lib
    "lib/genlayer/client.ts": "// GenLayer JS client initialization\nexport {};\n",
    "lib/genlayer/contract.ts": "// Contract read/write helpers\nexport {};\n",
    "lib/genlayer/consensus.ts": "// Consensus polling helpers\nexport {};\n",
    "lib/genlayer/constants.ts": (
        'export const CONTRACT_ADDRESS_CONSENSUS = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS_CONSENSUS ?? "";\n'
        'export const CONTRACT_ADDRESS_APPEALS = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS_APPEALS ?? "";\n'
        'export const GENLAYER_RPC_URL = process.env.NEXT_PUBLIC_GENLAYER_RPC_URL ?? "";\n'
    ),
    "lib/supabase/client.ts": "// Supabase browser client\nexport {};\n",
    "lib/supabase/server.ts": "// Supabase server client (RSC)\nexport {};\n",
    "lib/supabase/middleware.ts": "// Supabase auth middleware\nexport {};\n",
    "lib/validators/personas.ts": "// Validator personality definitions\nexport const VALIDATOR_PERSONAS: unknown[] = [];\n",
    "lib/validators/equivalence.ts": "// Equivalence scoring logic\nexport {};\n",
    "lib/utils.ts": "export function cn(...classes: string[]) {\n  return classes.filter(Boolean).join(' ');\n}\n",
    "lib/validations.ts": "// Input validation schemas (zod)\nexport {};\n",

    # Services
    "services/simulationService.ts": "// Orchestrate full simulation lifecycle\nexport {};\n",
    "services/validatorService.ts": "// Validator management\nexport {};\n",
    "services/appealService.ts": "// Appeals orchestration\nexport {};\n",
    "services/consensusService.ts": "// Consensus state machine\nexport {};\n",
    "services/analyticsService.ts": "// Analytics event tracking\nexport {};\n",
    "services/contractService.ts": "// GenLayer contract calls via genlayer-js\nexport {};\n",

    # Store
    "store/simulationStore.ts": "// Zustand store: active simulation state\nexport {};\n",
    "store/validatorStore.ts": "// Zustand store: validator state\nexport {};\n",
    "store/appealStore.ts": "// Zustand store: appeal state\nexport {};\n",
    "store/uiStore.ts": "// Zustand store: UI state\nexport {};\n",

    # Types
    "types/simulation.ts": (
        'export interface Simulation {\n'
        '  id: string;\n'
        '  claimId: string;\n'
        "  status: 'pending' | 'running' | 'accepted' | 'rejected' | 'appealed' | 'finalized';\n"
        '  validatorCount: number;\n'
        '  consensusReached: boolean | null;\n'
        '  finalVerdict: string | null;\n'
        '  createdAt: string;\n'
        '}\n'
    ),
    "types/validator.ts": (
        'export interface Validator {\n'
        '  id: string;\n'
        '  name: string;\n'
        '  model: string;\n'
        '  persona: string;\n'
        '  isActive: boolean;\n'
        '}\n\n'
        'export interface ValidatorVote {\n'
        '  validatorId: string;\n'
        '  simulationId: string;\n'
        "  role: 'leader' | 'validator';\n"
        "  vote: 'ACCEPT' | 'REJECT' | 'UNCERTAIN';\n"
        '  confidence: number;\n'
        '  reasoning: string;\n'
        '  equivalenceScore: number;\n'
        '}\n'
    ),
    "types/appeal.ts": (
        'export interface Appeal {\n'
        '  id: string;\n'
        '  simulationId: string;\n'
        '  reason: string;\n'
        "  status: 'open' | 'resolved' | 'rejected';\n"
        '  originalOutcome: string;\n'
        '  finalOutcome: string | null;\n'
        '  createdAt: string;\n'
        '}\n'
    ),
    "types/consensus.ts": (
        'export interface ConsensusResult {\n'
        '  simulationId: string;\n'
        '  round: number;\n'
        '  acceptCount: number;\n'
        '  rejectCount: number;\n'
        '  uncertainCount: number;\n'
        "  consensusType: 'unanimous' | 'majority' | 'split' | null;\n"
        '  equivalencePass: boolean;\n'
        "  outcome: 'ACCEPTED' | 'REJECTED' | 'APPEAL_TRIGGERED';\n"
        '}\n'
    ),
    "types/claim.ts": (
        'export interface Claim {\n'
        '  id: string;\n'
        '  userId: string | null;\n'
        '  content: string;\n'
        "  category: 'freelance' | 'review' | 'event' | 'custom';\n"
        '  createdAt: string;\n'
        '}\n'
    ),
    "types/contract.ts": (
        '// GenLayer contract types\n'
        'export interface ContractCallResult {\n'
        '  txHash: string;\n'
        '  status: string;\n'
        '  data: unknown;\n'
        '}\n'
    ),
    "types/supabase.ts": (
        '// Generated Supabase DB types (replace with: supabase gen types typescript)\n'
        'export type Json = string | number | boolean | null | { [key: string]: Json } | Json[];\n'
    ),

    # Intelligent Contracts
    "contracts/ConsensusSimulator.py": (
        '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\n'
        'from genlayer import *\n\n\n'
        'class ConsensusSimulator(gl.Contract):\n'
        '    """GenLayer Intelligent Contract for subjective consensus simulation."""\n\n'
        '    simulations: dict\n\n'
        '    def __init__(self) -> None:\n'
        '        self.simulations = {}\n\n'
        '    @gl.public.view\n'
        '    def get_simulation(self, simulation_id: str) -> dict:\n'
        '        return self.simulations.get(simulation_id, {})\n\n'
        '    @gl.public.write\n'
        '    def evaluate_claim(self, simulation_id: str, claim: str) -> None:\n'
        '        verdict = gl.exec_prompt(\n'
        '            f"You are a neutral evaluator. Answer ACCEPT or REJECT only.\\n"\n'
        '            f"Claim: {claim}\\n"\n'
        '            f"Answer:"\n'
        '        )\n'
        '        self.simulations[simulation_id] = {\n'
        '            "verdict": verdict.strip(),\n'
        '            "claim": claim,\n'
        '        }\n'
    ),
    "contracts/AppealManager.py": (
        '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\n'
        'from genlayer import *\n\n\n'
        'class AppealManager(gl.Contract):\n'
        '    """Manages appeal rounds for disputed consensus outcomes."""\n\n'
        '    appeals: dict\n\n'
        '    def __init__(self) -> None:\n'
        '        self.appeals = {}\n\n'
        '    @gl.public.view\n'
        '    def get_appeal(self, appeal_id: str) -> dict:\n'
        '        return self.appeals.get(appeal_id, {})\n\n'
        '    @gl.public.write\n'
        '    def open_appeal(self, appeal_id: str, claim: str, original_verdict: str, reason: str) -> None:\n'
        '        re_evaluation = gl.exec_prompt(\n'
        '            f"An appeal has been raised against this verdict: {original_verdict}.\\n"\n'
        '            f"Appeal reason: {reason}\\n"\n'
        '            f"Original claim: {claim}\\n"\n'
        '            f"Re-evaluate carefully. Answer ACCEPT or REJECT only.\\n"\n'
        '            f"Answer:"\n'
        '        )\n'
        '        self.appeals[appeal_id] = {\n'
        '            "claim": claim,\n'
        '            "original_verdict": original_verdict,\n'
        '            "reason": reason,\n'
        '            "re_verdict": re_evaluation.strip(),\n'
        '        }\n'
    ),
    "contracts/ValidatorRegistry.py": (
        '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\n'
        'from genlayer import *\n\n\n'
        'class ValidatorRegistry(gl.Contract):\n'
        '    """Registry of validator identities and models."""\n\n'
        '    validators: dict\n\n'
        '    def __init__(self) -> None:\n'
        '        self.validators = {}\n\n'
        '    @gl.public.view\n'
        '    def get_validator(self, validator_id: str) -> dict:\n'
        '        return self.validators.get(validator_id, {})\n\n'
        '    @gl.public.write\n'
        '    def register_validator(self, validator_id: str, name: str, model: str, persona: str) -> None:\n'
        '        self.validators[validator_id] = {\n'
        '            "name": name,\n'
        '            "model": model,\n'
        '            "persona": persona,\n'
        '            "active": True,\n'
        '        }\n'
    ),
    "contracts/README.md": (
        "# GenLayer Intelligent Contracts\n\n"
        "## Contracts\n\n"
        "- **ConsensusSimulator.py** — evaluates subjective claims via LLM, stores verdicts on-chain\n"
        "- **AppealManager.py** — handles appeal re-evaluation rounds\n"
        "- **ValidatorRegistry.py** — stores validator identities and models\n\n"
        "## Deployment\n\n"
        "1. Open GenLayer Studio: https://studio.genlayer.com\n"
        "2. Paste each contract into the editor\n"
        "3. Deploy to Studio Net\n"
        "4. Copy the contract address\n"
        "5. Set NEXT_PUBLIC_CONTRACT_ADDRESS_CONSENSUS in .env.local\n\n"
        "## Key GenLayer Patterns\n\n"
        "- `gl.exec_prompt()` — calls the validator's assigned LLM\n"
        "- `@gl.public.view` — read-only, no consensus required\n"
        "- `@gl.public.write` — state-changing, triggers Optimistic Democracy\n"
        "- Each validator re-executes the contract independently\n"
        "- Equivalence Principle determines if outputs are close enough to accept\n"
    ),

    # Supabase
    "supabase/migrations/001_initial_schema.sql": SQL_SCHEMA,
    "supabase/seed.sql": (
        "-- Seed: default validator personalities\n"
        "-- Run after migration 001\n\n"
        "INSERT INTO validators (name, model, persona, bias_profile) VALUES\n"
        "  ('Atlas',   'gpt-4o',          'analytical', '{\"strictness\": 0.8}'),\n"
        "  ('Nova',    'claude-3-5-sonnet','creative',   '{\"strictness\": 0.4}'),\n"
        "  ('Orion',   'llama-3',          'strict',     '{\"strictness\": 0.9}'),\n"
        "  ('Lyra',    'mistral-large',    'lenient',    '{\"strictness\": 0.2}'),\n"
        "  ('Zephyr',  'gemini-pro',       'balanced',   '{\"strictness\": 0.6}');\n"
    ),
    "supabase/functions/simulate-consensus/index.ts": (
        '// Supabase Edge Function: orchestrate consensus simulation\n'
        'import { serve } from "https://deno.land/std@0.168.0/http/server.ts";\n\n'
        'serve(async (_req) => {\n'
        '  return new Response(JSON.stringify({ ok: true }), {\n'
        '    headers: { "Content-Type": "application/json" },\n'
        '    status: 200,\n'
        '  });\n'
        '});\n'
    ),
    "supabase/functions/trigger-appeal/index.ts": (
        '// Supabase Edge Function: trigger appeal\n'
        'import { serve } from "https://deno.land/std@0.168.0/http/server.ts";\n\n'
        'serve(async (_req) => {\n'
        '  return new Response(JSON.stringify({ ok: true }), {\n'
        '    headers: { "Content-Type": "application/json" },\n'
        '    status: 200,\n'
        '  });\n'
        '});\n'
    ),
    "supabase/functions/sync-chain-state/index.ts": (
        '// Supabase Edge Function: sync GenLayer chain state to database\n'
        'import { serve } from "https://deno.land/std@0.168.0/http/server.ts";\n\n'
        'serve(async (_req) => {\n'
        '  return new Response(JSON.stringify({ ok: true }), {\n'
        '    headers: { "Content-Type": "application/json" },\n'
        '    status: 200,\n'
        '  });\n'
        '});\n'
    ),

    # Config
    "config/site.ts": (
        'export const siteConfig = {\n'
        '  name: "GenLayer Consensus Simulator",\n'
        '  description: "An interactive educational platform for understanding GenLayer Intelligent Contracts and Optimistic Democracy.",\n'
        '  url: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",\n'
        '  primaryColor: "#efece4",\n'
        '};\n'
    ),
    "config/chains.ts": (
        'export const GENLAYER_STUDIO_NET = {\n'
        '  id: 42069,\n'
        '  name: "GenLayer Studio Net",\n'
        '  rpcUrl: process.env.NEXT_PUBLIC_GENLAYER_RPC_URL ?? "",\n'
        '};\n'
    ),

    # Monitoring / Security / Analytics
    "monitoring/sentry.ts": "// Sentry initialization\nexport {};\n",
    "security/rate-limit.ts": "// Rate limiting middleware\nexport {};\n",
    "analytics/events.ts": "export const EVENTS = {} as const;\n",

    # Root configs
    ".env.example": (
        "# Supabase\n"
        "NEXT_PUBLIC_SUPABASE_URL=\n"
        "NEXT_PUBLIC_SUPABASE_ANON_KEY=\n"
        "SUPABASE_SERVICE_ROLE_KEY=\n\n"
        "# GenLayer\n"
        "NEXT_PUBLIC_GENLAYER_RPC_URL=\n"
        "NEXT_PUBLIC_CONTRACT_ADDRESS_CONSENSUS=\n"
        "NEXT_PUBLIC_CONTRACT_ADDRESS_APPEALS=\n"
        "NEXT_PUBLIC_GENLAYER_CHAIN_ID=\n\n"
        "# App\n"
        "NEXT_PUBLIC_APP_URL=http://localhost:3000\n"
        "NEXTAUTH_SECRET=\n\n"
        "# Monitoring\n"
        "SENTRY_DSN=\n"
    ),
    "next.config.ts": (
        'import type { NextConfig } from "next";\n\n'
        'const config: NextConfig = {\n'
        '  reactStrictMode: true,\n'
        '  experimental: {\n'
        '    typedRoutes: true,\n'
        '  },\n'
        '};\n\n'
        'export default config;\n'
    ),
    "tailwind.config.ts": (
        'import type { Config } from "tailwindcss";\n\n'
        'const config: Config = {\n'
        '  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],\n'
        '  theme: {\n'
        '    extend: {\n'
        '      colors: {\n'
        '        primary: "#efece4",\n'
        '      },\n'
        '    },\n'
        '  },\n'
        '  plugins: [],\n'
        '};\n\n'
        'export default config;\n'
    ),
    "tsconfig.json": (
        '{\n'
        '  "compilerOptions": {\n'
        '    "target": "ES2017",\n'
        '    "lib": ["dom", "dom.iterable", "esnext"],\n'
        '    "allowJs": true,\n'
        '    "skipLibCheck": true,\n'
        '    "strict": true,\n'
        '    "noEmit": true,\n'
        '    "esModuleInterop": true,\n'
        '    "module": "esnext",\n'
        '    "moduleResolution": "bundler",\n'
        '    "resolveJsonModule": true,\n'
        '    "isolatedModules": true,\n'
        '    "jsx": "preserve",\n'
        '    "incremental": true,\n'
        '    "plugins": [{ "name": "next" }],\n'
        '    "paths": { "@/*": ["./*"] }\n'
        '  },\n'
        '  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],\n'
        '  "exclude": ["node_modules"]\n'
        '}\n'
    ),
    "vitest.config.ts": (
        'import { defineConfig } from "vitest/config";\n\n'
        'export default defineConfig({\n'
        '  test: {\n'
        '    environment: "node",\n'
        '    include: ["tests/unit/**/*.test.ts", "tests/integration/**/*.test.ts"],\n'
        '  },\n'
        '});\n'
    ),
    "playwright.config.ts": (
        'import { defineConfig } from "@playwright/test";\n\n'
        'export default defineConfig({\n'
        '  testDir: "./tests/e2e",\n'
        '  use: { baseURL: "http://localhost:3000" },\n'
        '});\n'
    ),
    "README.md": (
        "# GenLayer Consensus Simulator\n\n"
        "An interactive educational platform for understanding GenLayer Intelligent Contracts and Optimistic Democracy.\n\n"
        "## Tech Stack\n\n"
        "- Next.js 15, TypeScript, TailwindCSS, shadcn/ui\n"
        "- Supabase (PostgreSQL, Auth, Edge Functions, RLS)\n"
        "- GenLayer Studio Net (Intelligent Contracts, Optimistic Democracy)\n"
        "- Vercel (deployment)\n\n"
        "## Modules\n\n"
        "| Module | Route | Description |\n"
        "|---|---|---|\n"
        "| Consensus Playground | /playground | Submit claims, watch validators vote |\n"
        "| Validator Lab | /validator-lab | Experiment with validator personalities |\n"
        "| Appeals Arena | /appeals | Challenge decisions, observe new consensus |\n"
        "| Equivalence Explorer | /equivalence | Visualize acceptable disagreement ranges |\n"
        "| Democracy Dashboard | /democracy | See how consensus forms |\n"
        "| LLM Comparison Center | /llm-compare | Compare outputs across models |\n"
        "| Learning Center | /learn | Interactive GenLayer explanations |\n"
        "| Developer Sandbox | /sandbox | Test consensus scenarios |\n\n"
        "## Getting Started\n\n"
        "See [docs/developer-guide.md](docs/developer-guide.md)\n"
    ),

    # Docs
    "docs/architecture.md": (
        "# Architecture\n\n"
        "Three-tier architecture: Next.js (Vercel) → Supabase → GenLayer Studio Net.\n\n"
        "See Phase 1 design for full diagram and rationale.\n"
    ),
    "docs/api.md": "# API Reference\n\nTo be completed in Phase 3.\n",
    "docs/deployment.md": "# Deployment Guide\n\nTo be completed in Phase 5.\n",
    "docs/developer-guide.md": "# Developer Guide\n\nTo be completed.\n",
    "docs/genlayer-integration.md": (
        "# GenLayer Integration\n\n"
        "## Contracts\n\nSee /contracts directory.\n\n"
        "## SDK\n\nUses genlayer-js. Client initialized in lib/genlayer/client.ts.\n\n"
        "## Key Concepts Applied\n\n"
        "- `gl.exec_prompt()` — LLM evaluation inside validators\n"
        "- Equivalence Principle — comparative and non-comparative modes\n"
        "- Optimistic Democracy — leader + validator rounds\n"
        "- Appeals — re-opens consensus with expanded validator set\n"
    ),

    # Tests
    "tests/unit/validators.test.ts": (
        'import { describe, it, expect } from "vitest";\n'
        'describe("Validators", () => {\n'
        '  it("placeholder", () => expect(true).toBe(true));\n'
        '});\n'
    ),
    "tests/unit/consensus.test.ts": (
        'import { describe, it, expect } from "vitest";\n'
        'describe("Consensus", () => {\n'
        '  it("placeholder", () => expect(true).toBe(true));\n'
        '});\n'
    ),
    "tests/unit/equivalence.test.ts": (
        'import { describe, it, expect } from "vitest";\n'
        'describe("Equivalence", () => {\n'
        '  it("placeholder", () => expect(true).toBe(true));\n'
        '});\n'
    ),
    "tests/integration/simulation.test.ts": (
        'import { describe, it, expect } from "vitest";\n'
        'describe("Simulation Integration", () => {\n'
        '  it("placeholder", () => expect(true).toBe(true));\n'
        '});\n'
    ),
    "tests/integration/appeal.test.ts": (
        'import { describe, it, expect } from "vitest";\n'
        'describe("Appeal Integration", () => {\n'
        '  it("placeholder", () => expect(true).toBe(true));\n'
        '});\n'
    ),
    "tests/e2e/playground.spec.ts": (
        'import { test, expect } from "@playwright/test";\n'
        'test("playground loads", async ({ page }) => {\n'
        '  await page.goto("/playground");\n'
        '  await expect(page).toHaveTitle(/GenLayer/);\n'
        '});\n'
    ),
    "tests/e2e/appeals.spec.ts": (
        'import { test, expect } from "@playwright/test";\n'
        'test("appeals page loads", async ({ page }) => {\n'
        '  await page.goto("/appeals");\n'
        '});\n'
    ),
}


def create_file(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  CREATED  {path.relative_to(ROOT)}")


def main() -> None:
    print(f"\nScaffolding: GenLayer Consensus Simulator")
    print(f"Root: {ROOT}\n")

    for d in DIRS:
        (ROOT / d).mkdir(parents=True, exist_ok=True)
        print(f"  DIR      {d}")

    print()

    for rel_path, content in FILES.items():
        create_file(ROOT / rel_path, content)

    print(f"\nDone. {len(FILES)} files created across {len(DIRS)} directories.")


if __name__ == "__main__":
    main()
