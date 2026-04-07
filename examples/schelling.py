"""
Schelling Segregation Model

Two types of agents on a grid. Each checks if enough neighbors are the
same type. If not, they move to a random cell. Simple rules produce
dramatic segregation from a well-mixed initial state.

Try varying tolerance (0.1 = very tolerant, 0.8 = very intolerant)
to see how it affects segregation levels.
"""

from agentstan import Simulation, DataCollector
from agentstan.experiment import sweep

TOLERANCE = 0.3

behavior_code = """
def agent_behavior(agent, model, agents_nearby):
    if not agents_nearby:
        return []

    same = sum(1 for a in agents_nearby if a.type == agent.type)
    ratio = same / len(agents_nearby)

    if ratio < agent['tolerance']:
        return [{'type': 'move_random'}]  # unhappy, relocate
    return []  # happy, stay
"""

spec = {
    "environment": {
        "type": "grid_2d",
        "dimensions": {"width": 30, "height": 30, "topology": "torus"},
    },
    "agent_types": {
        "blue": {
            "initial_count": 200,
            "initial_state": {"tolerance": TOLERANCE, "perception_radius": 2},
            "behavior_code": behavior_code,
        },
        "red": {
            "initial_count": 200,
            "initial_state": {"tolerance": TOLERANCE, "perception_radius": 2},
            "behavior_code": behavior_code,
        },
    },
}


def measure_segregation(sim):
    """Fraction of agents who are 'happy' (enough same-type neighbors)."""
    happy = 0
    total = 0
    for agent in sim.agent_manager.get_living_agents():
        nearby = sim.agent_manager.get_agents_near_agent(
            agent, agent.get_attribute("perception_radius", 2), sim.environment
        )
        if not nearby:
            continue
        total += 1
        same = sum(1 for a in nearby if a.type == agent.type)
        if same / len(nearby) >= agent.get_attribute("tolerance", 0.3):
            happy += 1
    return happy / total if total > 0 else 0


def run_single():
    print("=== Schelling Segregation Model ===")
    print(f"Grid: 30x30, 400 agents (200 blue, 200 red)")
    print(f"Tolerance: {TOLERANCE}")
    print()

    sim = Simulation(spec)
    collector = DataCollector(
        model_metrics={"segregation": measure_segregation},
    )
    sim.add_collector(collector)

    results = sim.run(50)
    data = collector.get_model_data()

    print(f"Initial segregation: {data[0]['segregation']:.1%}")
    print(f"Final segregation:   {data[-1]['segregation']:.1%}")
    print(f"Steps: {results['final_step']}")
    print()

    # Show trend
    for i in range(0, len(data), 10):
        bar = "#" * int(data[i]["segregation"] * 40)
        print(f"  Step {data[i]['step']:3d}: {data[i]['segregation']:.1%} {bar}")


def run_tolerance_sweep():
    print("\n=== Tolerance Sweep ===")
    print("How does tolerance affect segregation?\n")

    results = sweep(
        spec,
        param="agent_types.blue.initial_state.tolerance",
        values=[0.1, 0.2, 0.3, 0.5, 0.7],
        steps=50,
        n_runs=5,
        max_workers=4,
    )

    for val in sorted(results.keys()):
        runs = results[val]
        # Measure final segregation by counting surviving agents
        # (all survive in Schelling, so just report completion)
        avg_steps = sum(r["final_step"] for r in runs) / len(runs)
        print(f"  tolerance={val:.1f}: avg steps={avg_steps:.0f} ({len(runs)} runs)")


if __name__ == "__main__":
    run_single()
    run_tolerance_sweep()
