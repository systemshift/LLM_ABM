"""
Example: Predator-Prey with v2.0 API

Demonstrates the new general-purpose framework where LLMs can generate
complete agent behaviors, not just combine pre-defined rules.
"""

import llm_abm

# Define complete agent behaviors as code
rabbit_behavior = """
def rabbit_behavior(agent, model, agents_nearby):
    '''Rabbit behavior: eat, flee from wolves, reproduce'''
    actions = []

    # Get current state
    energy = agent.get_attribute('energy', 20)
    position = agent.get_attribute('position')

    # Energy management
    if energy < 15:
        # Hungry - try to eat (gain energy from environment)
        actions.append({
            'type': 'modify_state',
            'attribute': 'energy',
            'delta': 2  # Graze for energy
        })

    # Check for predators nearby
    wolves = [a for a in agents_nearby if a.type == 'wolf' and a.alive]
    if wolves:
        # Flee from nearest wolf
        nearest_wolf = wolves[0]
        wolf_pos = nearest_wolf.get_attribute('position')

        # Move away
        if position and wolf_pos:
            dx = 1 if position[0] < wolf_pos[0] else -1
            dy = 1 if position[1] < wolf_pos[1] else -1
            actions.append({
                'type': 'move',
                'direction': [dx, dy]
            })
    else:
        # No threat - move randomly (random is available globally)
        actions.append({
            'type': 'move',
            'direction': [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        })

    # Reproduction (random is available globally)
    if energy > 30 and random.random() < 0.08:
        actions.append({
            'type': 'reproduce',
            'energy_cost': 15,
            'offspring_count': 1
        })

    # Energy decay
    actions.append({
        'type': 'modify_state',
        'attribute': 'energy',
        'delta': -0.8
    })

    # Die if no energy
    if energy <= 0:
        actions.append({'type': 'die', 'cause': 'starvation'})

    return actions
"""

wolf_behavior = """
def wolf_behavior(agent, model, agents_nearby):
    '''Wolf behavior: hunt rabbits, move toward prey'''
    actions = []

    # Get current state
    energy = agent.get_attribute('energy', 40)
    position = agent.get_attribute('position')

    # Look for rabbits
    rabbits = [a for a in agents_nearby if a.type == 'rabbit' and a.alive]

    if rabbits:
        # Hunt nearest rabbit
        nearest_rabbit = rabbits[0]
        rabbit_pos = nearest_rabbit.get_attribute('position')

        # Check if at same position (can attack)
        if position == rabbit_pos:
            # Attempt predation
            actions.append({
                'type': 'interact',
                'target_id': nearest_rabbit.id,
                'interaction_type': 'predation',
                'params': {
                    'success_rate': 0.4,
                    'energy_gain': 10
                }
            })
        else:
            # Move toward rabbit
            actions.append({
                'type': 'move_to',
                'target': rabbit_pos
            })
    else:
        # No prey - move randomly to search (random is available globally)
        actions.append({
            'type': 'move',
            'direction': [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        })

    # Reproduction (harder for wolves)
    if energy > 50 and random.random() < 0.04:
        actions.append({
            'type': 'reproduce',
            'energy_cost': 20,
            'offspring_count': 1
        })

    # Energy decay
    actions.append({
        'type': 'modify_state',
        'attribute': 'energy',
        'delta': -0.8
    })

    # Die if no energy
    if energy <= 0:
        actions.append({'type': 'die', 'cause': 'starvation'})

    return actions
"""

