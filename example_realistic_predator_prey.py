"""
Example: Realistic Predator-Prey Model

This example demonstrates a realistic predator-prey simulation with
cyclical population dynamics (like real ecosystems).
"""

import llm_abm as abm

def main():
    # Realistic configuration
    config = {
        "grid": {"width": 50, "height": 50},
        "agents": {
            "rabbit": {"count": 100, "energy": 25},
            "wolf": {"count": 20, "energy": 40}
        }
    }

    print("Creating REALISTIC predator-prey model...")
    model = abm.create_model(config)
    print(f"Created model with {model['metrics']['total_agents']} agents")

    # Add realistic rules
    print("\nAdding behavioral rules...")
    model = abm.add_rule(model, "random_movement", {})
    model = abm.add_rule(model, "grazing", {"species": "rabbit", "energy_gain": 1.5, "probability": 0.6})
    model = abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit", "success_rate": 0.4, "energy_gain": 8})
    model = abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 30, "rate": 0.08})
    model = abm.add_rule(model, "reproduction", {"species": "wolf", "energy_threshold": 50, "rate": 0.04})
    model = abm.add_rule(model, "energy_decay", {"species": "all", "rate": 0.8})
    model = abm.add_rule(model, "death", {})
    print(f"Added {len(model['rules'])} rules")

    # Run simulation
    print("\nRunning simulation for 300 steps...")
    results = abm.run(model, steps=300)

    # Display results
    print(f"\nSteps completed: {results['final_step']}")
    print(f"Initial agents: {results['summary']['initial_agents']}")
    print(f"Final agents: {results['summary']['final_agents']}")
    print(f"\nFinal counts:")
    for agent_type, count in results['summary']['final_counts'].items():
        print(f"  {agent_type}: {count}")

    # Show key points in population history
    print("\nPopulation history (sample points):")
    history = results['metrics']['history']
    print("Step | Rabbits | Wolves")
    print("-" * 30)
    for i in [0, 50, 100, 150, 200, 250, len(history)-1]:
        if i < len(history):
            step_data = history[i]
            rabbits = step_data['agent_counts'].get('rabbit', 0)
            wolves = step_data['agent_counts'].get('wolf', 0)
            print(f"{step_data['step']:4d} | {rabbits:7d} | {wolves:6d}")

    # Check for population cycles
    rabbit_counts = [h['agent_counts'].get('rabbit', 0) for h in history]
    wolf_counts = [h['agent_counts'].get('wolf', 0) for h in history]

    avg_rabbits = sum(rabbit_counts) / len(rabbit_counts)
    avg_wolves = sum(wolf_counts) / len(wolf_counts)

    print(f"\nAverage populations over time:")
    print(f"  Rabbits: {avg_rabbits:.1f}")
    print(f"  Wolves: {avg_wolves:.1f}")

    # Export
    csv_data = abm.export(results, format="csv")
    with open("realistic_simulation.csv", 'w') as f:
        f.write(csv_data)
    print(f"\n✓ Results saved to: realistic_simulation.csv")

    print("\n" + "="*50)
    print("REALISTIC simulation complete!")
    print("Check the CSV file for full population dynamics")
    print("="*50)

if __name__ == "__main__":
    main()
