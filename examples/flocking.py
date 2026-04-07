"""
Flocking (Boids) Model

Birds follow three simple rules:
1. Separation — avoid crowding nearby birds
2. Alignment — steer toward average heading of neighbors
3. Cohesion — steer toward average position of neighbors

These three rules produce realistic emergent flocking behavior.
Uses continuous-like movement on a grid.
"""

from agentstan import Simulation, DataCollector

behavior_code = """
def bird_behavior(agent, model, agents_nearby):
    actions = []
    position = agent['position']

    if not agents_nearby:
        # No neighbors: move randomly
        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})
        return actions

    # Compute neighbor statistics
    flock = [a for a in agents_nearby if a.alive]
    if not flock:
        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})
        return actions

    # Average position of neighbors (cohesion target)
    avg_x = sum(a['position'][0] for a in flock) / len(flock)
    avg_y = sum(a['position'][1] for a in flock) / len(flock)

    # Separation: avoid nearest bird
    nearest = min(flock, key=lambda a: abs(a['position'][0] - position[0]) + abs(a['position'][1] - position[1]))
    nearest_pos = nearest['position']
    dist_to_nearest = abs(nearest_pos[0] - position[0]) + abs(nearest_pos[1] - position[1])

    dx, dy = 0, 0

    if dist_to_nearest <= 1:
        # Too close: separate (move away from nearest)
        dx = 1 if position[0] > nearest_pos[0] else (-1 if position[0] < nearest_pos[0] else 0)
        dy = 1 if position[1] > nearest_pos[1] else (-1 if position[1] < nearest_pos[1] else 0)
    else:
        # Cohesion: move toward flock center
        dx = 1 if avg_x > position[0] else (-1 if avg_x < position[0] else 0)
        dy = 1 if avg_y > position[1] else (-1 if avg_y < position[1] else 0)

    # Add some randomness (alignment noise)
    if random.random() < 0.2:
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])

    actions.append({'type': 'move', 'direction': [dx, dy]})
    return actions
"""

spec = {
    "environment": {
        "type": "grid_2d",
        "dimensions": {"width": 40, "height": 40, "topology": "torus"},
    },
    "agent_types": {
        "bird": {
            "initial_count": 50,
            "initial_state": {"perception_radius": 5},
            "behavior_code": behavior_code,
        },
    },
}


def compute_avg_cluster_size(sim):
    """Average number of neighbors per bird (proxy for flocking)."""
    total_neighbors = 0
    n = 0
    for agent in sim.agent_manager.get_living_agents():
        nearby = sim.agent_manager.get_agents_near_agent(
            agent, agent.get_attribute("perception_radius", 5), sim.environment
        )
        total_neighbors += len(nearby)
        n += 1
    return total_neighbors / n if n > 0 else 0


def run_single():
    print("=== Flocking (Boids) Model ===")
    print("50 birds on a 40x40 torus grid")
    print("Rules: separation, cohesion, random noise")
    print()

    sim = Simulation(spec)
    collector = DataCollector(
        model_metrics={"avg_neighbors": compute_avg_cluster_size},
    )
    sim.add_collector(collector)
    results = sim.run(100)

    data = collector.get_model_data()

    print(f"Steps: {results['final_step']}")
    print(f"Initial avg neighbors: {data[0]['avg_neighbors']:.1f}")
    print(f"Final avg neighbors:   {data[-1]['avg_neighbors']:.1f}")
    print()

    print("Flocking density over time:")
    for i in range(0, len(data), 10):
        bar = "#" * int(data[i]["avg_neighbors"] * 3)
        print(f"  Step {data[i]['step']:3d}: {data[i]['avg_neighbors']:.1f} neighbors {bar}")


if __name__ == "__main__":
    run_single()
