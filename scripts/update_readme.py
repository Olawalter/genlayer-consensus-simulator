"""Update README.md to reflect current tech stack and setup."""
import pathlib

ROOT = pathlib.Path("C:/GenB/GenLayer Consensus Simulator")
readme = ROOT / "README.md"

readme.write_text('''\
# GenLayer Consensus Simulator

An interactive educational platform for understanding GenLayer Intelligent Contracts and Optimistic Democracy. Submit real claims, watch five AI validators independently evaluate them on GenLayer Studio Net, and observe on-chain consensus in action.

**Live:** https://genlayer-consensus-simulator.vercel.app

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router), TypeScript |
| Styling | TailwindCSS, shadcn/ui, Framer Motion |
| Auth | Firebase Auth (email/password) |
| Database | Firebase Firestore |
| Blockchain | GenLayer Studio Net via genlayer-js |
| Deployment | Vercel |

---

## Modules

| Module | Route | Description |
|---|---|---|
| Consensus Playground | `/playground` | Submit claims, watch 5 validators vote on-chain |
| Developer Sandbox | `/sandbox` | Deploy and test Intelligent Contracts live |
| Validator Lab | `/validator-lab` | Experiment with validator personas |
| Appeals Arena | `/appeals` | Challenge decisions, trigger new consensus rounds |
| Equivalence Explorer | `/equivalence` | Visualize the Equivalence Principle |
| Democracy Dashboard | `/democracy` | See how Optimistic Democracy forms consensus |
| LLM Comparison | `/llm-compare` | Compare outputs across models |
| Learning Center | `/learn` | Interactive GenLayer explanations |

---

## How It Works

1. User submits a claim in the Playground
2. A `ClaimEvaluator` Intelligent Contract is deployed to GenLayer Studio Net
3. The contract\'s `evaluate()` method calls an LLM via `gl.vm.run_nondet_unsafe` — each of 5 validators runs this independently
4. The chain reaches consensus (Optimistic Democracy / Equivalence Principle)
5. Real validator votes, tx hash, and contract address are displayed in the UI

---

## Local Development

### Prerequisites

- Node.js 20+
- GenLayer Studio running locally at `http://localhost:4000`
- Firebase project with Auth and Firestore enabled

### Setup

```bash
git clone https://github.com/Olawalter/genlayer-consensus-simulator.git
cd genlayer-consensus-simulator
npm install
cp .env.example .env.local
# fill in .env.local with your Firebase and GenLayer credentials
npm run dev
```

### Environment Variables

```env
# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
FIREBASE_SERVICE_ACCOUNT_KEY=   # JSON string (server-side only)

# GenLayer Studio Net (client-side — local testnet only)
NEXT_PUBLIC_GENLAYER_PRIVATE_KEY=
NEXT_PUBLIC_GENLAYER_RPC_URL=http://localhost:4000/api
```

> `NEXT_PUBLIC_GENLAYER_PRIVATE_KEY` is only used against a local Studio Net instance — never use a key with real value here.

---

## GenLayer Contract

The core Intelligent Contract ([lib/genlayer/contracts.ts](lib/genlayer/contracts.ts)) uses the correct GenLayer LLM API:

```python
def evaluate(self, claim: str) -> None:
    def leader_fn():
        return gl.nondet.exec_prompt(
            f"Evaluate: {claim} — respond YES or NO"
        )
    def validator_fn(leader_result) -> bool:
        return isinstance(leader_result, gl.vm.Return) and \\
               leader_result.calldata.strip().upper()[:3] in ("YES", "NO")

    response = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
    self.result = str(response).strip().upper()[:3]
```

---

## CI / CD

GitHub Actions handles type-checking and deployment on every push to `main`.

Required GitHub repository secrets:

| Secret | Description |
|---|---|
| `VERCEL_TOKEN` | Vercel personal access token |
| `VERCEL_ORG_ID` | Vercel team/org ID |
| `VERCEL_PROJECT_ID` | Vercel project ID |

See [docs/developer-guide.md](docs/developer-guide.md) for full setup details.
''', encoding="utf-8")

print(f"Written: {readme}")
