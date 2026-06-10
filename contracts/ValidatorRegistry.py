# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class ValidatorRegistry(gl.Contract):
    """Registry of validator identities and models."""

    validators: dict

    def __init__(self) -> None:
        self.validators = {}

    @gl.public.view
    def get_validator(self, validator_id: str) -> dict:
        return self.validators.get(validator_id, {})

    @gl.public.write
    def register_validator(self, validator_id: str, name: str, model: str, persona: str) -> None:
        self.validators[validator_id] = {
            "name": name,
            "model": model,
            "persona": persona,
            "active": True,
        }
