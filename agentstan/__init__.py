"""
AgentStan: AI-native agent-based modeling framework.

STAN = Simulate, Test, Analyze, Narrate.

    from agentstan import Simulation                    # Simulate
    from agentstan.experiment import batch_run, sweep   # Test
    from agentstan.analysis import analyze_population   # Analyze
    from agentstan.ai import generate, interpret        # Narrate
"""

from .core.simulation import Simulation
from .core.agent import Agent, AgentManager
from .core.environment import Environment
from .core.collectors import DataCollector
from .core.scheduler import RandomScheduler, StagedScheduler, SimultaneousScheduler

__version__ = "1.0.0"

__all__ = [
    "Simulation",
    "Agent",
    "AgentManager",
    "Environment",
    "DataCollector",
    "RandomScheduler",
    "StagedScheduler",
    "SimultaneousScheduler",
]
