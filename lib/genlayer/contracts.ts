// Standard Intelligent Contract used by the Playground claim simulator
export const CLAIM_EVALUATOR_CONTRACT = `# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

class ClaimEvaluator(gl.Contract):
    result: str
    claim: str

    def __init__(self) -> None:
        self.result = ""
        self.claim = ""

    @gl.public.view
    def get_result(self) -> str:
        return self.result

    @gl.public.view
    def get_claim(self) -> str:
        return self.claim

    @gl.public.write
    def evaluate(self, claim: str) -> None:
        self.claim = claim

        def leader_fn():
            return gl.nondet.exec_prompt(
                f"You are a fact-checking validator on the GenLayer blockchain. "
                f"Evaluate the following claim and respond with ONLY the word YES or NO. "
                f"Respond YES if the claim is accurate or valid, NO if it is not. "
                f"Claim: {claim}"
            )

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            return isinstance(leader_result.calldata, str) and leader_result.calldata.strip().upper()[:3] in ("YES", "NO")

        response = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        self.result = str(response).strip().upper()[:3]
`;
