import json
import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LabInputError(ValueError):
    message: str
    status_code: int = 400

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class ReplayWorkload:
    instances: int
    iterations: int
    continue_every: int


def parse_delay(raw: str) -> int:
    if not re.fullmatch(r"[0-9]{1,5}", raw) or int(raw) > 25000:
        raise LabInputError("delay_ms must be an integer from 0 to 25000")
    return int(raw)


def parse_replay(body: bytes, defaults: tuple[str, str]) -> ReplayWorkload:
    if len(body) > 4096:
        raise LabInputError("Request body exceeds 4096 bytes", 413)
    try:
        payload = json.loads(body) if body else {}
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise LabInputError("Expected a JSON object") from None
    if not isinstance(payload, dict):
        raise LabInputError("Expected a JSON object")
    try:
        default_iterations, default_continue = (int(value) for value in defaults)
    except ValueError:
        raise LabInputError("Invalid DurableLab configuration", 503) from None
    values = (
        payload.get("instances", 1),
        payload.get("iterations", default_iterations),
        payload.get("continueAsNewEvery", default_continue),
    )
    for name, value, lower, upper in zip(
        ("instances", "iterations", "continueAsNewEvery"), values, (1, 1, 0), (10, 5000, 5000)
    ):
        if type(value) is not int or not lower <= value <= upper:
            raise LabInputError(f"{name} must be an integer from {lower} to {upper}")
    instances, iterations, continue_every = values
    if instances * iterations > 5000:
        raise LabInputError("instances * iterations must not exceed 5000")
    return ReplayWorkload(instances, iterations, continue_every)
