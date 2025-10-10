"""
Example: Balanced Predator-Prey Model

This example demonstrates a properly balanced predator-prey simulation where
populations can sustain themselves over time.

Key balance improvements:
1. Rabbits gain energy from grazing (eating grass)
2. Wolves get fixed energy per kill (not full rabbit energy)
3. Lower predation success rate (50% vs 80%)
4. Faster rabbit reproduction
5. Lower energy decay rate
"""

import llm_abm as abm

def main():
    # Balanced configuration
    config = {
        "grid": {"width": 50, "height": 50},
        "agents": {
            "rabbit": {"count": 100, "energy": 30},  # Start with more energy
            "wolf": {"count": 15, "energy": 50}  # Fewer wolves
        }
    }

    print("Creating BALANCED predator-prey model...")
    model = abm.create_model(config)
    print(f"Created model with {model['metrics']['total_agents']} agents")
    print(f"  - {model['metrics']['agent_counts']['rabbit']} rabbits")
    print(f"  - {model['metrics']['agent_counts']['wolf']} wolves")

    # Add balanced rules
    print("\nAdding behavioral rules...")

    # Movement - same as before
    model = abm.add_rule(model, "random_movement", {})
    print("  ✓ Random movement")

    # Grazing - NEW! Rabbits gain energy from eating grass
    model = abm.add_rule(model, "grazing", {
        "species": "rabbit",
        "energy_gain": 2,  # Gain 2 energy per step (70% chance)
        "probability": 0.7
    })
    print("  ✓ Grazing (rabbits gain energy)")

    # Predation - BALANCED! Wolves get fixed energy, lower success rate
    model = abm.add_rule(model, "predator_prey", {
        "predator": "wolf",
        "prey": "rabbit",
        "success_rate": 0.5,  # 50% chance (was 80%)
        "energy_gain": 10  # Fixed 10 energy (not full rabbit energy)
    })
    print("  ✓ Predator-prey (balanced)")

    # Reproduction - FASTER for rabbits
    model = abm.add_rule(model, "reproduction", {
        "species": "rabbit",
        "energy_threshold": 35,  # Lower threshold
        "rate": 0.15  # 15% chance (was 10%)
    })
    print("  ✓ Rabbit reproduction (faster)")

    # Reproduction for wolves - slower
    model = abm.add_rule(model, "reproduction", {
        "species": "wolf",
        "energy_threshold": 60,
        "rate": 0.05  # 5% chance
    })
    print("  ✓ Wolf reproduction (slower)")

    # Energy decay - REDUCED
    model = abm.add_rule(model, "energy_decay", {
        "species": "all",
        "rate": 0.5  # Half energy decay (was 1)
    })
    print("  ✓ Energy decay (reduced)")

    # Death - same as before
    model = abm.add_rule(model, "death", {})
    print("  ✓ Death when energy = 0")

    print(f"\nTotal rules: {len(model['rules'])}")

    # Run simulation for longer
    print("\n" + "="*60)
    print("Running BALANCED simulation for 200 steps...")
    print("="*60)
    results = abm.run(model, steps=200)

    # Display results
    print("\nSimulation completed!")
    print(f"Steps completed: {results['final_step']}")
    print(f"\nPopulation changes:")
    print(f"  Initial agents: {results['summary']['initial_agents']}")
    print(f"  Final agents: {results['summary']['final_agents']}")
    print(f"  Survival rate: {results['summary']['final_agents']/results['summary']['initial_agents']*100:.1f}%")
    print(f"\nFinal counts:")
    for agent_type, count in results['summary']['final_counts'].items():
        initial = config['agents'][agent_type]['count']
        print(f"  {agent_type}: {count} (started with {initial})")

    # Show population over time
    print("\nPopulation history (every 20 steps):")
    history = results['metrics']['history']
    print("Step | Rabbits | Wolves | Total")
    print("-" * 40)
    for i in range(0, len(history), 20):
        step_data = history[i]
        rabbits = step_data['agent_counts'].get('rabbit', 0)
        wolves = step_data['agent_counts'].get('wolf', 0)
        total = step_data['total_agents']
        print(f"{step_data['step']:4d} | {rabbits:7d} | {wolves:6d} | {total:5d}")

    # Export results
    print("\n" + "="*60)
    print("Exporting results...")
    print("="*60)

    # Save CSV for analysis
    csv_data = abm.export(results, format="csv")
    try:
        with open("balanced_simulation_results.csv", 'w') as f:
            f.write(csv_data)
        print("✓ CSV saved to: balanced_simulation_results.csv")
    except Exception as e:
        print(f"✗ Could not save CSV: {e}")

    # Save JSON
    json_data = abm.export(results, format="json")
    try:
        with open("balanced_simulation_results.json", 'w') as f:
            f.write(json_data)
        print("✓ JSON saved to: balanced_simulation_results.json")
    except Exception as e:
        print(f"✗ Could not save JSON: {e}")

    # Display summary
    summary = abm.export(results, format="summary")
    print("\n" + summary)

    print("\n" + "="*60)
    print("SUCCESS! Balanced simulation completed.")
    print("="*60)
    print("\nKey improvements over original:")
    print("  ✓ Rabbits can gain energy (grazing)")
    print("  ✓ Balanced predation (lower success, fixed energy)")
    print("  ✓ Faster rabbit reproduction")
    print("  ✓ Reduced energy decay")
    print("  ✓ Populations can sustain themselves!")

if __name__ == "__main__":
    main()
