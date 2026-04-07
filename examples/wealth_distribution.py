"""
Boltzmann Wealth Distribution

All agents start with equal wealth. Each step, every agent gives 1 unit
to a random neighbor. Despite fair rules, extreme inequality emerges —
the distribution converges to a Boltzmann (exponential) distribution.

This is a classic demonstration that inequality can arise from purely
random processes without any structural advantage.
"""

from agentstan import Simulation, DataCollector
from agentstan.experiment import batch_run

behavior_code = """
def agent_behavior(agent, model, agents_nearby):
    actions = []

    # Give 1 unit to a random neighbor (if we have money)
    if agent['wealth'] > 0 and agents_nearby:
        target = random.choice([a for a in agents_nearby if a.alive])
        actions.append({
            'type': 'interact',
            'target_id': target.id,
            'interaction_type': 'transfer_energy',
            'params': {'amount': 1}
        })

    # Random walk
    actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})

    return actions
"""

spec = {
    "environment": {
        "type": "grid_2d",
        "dimensions": {"width": 20, "height": 20, "topology": "torus"},
    },
    "agent_types": {
        "person": {
            "initial_count": 100,
            "initial_state": {"wealth": 10, "perception_radius": 2},
            # Note: we use 'wealth' but the interact handler uses 'energy'.
            # We remap via the energy attribute since that's what transfer_energy uses.
            "behavior_code": behavior_code,
        },
    },
}

# The transfer_energy interaction uses the 'energy' attribute.
# So we need agents to have 'energy' mapped to their wealth.
# Simplest: just use 'energy' as the wealth attribute.
spec["agent_types"]["person"]["initial_state"] = {
    "energy": 10,
    "perception_radius": 2,
}

# Update behavior to use 'energy' as wealth
behavior_code_energy = """
def agent_behavior(agent, model, agents_nearby):
    actions = []

    # Give 1 unit to a random neighbor (if we have money)
    if agent['energy'] > 0 and agents_nearby:
        target = random.choice([a for a in agents_nearby if a.alive])
        actions.append({
            'type': 'interact',
            'target_id': target.id,
            'interaction_type': 'transfer_energy',
            'params': {'amount': 1}
        })

    # Random walk
    actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})

    return actions
"""
spec["agent_types"]["person"]["behavior_code"] = behavior_code_energy


def compute_gini(sim):
    """Gini coefficient: 0 = perfect equality, 1 = perfect inequality."""
    wealths = sorted(a.get_attribute("energy", 0) for a in sim.agent_manager.get_living_agents())
    n = len(wealths)
    if n == 0 or sum(wealths) == 0:
        return 0
    cumulative = 0
    total = sum(wealths)
    for i, w in enumerate(wealths):
        cumulative += (2 * (i + 1) - n - 1) * w
    return cumulative / (n * total)


def run_single():
    print("=== Boltzmann Wealth Distribution ===")
    print("100 agents, each starts with 10 units")
    print("Each step: give 1 unit to a random neighbor")
    print()

    sim = Simulation(spec)
    collector = DataCollector(
        model_metrics={"gini": compute_gini},
        agent_metrics={"energy": lambda a: a.get_attribute("energy", 0)},
    )
    sim.add_collector(collector)
    results = sim.run(200)

    data = collector.get_model_data()
    agent_data = collector.get_agent_data()

    print(f"Initial Gini: {data[0]['gini']:.3f}")
    print(f"Final Gini:   {data[-1]['gini']:.3f}")
    print()

    # Show Gini over time
    print("Gini coefficient over time:")
    for i in range(0, len(data), 25):
        bar = "#" * int(data[i]["gini"] * 50)
        print(f"  Step {data[i]['step']:3d}: {data[i]['gini']:.3f} {bar}")
    print()

    # Final wealth distribution
    final_step = max(d["step"] for d in agent_data)
    final_wealths = sorted(
        [d["energy"] for d in agent_data if d["step"] == final_step],
        reverse=True,
    )

    print("Final wealth distribution (top 10 / bottom 10):")
    print(f"  Richest 10: {final_wealths[:10]}")
    print(f"  Poorest 10: {final_wealths[-10:]}")
    print(f"  Top 10% own: {sum(final_wealths[:10]) / sum(final_wealths):.0%} of total wealth")


if __name__ == "__main__":
    run_single()
