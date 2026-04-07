"""
Observation system for rich per-agent simulation snapshots.
"""

import copy
from typing import Dict, Any, List, Optional, Callable
from .agent import Agent, AgentManager


class AgentSnapshot:
    """Rich point-in-time snapshot of a single agent."""

    __slots__ = ("agent_id", "agent_type", "step", "state", "position",
                 "alive", "nearby", "narrative")

    def __init__(self, agent_id: int, agent_type: str, step: int,
                 state: Dict[str, Any], position: Any, alive: bool,
                 nearby: List[Dict[str, Any]], narrative: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.step = step
        self.state = state
        self.position = position
        self.alive = alive
        self.nearby = nearby
        self.narrative = narrative

    @staticmethod
    def from_agent(agent: Agent, step: int, environment, agent_manager: AgentManager) -> "AgentSnapshot":
        position = agent.get_attribute("position")
        nearby = []

        if position is not None:
            perception = agent.get_attribute("perception_radius", 5)
            for other in agent_manager.get_agents_near_agent(agent, perception, environment):
                other_pos = other.get_attribute("position")
                dist = environment.distance(position, other_pos) if other_pos else float("inf")
                nearby.append({
                    "id": other.id,
                    "type": other.type,
                    "distance": round(dist, 1),
                    "energy": other.get_attribute("energy"),
                    "alive": other.alive,
                })

        nearby.sort(key=lambda n: n["distance"])

        # Build narrative
        parts = [f"{agent.type} #{agent.id}"]
        if position:
            parts.append(f"at {position}")
        energy = agent.get_attribute("energy")
        if energy is not None:
            parts.append(f"energy {round(energy, 1)}")
        if nearby:
            nearest = nearby[0]
            parts.append(f"nearest {nearest['type']} #{nearest['id']} {nearest['distance']} away")
        narrative = ", ".join(parts)

        return AgentSnapshot(
            agent_id=agent.id,
            agent_type=agent.type,
            step=step,
            state=copy.deepcopy(agent.state),
            position=position,
            alive=agent.alive,
            nearby=nearby,
            narrative=narrative,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "step": self.step,
            "state": self.state,
            "position": self.position,
            "alive": self.alive,
            "nearby": self.nearby,
            "narrative": self.narrative,
        }


class SimulationSnapshot:
    """Full simulation state at a point in time."""

    def __init__(self, step: int, environment: Dict[str, Any],
                 agents: Dict[int, AgentSnapshot], counts: Dict[str, int]):
        self.step = step
        self.environment = environment
        self.agents = agents
        self.counts = counts

    def get_agent(self, agent_id: int) -> Optional[AgentSnapshot]:
        return self.agents.get(agent_id)

    def get_agents_by_type(self, agent_type: str) -> List[AgentSnapshot]:
        return [a for a in self.agents.values() if a.agent_type == agent_type]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "environment": self.environment,
            "counts": self.counts,
            "agents": {aid: a.to_dict() for aid, a in self.agents.items()},
        }

    @staticmethod
    def from_simulation(sim, agent_ids: Optional[List[int]] = None) -> "SimulationSnapshot":
        agents = {}
        for agent in sim.agent_manager.get_living_agents():
            if agent_ids and agent.id not in agent_ids:
                continue
            agents[agent.id] = AgentSnapshot.from_agent(
                agent, sim.step, sim.environment, sim.agent_manager
            )
        return SimulationSnapshot(
            step=sim.step,
            environment=sim.environment.to_dict(),
            agents=agents,
            counts=sim.agent_manager.get_counts(),
        )


class Observer:
    """
    Attaches to a simulation as a collector. Produces rich snapshots
    and fires callbacks for external consumers (web UI, AI observer).
    """

    def __init__(
        self,
        watch_agents: Optional[List[int]] = None,
        watch_types: Optional[List[str]] = None,
        every_n_steps: int = 1,
    ):
        self.watch_agents = watch_agents
        self.watch_types = watch_types
        self.every_n_steps = every_n_steps
        self.history: List[SimulationSnapshot] = []
        self.callbacks: List[Callable[["SimulationSnapshot"], None]] = []

    def collect(self, simulation) -> None:
        """DataCollector-compatible interface. Called after each step."""
        if simulation.step % self.every_n_steps != 0:
            return

        # Filter agent IDs if watching specific agents/types
        agent_ids = None
        if self.watch_agents:
            agent_ids = self.watch_agents
        elif self.watch_types:
            agent_ids = [
                a.id for a in simulation.agent_manager.get_living_agents()
                if a.type in self.watch_types
            ]

        snapshot = SimulationSnapshot.from_simulation(simulation, agent_ids)
        self.history.append(snapshot)

        for cb in self.callbacks:
            cb(snapshot)

    def on_snapshot(self, callback: Callable[["SimulationSnapshot"], None]) -> None:
        """Register callback fired each time a snapshot is taken."""
        self.callbacks.append(callback)

    def get_agent_history(self, agent_id: int) -> List[AgentSnapshot]:
        """Get time series of snapshots for one agent."""
        result = []
        for snap in self.history:
            agent_snap = snap.get_agent(agent_id)
            if agent_snap:
                result.append(agent_snap)
        return result

    def get_latest(self) -> Optional[SimulationSnapshot]:
        return self.history[-1] if self.history else None
