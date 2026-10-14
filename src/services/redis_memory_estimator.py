"""
redis_memory_estimator.py

Estimates the Redis memory impact of a Celery task payload, to support
the pre-deploy "Redis memory impact" review step (POLICY-10 retro item 3).

Usage:
    estimator = RedisMemoryEstimator(redis_client)
    report = estimator.estimate_task_payload(task_name, args, kwargs)
    print(report.summary())

    # For an existing key already in Redis:
    report = estimator.estimate_existing_key("celery-task-meta-...")
"""
import json
import sys
from dataclasses import dataclass
from typing import Any, Optional

# Per-key overhead Redis adds beyond the raw payload bytes (hash table entry,
# key object, expiry structure, etc). This is a heuristic, not exact --
# real overhead varies by Redis version, encoding, and key type.
ESTIMATED_KEY_OVERHEAD_BYTES = 96


@dataclass
class MemoryEstimate:
    key_or_task: str
    payload_bytes: int
    estimated_total_bytes: int
    source: str  # "redis_memory_usage" | "heuristic"
    warning_threshold_bytes: int

    @property
    def exceeds_threshold(self) -> bool:
        return self.estimated_total_bytes > self.warning_threshold_bytes

    def summary(self) -> str:
        kb = self.estimated_total_bytes / 1024
        flag = "RISK" if self.exceeds_threshold else "ok"
        return (
            f"[{flag}] {self.key_or_task}: ~{kb:.1f} KB "
            f"(source={self.source}, threshold={self.warning_threshold_bytes / 1024:.1f} KB)"
        )


class RedisMemoryEstimator:
    """
    Estimates Redis memory impact for Celery task payloads and existing keys.

    redis_client: an optional redis-py client. When provided and the server
    supports it, MEMORY USAGE is used for existing keys (exact). When not
    provided, or for payloads that do not exist in Redis yet (e.g. a task
    about to be enqueued), falls back to a size heuristic based on the
    serialized JSON payload.
    """

    def __init__(self, redis_client: Optional[Any] = None,
                 warning_threshold_bytes: int = 64 * 1024):
        self.redis_client = redis_client
        self.warning_threshold_bytes = warning_threshold_bytes

    def estimate_task_payload(self, task_name: str, args: tuple = (),
                               kwargs: Optional[dict] = None) -> MemoryEstimate:
        """Heuristic estimate for a task payload that is not yet in Redis
        (e.g. during code review, before the task is enqueued)."""
        kwargs = kwargs or {}
        serialized = json.dumps({"args": args, "kwargs": kwargs})
        payload_bytes = len(serialized.encode("utf-8"))
        estimated_total = payload_bytes + ESTIMATED_KEY_OVERHEAD_BYTES
        return MemoryEstimate(
            key_or_task=task_name,
            payload_bytes=payload_bytes,
            estimated_total_bytes=estimated_total,
            source="heuristic",
            warning_threshold_bytes=self.warning_threshold_bytes,
        )

    def estimate_existing_key(self, redis_key: str) -> MemoryEstimate:
        """Exact estimate for a key already in Redis, using MEMORY USAGE
        when the connected server supports it; falls back to STRLEN heuristic."""
        if self.redis_client is None:
            raise ValueError("redis_client is required to inspect an existing key")

        try:
            usage = self.redis_client.memory_usage(redis_key)
            if usage is not None:
                return MemoryEstimate(
                    key_or_task=redis_key,
                    payload_bytes=usage,
                    estimated_total_bytes=usage,
                    source="redis_memory_usage",
                    warning_threshold_bytes=self.warning_threshold_bytes,
                )
        except Exception:
            pass  # MEMORY USAGE unsupported/disabled -- fall back below

        raw = self.redis_client.get(redis_key) or b""
        payload_bytes = len(raw)
        estimated_total = payload_bytes + ESTIMATED_KEY_OVERHEAD_BYTES
        return MemoryEstimate(
            key_or_task=redis_key,
            payload_bytes=payload_bytes,
            estimated_total_bytes=estimated_total,
            source="heuristic",
            warning_threshold_bytes=self.warning_threshold_bytes,
        )


if __name__ == "__main__":
    # Example CLI usage for a pre-deploy check:
    #   python redis_memory_estimator.py <task_name> '<json_args>' '<json_kwargs>'
    task = sys.argv[1] if len(sys.argv) > 1 else "example.task"
    call_args = tuple(json.loads(sys.argv[2])) if len(sys.argv) > 2 else ()
    call_kwargs = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

    est = RedisMemoryEstimator()
    print(est.estimate_task_payload(task, call_args, call_kwargs).summary())
