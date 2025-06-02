# LLM-ABM: Agent-Based Modeling Library for LLMs

A functional, documentation-first ABM library designed specifically for LLM code generation. Features pure functions with predictable inputs/outputs, using simple dictionaries for all state management.

## Core Design Philosophy

- **Functional, Not Object-Oriented**: No classes, inheritance, or complex OOP patterns
- **Documentation-First**: All documentation fits in system prompt space
- **JSON-Native Configuration**: Simple dictionaries for all configuration
- **Template-Heavy Approach**: Pre-built rule templates for common ABM patterns

## Quick Start

```python
import llm_abm as abm

# Create model from simple config
config = {
    "grid": {"width": 50, "height": 50},
    "agents": {
        "rabbit": {"count": 100, "energy": 20},
        "wolf": {"count": 20, "energy": 40}
    }
}

model = abm.create_model(config)

# Add behavioral rules
model = abm.add_rule(model, "random_movement", {})
model = abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit"})
model = abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 30})
model = abm.add_rule(model, "energy_decay", {"species": "all", "rate": 1})
model = abm.add_rule(model, "death", {})

# Run simulation
results = abm.run(model, steps=100)

# Export data
summary = abm.export(results, format="summary")
json_data = abm.export(results, format="json")
csv_data = abm.export(results, format="csv")
```

## Core API (5 Functions)

### `create_model(config)`
Create model from simple config dictionary

### `add_rule(model, rule_name, params={})`
Add behavioral rule to model

### `step(model)`
Advance simulation one step

### `run(model, steps=100)`
Run simulation for multiple steps

### `export(results, format="json")`
Export data in various formats

## Available Rule Templates

### Movement Rules
- `random_movement`: Move agents randomly to adjacent cells
- `directed_movement`: Move agents toward target agent type

### Interaction Rules
- `predator_prey`: Handle predator-prey interactions with energy transfer
- `competition`: Handle resource competition between agents

### Lifecycle Rules
- `energy_decay`: Reduce agent energy each step
- `reproduction`: Spawn new agents when energy threshold is met
- `death`: Handle agent death when energy reaches zero
- `aging`: Age agents and handle death by old age

## Configuration Format

```python
config = {
    "grid": {
        "width": 50,
        "height": 50,
        "topology": "torus"  # or "bounded"
    },
    "agents": {
        "rabbit": {
            "count": 100,
            "energy": 20,
            "position": "random",  # or "center"
            "properties": {
                "speed": 1,
                "vision_range": 2
            }
        }
    },
    "environment": {
        "carrying_capacity": 200,
        "resource_regeneration": 0.1
    }
}
```

## Key Features

- **Pure Functions**: No side effects, predictable behavior
- **Dictionary State**: All model state as simple dictionaries
- **Rule Templates**: Pre-built behaviors for common patterns
- **Multiple Export Formats**: JSON, CSV, and human-readable summaries
- **Spatial Grid Support**: Torus and bounded topologies
- **Energy-Based Lifecycle**: Built-in energy and reproduction systems

## Examples

See `example_predator_prey.py` for a complete working example of a classic predator-prey simulation.

## Library Structure

```
llm_abm/
├── __init__.py          # Main API functions
├── core/
│   ├── model.py         # Model state management
│   ├── agent.py         # Agent data structures
│   ├── grid.py          # Spatial management
│   └── scheduler.py     # Step execution
├── rules/
│   ├── movement.py      # Movement rule templates
│   ├── interaction.py   # Interaction rule templates
│   └── lifecycle.py     # Birth/death rule templates
└── utils/
    ├── export.py        # Data export functions
    └── validation.py    # Config validation
```

## Data Structures

All state stored as simple dictionaries:

```python
# Model State
model = {
    "config": {...},
    "agents": [
        {
            "id": 1,
            "type": "rabbit",
            "position": {"x": 25, "y": 30},
            "energy": 15,
            "age": 5,
            "alive": True,
            "properties": {...}
        }
    ],
    "grid": {...},
    "rules": [...],
    "step": 0,
    "metrics": {...}
}
```

## LLM Optimization

This library is specifically designed for LLM code generation:

- Complete documentation fits in system prompt space
- No cross-references or external dependencies
- Self-explanatory function signatures
- Comprehensive error messages with fix suggestions
- Copy-pasteable examples that always work

## Version

0.1.0 - MVP Core Implementation

## License

See LICENSE file for details.
