"""
Cost control for LLM agent calls.
"""

from typing import Dict, Any, List, Optional


class LLMBudget:
    """Tracks and enforces LLM call budgets."""

    def __init__(
        self,
        max_calls_per_step: Optional[int] = None,
        max_calls_total: Optional[int] = None,
    ):
        self.max_calls_per_step = max_calls_per_step
        self.max_calls_total = max_calls_total

        self.calls_this_step = 0
        self.calls_total = 0
        self.tokens_total = 0
        self.log: List[Dict[str, Any]] = []

    def can_call(self, n: int = 1) -> bool:
        if self.max_calls_per_step and self.calls_this_step + n > self.max_calls_per_step:
            return False
        if self.max_calls_total and self.calls_total + n > self.max_calls_total:
            return False
        return True

    def record_call(self, prompt_tokens: int = 0, completion_tokens: int = 0,
                    model: str = "", agent_id: int = 0) -> None:
        self.calls_this_step += 1
        self.calls_total += 1
        self.tokens_total += prompt_tokens + completion_tokens
        self.log.append({
            "agent_id": agent_id,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        })

    def reset_step(self) -> None:
        self.calls_this_step = 0

    @property
    def exhausted(self) -> bool:
        if self.max_calls_total and self.calls_total >= self.max_calls_total:
            return True
        return False

    def get_summary(self) -> Dict[str, Any]:
        return {
            "calls_total": self.calls_total,
            "tokens_total": self.tokens_total,
            "calls_this_step": self.calls_this_step,
            "budget_remaining": (
                self.max_calls_total - self.calls_total
                if self.max_calls_total else None
            ),
        }
