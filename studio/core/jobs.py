from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass
class JobResult(Generic[T]):
    idempotency_key: str
    value: T


class JobQueue:
    def __init__(self, *, max_retries_per_failure: int = 2):
        self._results: dict[str, JobResult] = {}
        self._failure_counts: dict[str, int] = {}
        self.max_retries_per_failure = max_retries_per_failure

    def run_once(self, idempotency_key: str, fn: Callable[[], T]) -> JobResult[T]:
        if idempotency_key in self._results:
            return self._results[idempotency_key]
        result = JobResult(idempotency_key, fn())
        self._results[idempotency_key] = result
        return result

    def record_failure(self, tag: str) -> bool:
        count = self._failure_counts.get(tag, 0) + 1
        self._failure_counts[tag] = count
        return count < self.max_retries_per_failure
