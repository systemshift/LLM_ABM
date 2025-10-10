"""
LLM System Prompt Documentation

Compact documentation designed for system prompts (≤2K tokens).
Contains everything an LLM needs to generate working ABM simulations.
"""

def get_system_prompt_docs():
    """
    Return complete LLM-ABM documentation for system prompts
    
    Returns:
        str: Complete documentation under 2K tokens
    """
    return """# LLM-ABM: Agent-Based Modeling Library

## Core API (5 Functions)
```python
import llm_abm as abm

# 1. Create model from config
model = abm.create_model(config)

# 2. Add behavioral rules  
model = abm.add_rule(model, rule_name, params)

# 3. Run simulation
results = abm.run(model, steps=100)

# 4. Stream real-time simulation
for state in abm.run_stream(model, steps=50, delay=0.1):
    print(f"Step {state['step']}: {state['agent_counts']}")

# 5. Export data
data = abm.export(results, format="json")
```

## Configuration Format
```python
config = {
    "grid": {"width": 50, "height": 50, "topology": "torus"},
    "agents": {
        "rabbit": {"count": 100, "energy": 20, "position": "random"},
        "wolf": {"count": 20, "energy": 40}
    }
}
```

## Available Rules
**Movement:**
- `random_movement` - Random walk: `{"species": "all"}`
- `directed_movement` - Chase targets: `{"species": "wolf", "target": "rabbit"}`

**Interactions:**
- `predator_prey` - Hunting: `{"predator": "wolf", "prey": "rabbit", "success_rate": 0.5, "energy_gain": 10}`
- `grazing` - Herbivores gain energy: `{"species": "rabbit", "energy_gain": 2, "probability": 0.7}`
- `competition` - Resource competition: `{"species": ["rabbit"], "energy_per_resource": 5}`

**Lifecycle:**
- `energy_decay` - Energy loss: `{"species": "all", "rate": 0.8}`
- `reproduction` - Breeding: `{"species": "rabbit", "energy_threshold": 30, "rate": 0.08}`
- `death` - Death at zero energy: `{}`
- `aging` - Age-based death: `{"death_age": 100}`

**Balance Tips:**
- Prey MUST gain energy (use `grazing`) or they die
- Lower predation success (0.4-0.5) for sustainable populations
- Match energy_decay rate to energy_gain for equilibrium

## Custom Rules (Advanced)
```python
# From LLM-generated code
custom_code = '''
def pack_hunting(model, params):
    new_model = copy.deepcopy(model)
    for agent in new_model['agents']:
        if agent['type'] == 'wolf':
            # Custom behavior here
    return new_model
'''
model = abm.add_custom_rule(model, "pack_hunting", custom_code, "code")

# From simple conditions/actions
rule_dsl = {
    "conditions": ["agent['energy'] < 10", "agent['type'] == 'rabbit'"],
    "actions": ["agent['energy'] += 5"]
}
model = abm.add_custom_rule(model, "foraging", rule_dsl, "dsl")
```

## Complete Example (BALANCED)
```python
# Sustainable predator-prey ecosystem
config = {
    "grid": {"width": 30, "height": 30},
    "agents": {
        "rabbit": {"count": 80, "energy": 25},
        "wolf": {"count": 15, "energy": 40}
    }
}

model = abm.create_model(config)
model = abm.add_rule(model, "random_movement", {})
model = abm.add_rule(model, "grazing", {"species": "rabbit", "energy_gain": 1.5})  # KEY: Rabbits gain energy!
model = abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit", "success_rate": 0.4, "energy_gain": 10})
model = abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 30, "rate": 0.08})
model = abm.add_rule(model, "reproduction", {"species": "wolf", "energy_threshold": 50, "rate": 0.04})
model = abm.add_rule(model, "energy_decay", {"rate": 0.8})  # Reduced from 1
model = abm.add_rule(model, "death", {})

results = abm.run(model, steps=200)
print(f"Final: {results['summary']['final_counts']}")  # Both populations survive!
```

## Data Structures
- Model: `{"config": {}, "agents": [], "grid": {}, "rules": [], "step": 0}`
- Agent: `{"id": 1, "type": "rabbit", "position": {"x": 5, "y": 3}, "energy": 15, "alive": true}`
- All functions pure (no side effects), state as simple dictionaries

## Key Features
- Functional programming (no classes)
- JSON-native configuration
- Real-time streaming simulation
- Safe custom rule execution
- Built for LLM code generation"""

def get_rule_reference():
    """
    Return quick rule reference for LLMs
    
    Returns:
        str: Rule catalog under 1K tokens
    """
    return """# Rule Quick Reference

## Movement Rules
- **random_movement**: Random walk to adjacent cells
  - `species`: "all" or agent type (default: "all")

- **directed_movement**: Move toward target agent type  
  - `species`: Agent type that moves
  - `target`: Target agent type

## Interaction Rules
- **predator_prey**: Hunting with energy transfer
  - `predator`: Predator agent type
  - `prey`: Prey agent type
  - `success_rate`: Hunt success probability (default: 0.5)
  - `energy_gain`: Fixed energy gained per kill (default: 10)

- **grazing**: Herbivores gain energy from environment
  - `species`: Agent type that grazes
  - `energy_gain`: Energy gained per step (default: 2)
  - `probability`: Chance of successful grazing (default: 0.7)

- **competition**: Resource competition between species
  - `species`: List of competing agent types
  - `energy_per_resource`: Energy gained per resource (default: 5)

## Lifecycle Rules
- **energy_decay**: Reduce energy each step
  - `species`: "all" or agent type (default: "all")
  - `rate`: Energy loss per step (default: 0.8, was 1)

- **reproduction**: Spawn offspring when energy threshold met
  - `species`: Agent type that reproduces
  - `energy_threshold`: Min energy to reproduce (default: 30)
  - `rate`: Reproduction probability (default: 0.08, typical range: 0.04-0.15)

- **death**: Kill agents when energy reaches zero
  - `species`: "all" or agent type (default: "all")

- **aging**: Age agents and handle age-based death
  - `species`: "all" or agent type (default: "all")  
  - `death_age`: Age at death (default: 100)"""
