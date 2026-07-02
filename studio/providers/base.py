from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Estimate:
    provider: str
    model: str
    cost_usd: float


@dataclass(frozen=True)
class Generation:
    provider: str
    model: str
    job_id: str
    output_path: Path


class Provider(Protocol):
    def estimate(self, *, prompt: str, duration_sec: float = 0, kind: str = "video") -> Estimate:
        ...

    def generate(self, *, prompt: str, output_dir: Path, duration_sec: float = 1, kind: str = "video") -> Generation:
        ...
