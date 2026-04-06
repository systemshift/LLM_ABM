"""
Agent activation schedulers.

Control the order in which agents execute each step.
"""

import random
from typing import List
from .agent import Agent, AgentManager


class RandomScheduler:
    """Shuffle agent order each step (default)."""

    def get_agents(self, manager: AgentManager) -> List[Agent]:
        agents = manager.get_living_agents()
        random.shuffle(agents)
        return agents


class StagedScheduler:
    """Execute all agents of type A, then type B, etc."""

    def __init__(self, stage_order: List[str] = None):
        self.stage_order = stage_order

    def get_agents(self, manager: AgentManager) -> List[Agent]:
        order = self.stage_order or sorted(manager.agents_by_type.keys())
        agents = []
        for agent_type in order:
            type_agents = manager.get_agents_by_type(agent_type)
            random.shuffle(type_agents)
            agents.extend(type_agents)
        return agents


class SimultaneousScheduler:
    """
    All agents decide simultaneously, then all actions apply at once.

    Returns agents in random order but the simulation should collect
    all actions before processing any of them.
    """

    simultaneous = True

    def get_agents(self, manager: AgentManager) -> List[Agent]:
        agents = manager.get_living_agents()
        random.shuffle(agents)
        return agents
