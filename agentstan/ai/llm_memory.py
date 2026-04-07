"""
Agent memory system for LLM-powered agents.

Rolling buffer of observations and actions, stored in agent.state["_memory"].
"""

from typing import Dict, Any, List, Optional


class AgentMemory:
    """Rolling memory buffer for an LLM agent."""

    def __init__(self, max_entries: int = 20, summary_threshold: int = 15):
        self.entries: List[Dict[str, Any]] = []
        self.max_entries = max_entries
        self.summary_threshold = summary_threshold
        self.summary: Optional[str] = None

    def add(self, step: int, observation: str, action_taken: str, outcome: str = "") -> None:
        self.entries.append({
            "step": step,
            "observation": observation,
            "action": action_taken,
            "outcome": outcome,
        })
        if len(self.entries) > self.max_entries:
            self._compress()

    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        return self.entries[-n:]

    def to_prompt_text(self) -> str:
        """Format memory as text for LLM prompt injection."""
        parts = []
        if self.summary:
            parts.append(f"[Earlier: {self.summary}]")
        for entry in self.entries[-8:]:
            line = f"Step {entry['step']}: {entry['observation']}. Did: {entry['action']}."
            if entry.get("outcome"):
                line += f" Result: {entry['outcome']}."
            parts.append(line)
        return "\n".join(parts) if parts else "No memories yet."

    def _compress(self) -> None:
        """Compress old entries into summary string."""
        if len(self.entries) <= self.summary_threshold:
            return
        # Keep recent entries, summarize the rest
        to_summarize = self.entries[:-self.summary_threshold]
        self.entries = self.entries[-self.summary_threshold:]

        summary_parts = []
        if self.summary:
            summary_parts.append(self.summary)
        for entry in to_summarize:
            summary_parts.append(f"step {entry['step']}: {entry['action']}")

        # Truncate summary to avoid unbounded growth
        self.summary = "; ".join(summary_parts)[-500:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": self.entries,
            "summary": self.summary,
            "max_entries": self.max_entries,
            "summary_threshold": self.summary_threshold,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AgentMemory":
        if not data:
            return AgentMemory()
        mem = AgentMemory(
            max_entries=data.get("max_entries", 20),
            summary_threshold=data.get("summary_threshold", 15),
        )
        mem.entries = data.get("entries", [])
        mem.summary = data.get("summary")
        return mem
