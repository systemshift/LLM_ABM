"""
Action processor for handling agent actions and interactions
"""

import random
import copy
from typing import Dict, Any, List, Optional
from .agent_system import Agent, AgentManager
from .environment import Environment
from .event_logger import EventLogger


class ActionProcessor:
    """
    Processes actions returned by agent behavior functions
    """

    def __init__(self, agent_manager: AgentManager, environment: Environment,
                 logger: EventLogger):
        """
        Initialize action processor

        Args:
            agent_manager: Agent management system
            environment: Environment system
            logger: Event logger
        """
        self.agent_manager = agent_manager
        self.environment = environment
        self.logger = logger

    def process_actions(self, agent: Agent, actions: List[Dict[str, Any]], step: int):
        """
        Process all actions for an agent

        Args:
            agent: The agent taking actions
            actions: List of action dictionaries
            step: Current simulation step
        """
        for action in actions:
            action_type = action.get("type")

            if action_type == "move":
                self._process_move(agent, action, step)
            elif action_type == "move_to":
                self._process_move_to(agent, action, step)
            elif action_type == "move_random":
                self._process_move_random(agent, step)
            elif action_type == "interact":
                self._process_interact(agent, action, step)
            elif action_type == "reproduce":
                self._process_reproduce(agent, action, step)
            elif action_type == "die":
                self._process_die(agent, action, step)
            elif action_type == "modify_state":
                self._process_modify_state(agent, action, step)
            elif action_type == "custom":
                self._process_custom(agent, action, step)
            else:
                # Unknown action type, log it
                self.logger.log_agent_action(
                    step=step,
                    agent_id=agent.id,
                    agent_type=agent.type,
                    action_type=action_type or "unknown",
                    details={"error": "Unknown action type"}
                )

    def _process_move(self, agent: Agent, action: Dict, step: int):
        """Process movement by direction"""
        direction = action.get("direction", [0, 0])
        current_pos = agent.state.get("position")

        if current_pos is None:
            return

        # Calculate new position
        if self.environment.env_type == "grid_2d":
            x, y = current_pos
            dx, dy = direction if isinstance(direction, (list, tuple)) else (0, 0)
            new_pos = (x + dx, y + dy)
            new_pos = self.environment.normalize_position(new_pos)

        elif self.environment.env_type == "continuous_2d":
            x, y = current_pos
            dx, dy = direction if isinstance(direction, (list, tuple)) else (0, 0)
            new_pos = (x + dx, y + dy)
            if self.environment.bounded:
                new_pos = self.environment.normalize_position(new_pos)

        else:
            # For other environment types, movement is handled differently
            return

        # Update position
        old_pos = agent.state["position"]
        agent.state["position"] = new_pos

        # Log the action
        self.logger.log_agent_action(
            step=step,
            agent_id=agent.id,
            agent_type=agent.type,
            action_type="move",
            details={"from": old_pos, "to": new_pos, "direction": direction}
        )

    def _process_move_to(self, agent: Agent, action: Dict, step: int):
        """Process movement to specific target position"""
        target = action.get("target")

        if target is None:
            return

        current_pos = agent.state.get("position")
        if current_pos is None:
            return

        # Move one step toward target
        if self.environment.env_type in ["grid_2d", "continuous_2d"]:
            x1, y1 = current_pos
            x2, y2 = target

            # Calculate direction
            dx = 1 if x2 > x1 else (-1 if x2 < x1 else 0)
            dy = 1 if y2 > y1 else (-1 if y2 < y1 else 0)

            new_pos = (x1 + dx, y1 + dy)
            new_pos = self.environment.normalize_position(new_pos)

            old_pos = agent.state["position"]
            agent.state["position"] = new_pos

            self.logger.log_agent_action(
                step=step,
                agent_id=agent.id,
                agent_type=agent.type,
                action_type="move_to",
                details={"from": old_pos, "to": new_pos, "target": target}
            )

    def _process_move_random(self, agent: Agent, step: int):
        """Process random movement"""
        current_pos = agent.state.get("position")
        if current_pos is None:
            return

        # Get random neighboring position
        neighbors = self.environment.get_neighbors(current_pos, radius=1)
        if not neighbors:
            return

        new_pos = random.choice(neighbors)
        old_pos = agent.state["position"]
        agent.state["position"] = new_pos

        self.logger.log_agent_action(
            step=step,
            agent_id=agent.id,
            agent_type=agent.type,
            action_type="move_random",
            details={"from": old_pos, "to": new_pos}
        )

    def _process_interact(self, agent: Agent, action: Dict, step: int):
        """Process interaction with another agent"""
        target_id = action.get("target_id")
        interaction_type = action.get("interaction_type", "generic")
        params = action.get("params", {})

        target = self.agent_manager.get_agent(target_id)
        if target is None or not target.alive:
            return

        # Log the interaction
        self.logger.log_interaction(
            step=step,
            agent_ids=[agent.id, target.id],
            interaction_type=interaction_type,
            outcome="success",
            details=params
        )

        # Specific interaction types
        if interaction_type == "predation":
            self._handle_predation(agent, target, params, step)
        elif interaction_type == "transfer_energy":
            self._handle_energy_transfer(agent, target, params, step)

    def _handle_predation(self, predator: Agent, prey: Agent,
                         params: Dict, step: int):
        """Handle predation interaction"""
        success_rate = params.get("success_rate", 0.5)
        energy_gain = params.get("energy_gain", 10)

        if random.random() < success_rate:
            # Successful predation
            prey.kill()
            predator.modify_attribute("energy", energy_gain)

            self.logger.log_agent_death(
                step=step,
                agent_id=prey.id,
                agent_type=prey.type,
                cause="predation"
            )

            self.logger.log_state_change(
                step=step,
                agent_id=predator.id,
                attribute="energy",
                old_value=predator.get_attribute("energy") - energy_gain,
                new_value=predator.get_attribute("energy"),
                cause="predation_success"
            )

    def _handle_energy_transfer(self, source: Agent, target: Agent,
                               params: Dict, step: int):
        """Handle energy transfer between agents"""
        amount = params.get("amount", 5)

        source_energy = source.get_attribute("energy", 0)
        if source_energy >= amount:
            source.modify_attribute("energy", -amount)
            target.modify_attribute("energy", amount)

            self.logger.log_interaction(
                step=step,
                agent_ids=[source.id, target.id],
                interaction_type="energy_transfer",
                outcome="success",
                details={"amount": amount}
            )

    def _process_reproduce(self, agent: Agent, action: Dict, step: int):
        """Process reproduction"""
        energy_cost = action.get("energy_cost", 10)
        offspring_count = action.get("offspring_count", 1)

        # Check if agent has enough energy
        if agent.get_attribute("energy", 0) < energy_cost:
            return

        # Create offspring
        for _ in range(offspring_count):
            offspring = agent.clone()
            offspring.set_attribute("energy", agent.get_attribute("energy", 0) // 2)
            offspring.set_attribute("age", 0)

            # Place offspring at parent's position
            offspring.state["position"] = agent.state.get("position")

            self.agent_manager.add_agent(offspring)

            self.logger.log_agent_birth(
                step=step,
                parent_id=agent.id,
                child_id=offspring.id,
                agent_type=offspring.type
            )

        # Deduct energy from parent
        agent.modify_attribute("energy", -energy_cost)

    def _process_die(self, agent: Agent, action: Dict, step: int):
        """Process agent death"""
        cause = action.get("cause", "voluntary")

        agent.kill()

        self.logger.log_agent_death(
            step=step,
            agent_id=agent.id,
            agent_type=agent.type,
            cause=cause
        )

    def _process_modify_state(self, agent: Agent, action: Dict, step: int):
        """Process modification of agent state"""
        attribute = action.get("attribute")
        value = action.get("value")
        delta = action.get("delta")

        if attribute is None:
            return

        old_value = agent.get_attribute(attribute)

        if value is not None:
            agent.set_attribute(attribute, value)
            new_value = value
        elif delta is not None:
            agent.modify_attribute(attribute, delta)
            new_value = agent.get_attribute(attribute)
        else:
            return

        self.logger.log_state_change(
            step=step,
            agent_id=agent.id,
            attribute=attribute,
            old_value=old_value,
            new_value=new_value,
            cause="modify_state_action"
        )

    def _process_custom(self, agent: Agent, action: Dict, step: int):
        """Process custom action"""
        self.logger.log_agent_action(
            step=step,
            agent_id=agent.id,
            agent_type=agent.type,
            action_type="custom",
            details=action.get("details", {})
        )
