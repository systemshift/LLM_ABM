"""
LLM-ABM v2.0 Public API

Simple, powerful API for general-purpose agent-based modeling where LLMs
can generate complete simulations.
"""

from typing import Dict, Any, List, Tuple, Optional, Callable
from .core.simulation import Simulation


def create_simulation(specification: Dict[str, Any]) -> Simulation:
    """
    Create a simulation from a complete specification

    Args:
        specification: Complete simulation specification including:
            - metadata: Name, description
            - environment: Type, dimensions, properties
            - agent_types: Agent definitions with behaviors
            - global_functions: Optional global rules

    Returns:
        Simulation object ready to run

    Example:
        ```python
        spec = {
            "environment": {
                "type": "grid_2d",
                "dimensions": {"width": 50, "height": 50}
            },
            "agent_types": {
                "rabbit": {
                    "initial_count": 80,
                    "initial_state": {"energy": 25},
                    "behavior_code": "def rabbit_behavior(agent, model, nearby):\\n    ..."
                }
            }
        }
        sim = create_simulation(spec)
        ```
    """
    return Simulation(specification)


def run(simulation: Simulation, steps: int, log_level: str = "normal") -> Dict[str, Any]:
    """
    Run a simulation for specified number of steps

    Args:
        simulation: Simulation object
        steps: Number of steps to execute
        log_level: "minimal", "normal", or "detailed"

    Returns:
        Results dictionary containing:
            - metrics: Population counts over time
            - summary: Initial/final statistics
            - events: Full event log
            - event_summary: Event statistics

    Example:
        ```python
        results = run(sim, steps=200)
        print(results['summary']['final_counts'])
        ```
    """
    if hasattr(simulation, 'logger'):
        simulation.logger.log_level = log_level

    return simulation.run(steps)


def run_stream(simulation: Simulation, steps: int, delay: float = 0.1,
               callback: Optional[Callable] = None):
    """
    Run simulation with real-time streaming updates

    Args:
        simulation: Simulation object
        steps: Number of steps to execute
        delay: Delay between steps in seconds (0 for fastest)
        callback: Optional function called each step with state

    Yields:
        State dictionary for each step containing:
            - step: Current step number
            - agent_counts: Population by type
            - total_agents: Total population
            - environment: Environment properties

    Example:
        ```python
        for state in run_stream(sim, steps=100, delay=0.05):
            print(f"Step {state['step']}: {state['agent_counts']}")
        ```
    """
    yield from simulation.run_stream(steps, delay, callback)


def export(results: Dict[str, Any], filename: str, format: str = "json") -> str:
    """
    Export simulation results to file

    Args:
        results: Results dictionary from run()
        filename: Output file path
        format: "json" or "csv"

    Returns:
        Path to saved file

    Example:
        ```python
        results = run(sim, steps=200)
        export(results, "simulation_results.json", format="json")
        export(results, "simulation_events.csv", format="csv")
        ```
    """
    import json

    if format == "json":
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    elif format == "csv":
        import csv

        # Export events as CSV
        events = results.get("events", [])
        if not events:
            return filename

        with open(filename, 'w', newline='') as f:
            # Get all possible fields
            fieldnames = set()
            for event in events:
                fieldnames.update(event.keys())

            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()

            for event in events:
                # Convert complex types to strings
                row = {}
                for key, value in event.items():
                    if isinstance(value, (list, dict)):
                        row[key] = str(value)
                    else:
                        row[key] = value
                writer.writerow(row)

    else:
        raise ValueError(f"Unknown format: {format}")

    return filename


def validate_specification(specification: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a simulation specification

    Args:
        specification: Simulation specification to validate

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        ```python
        is_valid, errors = validate_specification(spec)
        if not is_valid:
            print("Errors:", errors)
        ```
    """
    errors = []

    # Check required fields
    if "environment" not in specification:
        errors.append("Missing 'environment' in specification")
    else:
        env = specification["environment"]
        if "type" not in env:
            errors.append("Missing 'type' in environment specification")
        if "dimensions" not in env:
            errors.append("Missing 'dimensions' in environment specification")

    if "agent_types" not in specification:
        errors.append("Missing 'agent_types' in specification")
    else:
        agent_types = specification["agent_types"]
        if not agent_types:
            errors.append("At least one agent type must be defined")

        for agent_type, type_spec in agent_types.items():
            if "initial_count" not in type_spec:
                errors.append(f"Missing 'initial_count' for agent type '{agent_type}'")
            if "initial_state" not in type_spec:
                errors.append(f"Missing 'initial_state' for agent type '{agent_type}'")

    is_valid = len(errors) == 0
    return is_valid, errors


def get_state(simulation: Simulation) -> Dict[str, Any]:
    """
    Get current state of a simulation

    Args:
        simulation: Simulation object

    Returns:
        Current state dictionary

    Example:
        ```python
        state = get_state(sim)
        print(f"Current step: {state['step']}")
        ```
    """
    return simulation.get_state()


# Convenience function for quick simulations
def quick_simulation(environment_type: str = "grid_2d",
                     dimensions: Dict[str, int] = None,
                     agent_types: Dict[str, Any] = None,
                     steps: int = 100) -> Dict[str, Any]:
    """
    Create and run a simple simulation quickly

    Args:
        environment_type: "grid_2d", "continuous_2d", or "network"
        dimensions: Environment dimensions
        agent_types: Agent type definitions
        steps: Number of steps to run

    Returns:
        Simulation results

    Example:
        ```python
        results = quick_simulation(
            environment_type="grid_2d",
            dimensions={"width": 30, "height": 30},
            agent_types={
                "rabbit": {
                    "initial_count": 50,
                    "initial_state": {"energy": 20}
                }
            },
            steps=100
        )
        ```
    """
    if dimensions is None:
        dimensions = {"width": 50, "height": 50}

    if agent_types is None:
        agent_types = {
            "agent": {
                "initial_count": 10,
                "initial_state": {"energy": 100}
            }
        }

    spec = {
        "environment": {
            "type": environment_type,
            "dimensions": dimensions
        },
        "agent_types": agent_types
    }

    sim = create_simulation(spec)
    return run(sim, steps)
