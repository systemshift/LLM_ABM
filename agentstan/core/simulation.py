"""
Core simulation engine.
"""

import copy
import time
from typing import Dict, Any, List, Optional, Callable

from .environment import Environment
from .agent import Agent, AgentManager
from .actions import ActionProcessor
from .logger import EventLogger
from .scheduler import RandomScheduler


class Simulation:
    """
    Core simulation engine that manages environment, agents, and execution.

    Args:
        specification: Simulation spec dict with environment and agent_types.
        scheduler: Agent activation scheduler (default: RandomScheduler).
    """

    def __init__(self, specification: Dict[str, Any], scheduler=None):
        self.spec = specification
        self.step = 0
        self.scheduler = scheduler or RandomScheduler()
        self.collectors = []

        # Initialize core systems
        self.environment = self._create_environment()
        self.agent_manager = AgentManager()
        self.logger = EventLogger(
            enabled=True,
            log_level=specification.get("log_level", "normal"),
        )
        self.action_processor = ActionProcessor(
            self.agent_manager, self.environment, self.logger
        )

        self._create_agents()

        # Optional systems (attached after init)
        self.intervention_engine = None
        self.llm_engine = None

        self.metrics = {
            "initial_agents": self.agent_manager.get_total_count(),
            "initial_counts": self.agent_manager.get_counts(),
            "history": [],
        }

    def add_collector(self, collector) -> None:
        """Attach a DataCollector to this simulation."""
        self.collectors.append(collector)

    def add_observer(self, observer) -> None:
        """Attach an Observer (also registers as collector)."""
        self.collectors.append(observer)

    def attach_intervention_engine(self, engine) -> None:
        """Attach an InterventionEngine for mid-simulation modifications."""
        self.intervention_engine = engine

    def attach_llm_engine(self, engine) -> None:
        """Attach an LLMBehaviorEngine for LLM-powered agents."""
        self.llm_engine = engine

    def _create_environment(self) -> Environment:
        env_spec = self.spec.get("environment", {})
        return Environment.from_dict(env_spec)

    def _create_agents(self):
        agent_types = self.spec.get("agent_types", {})

        for agent_type, type_spec in agent_types.items():
            initial_count = type_spec.get("initial_count", 0)
            initial_state = type_spec.get("initial_state", {})
            behavior_code = type_spec.get("behavior_code", "")

            behavior_func = None
            if behavior_code:
                behavior_func = self._compile_behavior_function(
                    agent_type, behavior_code
                )

            for _ in range(initial_count):
                agent = Agent(
                    agent_type=agent_type,
                    initial_state=copy.deepcopy(initial_state),
                    behavior_function=behavior_func,
                )
                if agent.state.get("position") is None:
                    agent.state["position"] = self.environment.get_random_position()
                self.agent_manager.add_agent(agent)

    def _compile_behavior_function(
        self, agent_type: str, behavior_code: str
    ) -> Optional[Callable]:
        try:
            import random
            import math

            namespace = {
                "__builtins__": {
                    "abs": abs, "len": len, "max": max, "min": min,
                    "sum": sum, "range": range, "enumerate": enumerate,
                    "list": list, "dict": dict, "str": str, "int": int,
                    "float": float, "bool": bool, "any": any, "all": all,
                    "sorted": sorted, "reversed": reversed, "round": round,
                    "zip": zip, "map": map, "filter": filter, "tuple": tuple,
                    "set": set, "True": True, "False": False, "None": None,
                    "isinstance": isinstance, "print": print,
                },
                "random": random,
                "math": math,
            }

            exec(behavior_code, namespace)

            func_name = f"{agent_type}_behavior"
            if func_name in namespace:
                return namespace[func_name]

            for name, obj in namespace.items():
                if callable(obj) and not name.startswith("_") and name not in ("random", "math"):
                    return obj

            return None

        except Exception as e:
            raise ValueError(f"Error compiling behavior for {agent_type}: {e}")

    def run_step(self):
        """Execute one simulation step."""
        self.step += 1
        self.environment.update(self.step)

        # Apply queued interventions from previous cycle
        if self.intervention_engine:
            self.intervention_engine.apply_pending()

        # Pre-compute LLM agent decisions in batch
        if self.llm_engine:
            self.llm_engine.prepare_batch(self)

        agents = self.scheduler.get_agents(self.agent_manager)
        simultaneous = getattr(self.scheduler, "simultaneous", False)

        if simultaneous:
            # Collect all actions first, then process
            all_actions = []
            for agent in agents:
                if not agent.alive:
                    continue
                actions = self._get_agent_actions(agent)
                if actions:
                    all_actions.append((agent, actions))
            for agent, actions in all_actions:
                if agent.alive:
                    self.action_processor.process_actions(agent, actions, self.step)
        else:
            for agent in agents:
                if not agent.alive:
                    continue
                actions = self._get_agent_actions(agent)
                if actions:
                    self.action_processor.process_actions(agent, actions, self.step)

        self._apply_global_functions()
        self.agent_manager.cleanup_dead_agents()
        self._record_metrics()

        # Run collectors
        for collector in self.collectors:
            collector.collect(self)

    def _get_agent_actions(self, agent: Agent) -> List[Dict[str, Any]]:
        perception_radius = agent.get_attribute("perception_radius", 5)
        agents_nearby = self.agent_manager.get_agents_near_agent(
            agent, perception_radius, self.environment
        )
        sim_state = {
            "step": self.step,
            "environment": self.environment.to_dict(),
            "agent_counts": self.agent_manager.get_counts(),
        }
        return agent.execute_behavior(sim_state, agents_nearby)

    def _apply_global_functions(self):
        for agent in self.agent_manager.get_living_agents():
            energy = agent.get_attribute("energy", None)
            if energy is not None and energy <= 0:
                agent.kill()
                self.logger.log_agent_death(
                    step=self.step,
                    agent_id=agent.id,
                    agent_type=agent.type,
                    cause="energy_depleted",
                )

    def _record_metrics(self):
        counts = self.agent_manager.get_counts()
        total = self.agent_manager.get_total_count()
        self.metrics["history"].append({
            "step": self.step,
            "agent_counts": counts,
            "total_agents": total,
        })

    def run(self, steps: int) -> Dict[str, Any]:
        """Run simulation for N steps. Returns results dict."""
        start_time = time.time()

        for _ in range(steps):
            self.run_step()
            if self.agent_manager.get_total_count() == 0:
                break

        return {
            "spec": self.spec,
            "final_step": self.step,
            "duration": time.time() - start_time,
            "metrics": self.metrics,
            "summary": {
                "initial_agents": self.metrics["initial_agents"],
                "initial_counts": self.metrics["initial_counts"],
                "final_agents": self.agent_manager.get_total_count(),
                "final_counts": self.agent_manager.get_counts(),
            },
            "events": self.logger.export_json(),
            "event_summary": self.logger.get_summary(),
        }

    def run_stream(self, steps: int, delay: float = 0.1, callback: Optional[Callable] = None):
        """Run simulation yielding state each step."""
        for _ in range(steps):
            self.run_step()

            state = {
                "step": self.step,
                "agent_counts": self.agent_manager.get_counts(),
                "total_agents": self.agent_manager.get_total_count(),
                "environment": self.environment.properties,
            }

            if callback:
                callback(state)
            yield state

            if self.agent_manager.get_total_count() == 0:
                break
            if delay > 0:
                time.sleep(delay)

    def get_state(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "environment": self.environment.to_dict(),
            "agents": self.agent_manager.to_dict(),
            "metrics": self.metrics,
        }
