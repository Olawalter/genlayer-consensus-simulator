# GenLayer Intelligent Contracts

## Contracts

- **ConsensusSimulator.py** — evaluates subjective claims via LLM, stores verdicts on-chain
- **AppealManager.py** — handles appeal re-evaluation rounds
- **ValidatorRegistry.py** — stores validator identities and models

## Deployment

1. Open GenLayer Studio: https://studio.genlayer.com
2. Paste each contract into the editor
3. Deploy to Studio Net
4. Copy the contract address
5. Set NEXT_PUBLIC_CONTRACT_ADDRESS_CONSENSUS in .env.local

## Key GenLayer Patterns

- `gl.exec_prompt()` — calls the validator's assigned LLM
- `@gl.public.view` — read-only, no consensus required
- `@gl.public.write` — state-changing, triggers Optimistic Democracy
- Each validator re-executes the contract independently
- Equivalence Principle determines if outputs are close enough to accept
