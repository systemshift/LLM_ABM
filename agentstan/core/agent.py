"""
Dynamic agent system with flexible attributes and behaviors
"""

import copy
from typing import Dict, Any, List, Optional, Callable


class Agent:
    """
    Dynamic agent with arbitrary attributes and behavior function
    """

    _next_id = 1

    def __init__(self, agent_type: str, initial_state: Dict[str, Any],
                 behavior_function: Optional[Callable] = None):
        """
        Initialize agent

        Args:
            agent_type: Type/species of agent
            initial_state: Initial attribute values
            behavior_function: Function that defines agent behavior
        """
        self.id = Agent._next_id
        Agent._next_id += 1

        self.type = agent_type
        self.alive = True
        self.state = copy.deepcopy(initial_state)
        self.behavior_function = behavior_function

        # Ensure position exists
        if "position" not in self.state:
            self.state["position"] = None

    def execute_behavior(self, simulation_state: Dict[str, Any],
                        agents_nearby: List['Agent']) -> List[Dict[str, Any]]:
        """
        Execute this agent's behavior function

        Args:
            simulation_state: Full simulation state
            agents_nearby: List of nearby agents

        Returns:
            List of actions to take
        """
        if not self.alive or self.behavior_function is None:
            return []

        try:
            # Call the behavior function
            actions = self.behavior_function(self, simulation_state, agents_nearby)
            return actions if actions else []
        except Exception as e:
            # Log error but don't crash simulation
            print(f"Error in agent {self.id} behavior: {e}")
            return []

    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Get agent attribute value"""
        return self.state.get(name, default)

    def set_attribute(self, name: str, value: Any):
        """Set agent attribute value"""
        self.state[name] = value

    def modify_attribute(self, name: str, delta: Any):
        """Modify numeric attribute by delta"""
        current = self.get_attribute(name, 0)
        self.set_attribute(name, current + delta)

    def __getitem__(self, key: str) -> Any:
        """Dict-style access: agent['energy']"""
        return self.state[key]

    def __setitem__(self, key: str, value: Any):
        """Dict-style assignment: agent['energy'] = 10"""
        self.state[key] = value

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator: 'energy' in agent"""
        return key in self.state

    def kill(self):
        """Mark agent as dead"""
        self.alive = False

    def clone(self) -> 'Agent':
        """Create a copy of this agent with new ID"""
        new_agent = Agent(
            agent_type=self.type,
            initial_state=copy.deepcopy(self.state),
            behavior_function=self.behavior_function
        )
        return new_agent

    def to_dict(self) -> Dict[str, Any]:
        """Export agent as dictionary"""
        return {
            "id": self.id,
            "type": self.type,
            "alive": self.alive,
            "state": copy.deepcopy(self.state)
        }

    def __repr__(self):
        return f"Agent(id={self.id}, type={self.type}, alive={self.alive})"


class AgentManager:
    """
    Manages all agents in a simulation
    """

    def __init__(self):
        """Initialize agent manager"""
        self.agents: List[Agent] = []
        self.agents_by_type: Dict[str, List[Agent]] = {}

    def add_agent(self, agent: Agent):
        """Add an agent to the simulation"""
        self.agents.append(agent)

        if agent.type not in self.agents_by_type:
            self.agents_by_type[agent.type] = []
        self.agents_by_type[agent.type].append(agent)

    def remove_agent(self, agent: Agent):
        """Remove an agent from the simulation"""
        if agent in self.agents:
            self.agents.remove(agent)
        if agent.type in self.agents_by_type and agent in self.agents_by_type[agent.type]:
            self.agents_by_type[agent.type].remove(agent)

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get agent by ID"""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None

    def get_living_agents(self) -> List[Agent]:
        """Get all living agents"""
        return [a for a in self.agents if a.alive]

    def get_agents_by_type(self, agent_type: str) -> List[Agent]:
        """Get all living agents of a specific type"""
        return [a for a in self.agents_by_type.get(agent_type, []) if a.alive]

    def get_agents_at_position(self, position: Any) -> List[Agent]:
        """Get all living agents at a specific position"""
        return [
            a for a in self.agents
            if a.alive and a.state.get("position") == position
        ]

    def get_agents_near_position(self, position: Any, radius: float,
                                 environment) -> List[Agent]:
        """Get all living agents within radius of position"""
        nearby = []
        for agent in self.agents:
            if not agent.alive:
                continue

            agent_pos = agent.state.get("position")
            if agent_pos is None:
                continue

            dist = environment.distance(position, agent_pos)
            if dist <= radius:
                nearby.append(agent)

        return nearby

    def get_agents_near_agent(self, agent: Agent, radius: float,
                             environment) -> List[Agent]:
        """Get all living agents within radius of an agent"""
        position = agent.state.get("position")
        if position is None:
            return []

        nearby = self.get_agents_near_position(position, radius, environment)
        # Remove the agent itself
        return [a for a in nearby if a.id != agent.id]

    def cleanup_dead_agents(self):
        """Remove dead agents from active lists"""
        self.agents = [a for a in self.agents if a.alive]
        for agent_type in self.agents_by_type:
            self.agents_by_type[agent_type] = [
                a for a in self.agents_by_type[agent_type] if a.alive
            ]

    def get_counts(self) -> Dict[str, int]:
        """Get count of living agents by type"""
        counts = {}
        for agent_type, agents in self.agents_by_type.items():
            counts[agent_type] = sum(1 for a in agents if a.alive)
        return counts

    def get_total_count(self) -> int:
        """Get total count of living agents"""
        return sum(1 for a in self.agents if a.alive)

    def reset(self):
        """Clear all agents and reset ID counter"""
        self.agents = []
        self.agents_by_type = {}
        Agent._next_id = 1

    def to_dict(self) -> Dict[str, Any]:
        """Export all agents as dictionary"""
        return {
            "agents": [a.to_dict() for a in self.agents],
            "counts": self.get_counts(),
            "total": self.get_total_count()
        }
