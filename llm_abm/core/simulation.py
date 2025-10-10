"""
Main simulation engine for general-purpose agent-based modeling
"""

import copy
import time
from typing import Dict, Any, List, Optional, Callable

from .environment import Environment
from .agent_system import Agent, AgentManager
from .action_processor import ActionProcessor
from .event_logger import EventLogger


class Simulation:
    """
    Core simulation engine that manages environment, agents, and execution
    """

    def __init__(self, specification: Dict[str, Any]):
        """
        Initialize simulation from specification

        Args:
            specification: Complete simulation specification dictionary
        """
        self.spec = specification
        self.step = 0

        # Initialize core systems
        self.environment = self._create_environment()
        self.agent_manager = AgentManager()
        self.logger = EventLogger(
            enabled=True,
            log_level=specification.get("log_level", "normal")
        )
        self.action_processor = ActionProcessor(
            self.agent_manager,
            self.environment,
            self.logger
        )

        # Initialize agents
        self._create_agents()

        # Store global functions (like reproduction, death)
        self.global_functions = specification.get("global_functions", {})

        # Metrics
        self.metrics = {
            "initial_agents": self.agent_manager.get_total_count(),
            "initial_counts": self.agent_manager.get_counts(),
            "history": []
        }

    def _create_environment(self) -> Environment:
        """Create environment from specification"""
        env_spec = self.spec.get("environment", {})
        return Environment.from_dict(env_spec)

    def _create_agents(self):
        """Create initial agent population from specification"""
        agent_types = self.spec.get("agent_types", {})

        for agent_type, type_spec in agent_types.items():
            initial_count = type_spec.get("initial_count", 0)
            initial_state = type_spec.get("initial_state", {})
            behavior_code = type_spec.get("behavior_code", "")

            # Compile behavior function if provided
            behavior_func = None
            if behavior_code:
                behavior_func = self._compile_behavior_function(
                    agent_type,
                    behavior_code
                )

            # Create agents
            for _ in range(initial_count):
                agent = Agent(
                    agent_type=agent_type,
                    initial_state=copy.deepcopy(initial_state),
                    behavior_function=behavior_func
                )

                # Assign random position if not set
                if agent.state.get("position") is None:
                    agent.state["position"] = self.environment.get_random_position()

                self.agent_manager.add_agent(agent)

    def _compile_behavior_function(self, agent_type: str,
                                   behavior_code: str) -> Optional[Callable]:
        """
        Compile behavior code into executable function

        Args:
            agent_type: Type of agent
            behavior_code: Python code defining behavior

        Returns:
            Compiled function or None
        """
        try:
            import random
            import math

            # Create safe namespace for execution
            # Provide modules directly so code doesn't need to import
            namespace = {
                '__builtins__': {
                    'abs': abs, 'len': len, 'max': max, 'min': min,
                    'sum': sum, 'range': range, 'enumerate': enumerate,
                    'list': list, 'dict': dict, 'str': str, 'int': int,
                    'float': float, 'bool': bool, 'any': any, 'all': all,
                    'sorted': sorted, 'reversed': reversed
                },
                'random': random,  # Provide module directly
                'math': math  # Provide module directly
            }

            # Execute the code to define the function
            exec(behavior_code, namespace)

            # Look for function with expected name
            func_name = f"{agent_type}_behavior"
            if func_name in namespace:
                return namespace[func_name]

            # Otherwise look for any function
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    return obj

            return None

        except Exception as e:
            print(f"Error compiling behavior for {agent_type}: {e}")
            return None

    def run_step(self):
        """Execute one simulation step"""
        self.step += 1

        # Update environment
        self.environment.update(self.step)

        # Get all living agents
        agents = self.agent_manager.get_living_agents()

        # Execute behavior for each agent
        for agent in agents:
            if not agent.alive:
                continue

            # Get nearby agents for context
            perception_radius = agent.get_attribute("perception_radius", 5)
            agents_nearby = self.agent_manager.get_agents_near_agent(
                agent,
                perception_radius,
                self.environment
            )

            # Build simulation state for agent
            sim_state = {
                "step": self.step,
                "environment": self.environment.to_dict(),
                "agent_counts": self.agent_manager.get_counts()
            }

            # Execute agent behavior
            actions = agent.execute_behavior(sim_state, agents_nearby)

            # Process actions
            if actions:
                self.action_processor.process_actions(agent, actions, self.step)

        # Apply global functions (e.g., death conditions)
        self._apply_global_functions()

        # Clean up dead agents
        self.agent_manager.cleanup_dead_agents()

        # Record metrics
        self._record_metrics()

    def _apply_global_functions(self):
        """Apply global functions to all agents"""
        # Example: automatic death when energy <= 0
        for agent in self.agent_manager.get_living_agents():
            energy = agent.get_attribute("energy", None)
            if energy is not None and energy <= 0:
                agent.kill()
                self.logger.log_agent_death(
                    step=self.step,
                    agent_id=agent.id,
                    agent_type=agent.type,
                    cause="energy_depleted"
                )

    def _record_metrics(self):
        """Record step metrics"""
        counts = self.agent_manager.get_counts()
        total = self.agent_manager.get_total_count()

        self.metrics["history"].append({
            "step": self.step,
            "agent_counts": counts,
            "total_agents": total,
            "environment": copy.deepcopy(self.environment.properties)
        })

    def run(self, steps: int) -> Dict[str, Any]:
        """
        Run simulation for specified number of steps

        Args:
            steps: Number of steps to run

        Returns:
            Results dictionary with metrics and logs
        """
        start_time = time.time()

        for _ in range(steps):
            self.run_step()

            # Stop if all agents dead
            if self.agent_manager.get_total_count() == 0:
                break

        end_time = time.time()

        # Compile results
        results = {
            "spec": self.spec,
            "final_step": self.step,
            "duration": end_time - start_time,
            "metrics": self.metrics,
            "summary": {
                "initial_agents": self.metrics["initial_agents"],
                "initial_counts": self.metrics["initial_counts"],
                "final_agents": self.agent_manager.get_total_count(),
                "final_counts": self.agent_manager.get_counts()
            },
            "events": self.logger.export_json(),
            "event_summary": self.logger.get_summary()
        }

        return results

    def run_stream(self, steps: int, delay: float = 0.1,
                  callback: Optional[Callable] = None):
        """
        Run simulation with streaming updates

        Args:
            steps: Number of steps to run
            delay: Delay between steps in seconds
            callback: Optional callback function called each step

        Yields:
            State dictionary for each step
        """
        for _ in range(steps):
            self.run_step()

            state = {
                "step": self.step,
                "agent_counts": self.agent_manager.get_counts(),
                "total_agents": self.agent_manager.get_total_count(),
                "environment": self.environment.properties
            }

            if callback:
                callback(state)

            yield state

            # Stop if all agents dead
            if self.agent_manager.get_total_count() == 0:
                break

            if delay > 0:
                time.sleep(delay)

    def get_state(self) -> Dict[str, Any]:
        """Get current simulation state"""
        return {
            "step": self.step,
            "environment": self.environment.to_dict(),
            "agents": self.agent_manager.to_dict(),
            "metrics": self.metrics
        }

    def export_events(self, format: str = "json") -> Any:
        """
        Export simulation events

        Args:
            format: "json" or "csv"

        Returns:
            Events in requested format
        """
        if format == "json":
            return self.logger.export_json()
        elif format == "csv":
            return self.logger.export_csv_data()
        else:
            raise ValueError(f"Unknown format: {format}")
