"""
Example: Flocking Birds Simulation

This example demonstrates the new flocking behavior with bird agents
that exhibit alignment, cohesion, and separation behaviors.
"""

import llm_abm as abm

def main():
    print("Flocking Birds Simulation")
    print("=" * 40)
    
    # Configuration for flocking birds
    config = {
        "grid": {"width": 20, "height": 20, "topology": "torus"},
        "agents": {
            "bird": {"count": 30, "energy": 100}
        }
    }
    
    # Create model
    model = abm.create_model(config)
    print(f"Created model with {model['metrics']['total_agents']} birds")
    
    # Add flocking behavior
    model = abm.add_rule(model, "flocking", {
        "species": "bird",
        "radius": 4,
        "cohesion_weight": 1.0,
        "separation_weight": 2.0
    })
    
    # Add energy decay to keep birds moving
    model = abm.add_rule(model, "energy_decay", {"species": "bird", "rate": 0.5})
    
    print(f"Added {len(model['rules'])} rules")
    
    # Stream simulation to see flocking behavior
    print("\nStreaming flocking simulation...")
    
    def flocking_callback(state):
        birds = state['agent_counts'].get('bird', 0)
        print(f"  Step {state['step']:2d}: {birds:2d} birds flocking")
    
    states = []
    for state in abm.run_stream(model, steps=25, delay=0.1, callback=flocking_callback):
        states.append(state)
        if state['total_agents'] == 0:
            break
    
    print(f"\nCompleted {len(states)} steps of flocking simulation")
    
    # Show final bird positions to see clustering
    if states:
        final_state = states[-1]
        print(f"\nFinal bird positions:")
        bird_positions = {}
        
        for agent in final_state['agents']:
            if agent['alive'] and agent['type'] == 'bird':
                pos = f"({agent['position']['x']}, {agent['position']['y']})"
                bird_positions[pos] = bird_positions.get(pos, 0) + 1
        
        # Show positions with multiple birds (flocking evidence)
        flocks = {pos: count for pos, count in bird_positions.items() if count > 1}
        if flocks:
            print("Detected flocks (multiple birds at same location):")
            for pos, count in flocks.items():
                print(f"  {pos}: {count} birds")
        else:
            print("Birds spread out - showing first 5 positions:")
            for i, pos in enumerate(list(bird_positions.keys())[:5]):
                print(f"  {pos}")
    
    print("\n" + "=" * 40)
    print("✓ Flocking behavior demonstrated!")
    print("✓ New rule 'flocking' ready for use")

if __name__ == "__main__":
    main()
