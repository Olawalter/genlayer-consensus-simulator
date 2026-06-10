# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class AppealManager(gl.Contract):
    """Manages appeal rounds for disputed consensus outcomes."""

    appeals: dict

    def __init__(self) -> None:
        self.appeals = {}

    @gl.public.view
    def get_appeal(self, appeal_id: str) -> dict:
        return self.appeals.get(appeal_id, {})

    @gl.public.write
    def open_appeal(self, appeal_id: str, claim: str, original_verdict: str, reason: str) -> None:
        re_evaluation = gl.exec_prompt(
            f"An appeal has been raised against this verdict: {original_verdict}.\n"
            f"Appeal reason: {reason}\n"
            f"Original claim: {claim}\n"
            f"Re-evaluate carefully. Answer ACCEPT or REJECT only.\n"
            f"Answer:"
        )
        self.appeals[appeal_id] = {
            "claim": claim,
            "original_verdict": original_verdict,
            "reason": reason,
            "re_verdict": re_evaluation.strip(),
        }
