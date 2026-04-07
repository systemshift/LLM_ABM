"""
Predator-Prey (Lotka-Volterra) Model

Wolves hunt rabbits. Rabbits graze for energy. Both reproduce when
energy is high. Classic oscillating population dynamics emerge:
rabbits boom → wolves boom → rabbits crash → wolves crash → repeat.

Try varying wolf count, predation success rate, or energy decay
to find stable vs unstable parameter regions.
"""

from agentstan import Simulation, DataCollector
from agentstan.analysis import analyze_population
from agentstan.experiment import sweep

rabbit_code = """
def rabbit_behavior(agent, model, agents_nearby):
    actions = []
    energy = agent['energy']
    position = agent['position']

    # Graze for energy
    if energy < 20:
        actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': 2.0})

    # Flee from wolves
    wolves = [a for a in agents_nearby if a.type == 'wolf' and a.alive]
    if wolves:
        w = wolves[0]['position']
        dx = 1 if position[0] > w[0] else -1
        dy = 1 if position[1] > w[1] else -1
        actions.append({'type': 'move', 'direction': [dx, dy]})
    else:
        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})

    # Reproduce
    if energy > 30 and random.random() < 0.08:
        actions.append({'type': 'reproduce', 'energy_cost': 14, 'offspring_count': 1})

    # Metabolism
    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -0.8})

    if energy <= 0:
        actions.append({'type': 'die', 'cause': 'starvation'})

    return actions
"""

wolf_code = """
def wolf_behavior(agent, model, agents_nearby):
    actions = []
    energy = agent['energy']
    position = agent['position']

    # Hunt rabbits
    rabbits = [a for a in agents_nearby if a.type == 'rabbit' and a.alive]
    if rabbits:
        prey = rabbits[0]
        prey_pos = prey['position']
        if position == prey_pos:
            actions.append({
                'type': 'interact', 'target_id': prey.id,
                'interaction_type': 'predation',
                'params': {'success_rate': 0.4, 'energy_gain': 12}
            })
        else:
            actions.append({'type': 'move_to', 'target': (prey_pos[0], prey_pos[1])})
    else:
        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})

    # Reproduce
    if energy > 50 and random.random() < 0.04:
        actions.append({'type': 'reproduce', 'energy_cost': 20, 'offspring_count': 1})

    # Metabolism
    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -1.0})

    if energy <= 0:
        actions.append({'type': 'die', 'cause': 'starvation'})

    return actions
"""

spec = {
    "environment": {
        "type": "grid_2d",
        "dimensions": {"width": 40, "height": 40, "topology": "torus"},
    },
    "agent_types": {
        "rabbit": {
            "initial_count": 80,
            "initial_state": {"energy": 25, "perception_radius": 5},
            "behavior_code": rabbit_code,
        },
        "wolf": {
            "initial_count": 15,
            "initial_state": {"energy": 40, "perception_radius": 7},
            "behavior_code": wolf_code,
        },
    },
}


def run_single():
    print("=== Predator-Prey Model ===")
    print("80 rabbits, 15 wolves, 40x40 grid")
    print()

    sim = Simulation(spec)
    collector = DataCollector()
    sim.add_collector(collector)
    results = sim.run(200)

    # Population analysis
    report = analyze_population(results)
    summary = results["summary"]

    print(f"Steps: {results['final_step']}")
    print(f"Initial: rabbit={summary['initial_counts'].get('rabbit', 0)}, wolf={summary['initial_counts'].get('wolf', 0)}")
    print(f"Final:   rabbit={summary['final_counts'].get('rabbit', 0)}, wolf={summary['final_counts'].get('wolf', 0)}")
    print()

    for agent_type in ["rabbit", "wolf"]:
        info = report["agent_types"].get(agent_type, {})
        print(f"  {agent_type}:")
        print(f"    stability: {info.get('stability', '?')}")
        print(f"    peak: {info.get('peak', '?')} (step {info.get('peak_step', '?')})")
        if info.get("extinct"):
            print(f"    EXTINCT at step {info.get('extinction_step')}")
        if info.get("period"):
            print(f"    oscillation period: ~{info['period']} steps")
        print()

    # Print population timeline
    data = collector.get_model_data()
    print("Population over time:")
    for i in range(0, len(data), 20):
        row = data[i]
        r = row.get("count_rabbit", 0)
        w = row.get("count_wolf", 0)
        r_bar = "R" * min(r // 2, 40)
        w_bar = "W" * min(w, 20)
        print(f"  Step {row['step']:3d}: {r_bar} ({r}) | {w_bar} ({w})")


def run_wolf_sweep():
    print("\n=== Wolf Count Sweep ===")
    print("How many wolves are sustainable?\n")

    results = sweep(
        spec,
        param="agent_types.wolf.initial_count",
        values=[5, 10, 15, 20, 30],
        steps=200,
        n_runs=5,
        max_workers=4,
    )

    for val in sorted(results.keys()):
        runs = results[val]
        avg_rabbits = sum(r["summary"]["final_counts"].get("rabbit", 0) for r in runs) / len(runs)
        avg_wolves = sum(r["summary"]["final_counts"].get("wolf", 0) for r in runs) / len(runs)
        extinct = sum(1 for r in runs if r["summary"]["final_counts"].get("wolf", 0) == 0)
        print(f"  wolves={val:2d}: avg final rabbit={avg_rabbits:5.1f}, wolf={avg_wolves:4.1f}, wolf extinct {extinct}/{len(runs)}")


if __name__ == "__main__":
    run_single()
    run_wolf_sweep()
