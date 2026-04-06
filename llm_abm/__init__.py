"""
LLM-ABM: Agent-Based Modeling Library

A simulation engine for agent-based models. Agents are defined with
Python behavior functions that return action lists. Supports grid,
continuous, and network environments.

Optional LLM integration (pip install llm-abm[chat]) lets you generate
simulation specs from natural language via OpenAI.
"""

from .core.simulation import Simulation
from .core.agent_system import Agent, AgentManager
from .core.environment import Environment
from .prompt import get_system_prompt

__version__ = "0.3.0"

__all__ = [
    # Core engine
    "Simulation",
    "Agent",
    "AgentManager",
    "Environment",
    # Convenience functions
    "create_simulation",
    "run",
    "export",
    # Prompt (for building your own LLM integration)
    "get_system_prompt",
]


def create_simulation(spec: dict) -> Simulation:
    """Create a simulation from a specification dict."""
    return Simulation(spec)


def run(simulation: Simulation, steps: int = 200) -> dict:
    """Run a simulation for the given number of steps."""
    return simulation.run(steps)


def export(results: dict, filename: str, format: str = "json") -> str:
    """Export simulation results to a file."""
    import json
    import csv

    if format == "json":
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
    elif format == "csv":
        events = results.get("events", [])
        if events:
            fieldnames = set()
            for event in events:
                fieldnames.update(event.keys())
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                for event in events:
                    row = {
                        k: str(v) if isinstance(v, (list, dict)) else v
                        for k, v in event.items()
                    }
                    writer.writerow(row)
    else:
        raise ValueError(f"Unknown format: {format}")

    return filename