def main():
    print("=" * 60)
    print("LLM-ABM v2.0 Example: General-Purpose Predator-Prey")
    print("=" * 60)

    # Create complete simulation specification
    spec = {
        "metadata": {
            "name": "Predator-Prey Ecosystem",
            "description": "Wolves hunt rabbits with emergent population dynamics"
        },
        "environment": {
            "type": "grid_2d",
            "dimensions": {
                "width": 30,
                "height": 30,
                "topology": "torus"
            },
            "properties": {
                "food_availability": 1.0
            }
        },
        "agent_types": {
            "rabbit": {
                "initial_count": 80,
                "initial_state": {
                    "energy": 25,
                    "age": 0,
                    "perception_radius": 5
                },
                "behavior_code": rabbit_behavior
            },
            "wolf": {
                "initial_count": 15,
                "initial_state": {
                    "energy": 40,
                    "age": 0,
                    "perception_radius": 7
                },
                "behavior_code": wolf_behavior
            }
        },
        "log_level": "normal"
    }

    print("\n1. VALIDATING SPECIFICATION")
    print("-" * 40)
    is_valid, errors = llm_abm.validate_specification(spec)
    if is_valid:
        print("✓ Specification is valid")
    else:
        print("✗ Specification has errors:")
        for error in errors:
            print(f"  - {error}")
        return

    print("\n2. CREATING SIMULATION")
    print("-" * 40)
    sim = llm_abm.create_simulation(spec)
    print(f"✓ Created simulation with {sim.agent_manager.get_total_count()} agents")
    print(f"  Environment: {sim.environment.width}x{sim.environment.height} grid")
    print(f"  Agent types: {list(spec['agent_types'].keys())}")

    print("\n3. RUNNING SIMULATION")
    print("-" * 40)
    print("Running 200 steps...")

    results = llm_abm.run_v2(sim, steps=200, log_level="normal")

    print(f"\n✓ Simulation complete!")
    print(f"  Steps completed: {results['final_step']}")
    print(f"  Duration: {results['duration']:.2f} seconds")
    print(f"  Initial agents: {results['summary']['initial_agents']}")
    print(f"  Final agents: {results['summary']['final_agents']}")

    print("\n4. POPULATION DYNAMICS")
    print("-" * 40)
    print("Final counts:")
    for agent_type, count in results['summary']['final_counts'].items():
        print(f"  {agent_type}: {count}")

    # Show population history
    print("\nPopulation over time:")
    print("Step | Rabbits | Wolves")
    print("-" * 30)
    history = results['metrics']['history']
    for i in [0, 50, 100, 150, len(history)-1]:
        if i < len(history):
            step_data = history[i]
            rabbits = step_data['agent_counts'].get('rabbit', 0)
            wolves = step_data['agent_counts'].get('wolf', 0)
            print(f"{step_data['step']:4d} | {rabbits:7d} | {wolves:6d}")

    print("\n5. EVENT ANALYSIS")
    print("-" * 40)
    event_summary = results['event_summary']
    print(f"Total events logged: {event_summary['total_events']}")
    print("Events by type:")
    for event_type, count in event_summary['event_types'].items():
        print(f"  {event_type}: {count}")

    # Analyze specific events
    events = results['events']
    deaths = [e for e in events if e['type'] == 'agent_death']
    predation_deaths = [d for d in deaths if d.get('cause') == 'predation']
    starvation_deaths = [d for d in deaths if d.get('cause') == 'starvation']

    print(f"\nDeath analysis:")
    print(f"  Total deaths: {len(deaths)}")
    print(f"  By predation: {len(predation_deaths)}")
    print(f"  By starvation: {len(starvation_deaths)}")

    births = [e for e in events if e['type'] == 'agent_birth']
    print(f"  Total births: {len(births)}")

    print("\n6. EXPORTING RESULTS")
    print("-" * 40)

    # Export full results
    llm_abm.export_v2(results, "v2_simulation_results.json", format="json")
    print("✓ Exported full results to: v2_simulation_results.json")

    # Export events as CSV
    llm_abm.export_v2(results, "v2_simulation_events.csv", format="csv")
    print("✓ Exported events to: v2_simulation_events.csv")

    print("\n" + "=" * 60)
    print("v2.0 DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey v2.0 Features Demonstrated:")
    print("✓ Complete agent behavior generation (not pre-defined rules)")
    print("✓ Flexible agent attributes (energy, age, perception_radius)")
    print("✓ Comprehensive event logging (every action tracked)")
    print("✓ Rich simulation analysis (death causes, births, interactions)")
    print("✓ General-purpose framework (LLM can design anything)")
    print("=" * 60)

if __name__ == "__main__":
    main()
