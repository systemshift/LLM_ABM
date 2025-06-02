"""
Example: Predator-Prey Model

This example demonstrates the LLM-ABM library with a classic predator-prey simulation.
Rabbits and wolves move randomly, wolves hunt rabbits, rabbits reproduce, and energy decays.
"""

import llm_abm as abm

def main():
    # Configuration matching the spec example
    config = {
        "grid": {"width": 50, "height": 50},
        "agents": {
            "rabbit": {"count": 100, "energy": 20},
            "wolf": {"count": 20, "energy": 40}
        }
    }

    # Create model
    print("Creating predator-prey model...")
    model = abm.create_model(config)
    print(f"Created model with {model['metrics']['total_agents']} agents")
    
    # Add rules
    print("Adding behavioral rules...")
    model = abm.add_rule(model, "random_movement", {})
    model = abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit"})
    model = abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 30})
    model = abm.add_rule(model, "energy_decay", {"species": "all", "rate": 1})
    model = abm.add_rule(model, "death", {})
    
    print(f"Added {len(model['rules'])} rules:")
    for rule in model['rules']:
        print(f"  - {rule['name']}: {rule['params']}")
    
    # Run simulation
    print("\nRunning simulation for 100 steps...")
    results = abm.run(model, steps=100)
    
    # Display results
    print("\nSimulation completed!")
    print(f"Steps completed: {results['final_step']}")
    print(f"Initial agents: {results['summary']['initial_agents']}")
    print(f"Final agents: {results['summary']['final_agents']}")
    print(f"Final counts: {results['summary']['final_counts']}")
    
    # Export data
    print("\nExporting results...")
    
    # Summary export
    summary = abm.export(results, format="summary")
    print(summary)
    
    # JSON export (first 500 characters)
    json_data = abm.export(results, format="json")
    print(f"\nJSON export (first 500 chars):\n{json_data[:500]}...")
    
    # CSV export (first 10 lines)
    csv_data = abm.export(results, format="csv")
    csv_lines = csv_data.split('\n')[:10]
    print(f"\nCSV export (first 10 lines):\n" + '\n'.join(csv_lines))
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()
