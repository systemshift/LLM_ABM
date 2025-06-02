"""
Example: Streaming Simulation with Time Control

This example demonstrates the new streaming functionality with time controls.
Watch a predator-prey simulation unfold in real-time with adjustable speed.
"""

import llm_abm as abm
import time

def print_callback(state):
    """Callback function to print simulation state"""
    print(f"Step {state['step']}: {state['total_agents']} total agents - {state['agent_counts']}")

def main():
    # Configuration for a small predator-prey model
    config = {
        "grid": {"width": 20, "height": 20},
        "agents": {
            "rabbit": {"count": 30, "energy": 15},
            "wolf": {"count": 8, "energy": 30}
        }
    }

    # Create model
    print("Creating streaming predator-prey model...")
    model = abm.create_model(config)
    
    # Add rules
    model = abm.add_rule(model, "random_movement", {})
    model = abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit"})
    model = abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 25})
    model = abm.add_rule(model, "energy_decay", {"species": "all", "rate": 1})
    model = abm.add_rule(model, "death", {})
    
    print(f"Initial agents: {model['metrics']['total_agents']}")
    print(f"Rules: {[rule['name'] for rule in model['rules']]}")
    
    print("\n" + "="*50)
    print("STREAMING SIMULATION - FAST MODE (0.1s delay)")
    print("="*50)
    
    # Stream simulation with fast mode
    stream_states = []
    start_time = time.time()
    
    for state in abm.run_stream(model, steps=50, delay=0.1, callback=print_callback):
        stream_states.append(state)
        
        # Stop if no agents left
        if state['total_agents'] == 0:
            print("All agents died - stopping simulation")
            break
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"\nFast simulation completed in {elapsed:.2f} seconds")
    print(f"Collected {len(stream_states)} state snapshots")
    
    print("\n" + "="*50)
    print("STREAMING SIMULATION - SLOW MODE (0.5s delay)")
    print("="*50)
    
    # Reset model and run again in slow mode
    model = abm.create_model(config)
    model = abm.add_rule(model, "random_movement", {})
    model = abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit"})
    model = abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 25})
    model = abm.add_rule(model, "energy_decay", {"species": "all", "rate": 1})
    model = abm.add_rule(model, "death", {})
    
    slow_stream_states = []
    
    for state in abm.run_stream(model, steps=20, delay=0.5, callback=print_callback):
        slow_stream_states.append(state)
        
        # Stop if no agents left
        if state['total_agents'] == 0:
            print("All agents died - stopping simulation")
            break
    
    print("\n" + "="*50)
    print("STREAM DATA EXPORT EXAMPLES")
    print("="*50)
    
    # Export streaming data
    print("1. Stream JSON Export (first 3 states):")
    if len(stream_states) >= 3:
        json_export = abm.export_stream_json(stream_states[:3])
        print(f"JSON length: {len(json_export)} characters")
        print("Sample:", json_export[:300] + "...")
    
    print("\n2. Stream CSV Export:")
    csv_export = abm.export_stream_csv(stream_states)
    csv_lines = csv_export.split('\n')
    print("CSV Header:", csv_lines[0])
    print("First 5 data rows:")
    for line in csv_lines[1:6]:
        print("  ", line)
    
    print("\n3. Real-time Data Analysis:")
    if stream_states:
        print(f"Total simulation steps: {len(stream_states)}")
        print(f"Peak agent count: {max(state['total_agents'] for state in stream_states)}")
        print(f"Final agent count: {stream_states[-1]['total_agents']}")
        
        # Show population dynamics
        print("\nPopulation over time:")
        for i, state in enumerate(stream_states[::5]):  # Every 5th step
            counts = state['agent_counts']
            rabbits = counts.get('rabbit', 0)
            wolves = counts.get('wolf', 0)
            print(f"  Step {state['step']:2d}: {rabbits:2d} rabbits, {wolves:2d} wolves")
    
    print("\n" + "="*50)
    print("STREAMING FEATURES DEMONSTRATED:")
    print("✓ Real-time state streaming")
    print("✓ Adjustable simulation speed")
    print("✓ Callback functions for custom processing")
    print("✓ Stream data export (JSON/CSV)")
    print("✓ Live population monitoring")
    print("✓ Timestamp tracking")
    print("="*50)

if __name__ == "__main__":
    main()
