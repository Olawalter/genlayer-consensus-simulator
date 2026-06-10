# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class ConsensusSimulator(gl.Contract):
    """GenLayer Intelligent Contract for subjective consensus simulation."""

    simulations: dict

    def __init__(self) -> None:
        self.simulations = {}

    @gl.public.view
    def get_simulation(self, simulation_id: str) -> dict:
        return self.simulations.get(simulation_id, {})

    @gl.public.write
    def evaluate_claim(self, simulation_id: str, claim: str) -> None:
        verdict = gl.exec_prompt(
            f"You are a neutral evaluator. Answer ACCEPT or REJECT only.\n"
            f"Claim: {claim}\n"
            f"Answer:"
        )
        self.simulations[simulation_id] = {
            "verdict": verdict.strip(),
            "claim": claim,
        }
