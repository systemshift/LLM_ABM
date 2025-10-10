# LLM-ABM v2.0 Architecture

## Design Philosophy

**Goal:** A truly general-purpose agent-based modeling framework where LLMs can generate complete simulations - environment, agents, behaviors, and interactions.

**Key Principles:**
1. **LLM as architect** - Generate entire simulation specifications, not just configurations
2. **Functional & flat** - All docs fit in system prompt (~4K tokens)
3. **Safe execution** - Validate and sandbox all LLM-generated code
4. **Comprehensive logging** - Track all events for future analysis
5. **Zero assumptions** - Don't force grids, energy, or any specific mechanics

## Core Components

### 1. Simulation Specification

A complete simulation is defined by a single JSON-serializable specification:

```python
{
    "metadata": {
        "name": "Predator-Prey Ecosystem",
        "description": "Wolves hunt rabbits with seasonal food variation"
    },
    "environment": {
        "type": "grid_2d",  # or "continuous_2d", "network", "custom"
        "dimensions": {"width": 50, "height": 50},
        "properties": {
            "season": {"type": "cyclic", "period": 100, "values": ["spring", "summer", "fall", "winter"]},
            "food_level": {"type": "function", "code": "..."}
        }
    },
    "agent_types": {
        "rabbit": {
            "initial_count": 80,
            "initial_state": {"energy": 25, "age": 0, "memory": []},
            "behavior_code": "def rabbit_behavior(agent, model, agents_nearby):\n    ..."
        },
        "wolf": {
            "initial_count": 15,
            "initial_state": {"energy": 40, "pack_id": None},
            "behavior_code": "def wolf_behavior(agent, model, agents_nearby):\n    ..."
        }
    },
    "global_functions": {
        "reproduction": "def reproduction(agent, model):\n    ...",
        "death": "def death(agent):\n    ..."
    }
}
```

### 2. Execution Flow

```
1. LLM generates specification → JSON
2. Framework validates specification → Safe code check
3. Compile simulation → Python objects
4. Run simulation loop:
   - Update environment state
   - Execute each agent's behavior function
   - Apply global functions
   - Log all events
   - Update metrics
5. Export results → Full event log + metrics
```

### 3. Agent Behavior Functions

Instead of composing pre-defined rules, each agent type has a complete behavior function:

```python
def rabbit_behavior(agent, model, agents_nearby):
    """
    Full control over agent behavior

    Args:
        agent: This agent's state (dict with any attributes)
        model: Full simulation state (environment, all agents, step number)
        agents_nearby: List of agents in perception range

    Returns:
        actions: List of actions to take this step
    """
    actions = []

    # Agent can make decisions based on anything
    if agent['energy'] < 10:
        # Find food
        food_locations = [p for p in model['environment']['food_patches'] if p['available']]
        if food_locations:
            actions.append({'type': 'move_to', 'target': food_locations[0]})
            actions.append({'type': 'eat'})

    # Check for predators
    wolves_nearby = [a for a in agents_nearby if a['type'] == 'wolf']
    if wolves_nearby:
        actions.append({'type': 'flee', 'direction': 'away_from', 'target': wolves_nearby[0]})

    # Remember last location
    agent['memory'].append(agent['position'])
    if len(agent['memory']) > 10:
        agent['memory'].pop(0)

    return actions
```

### 4. Event Logging

Every action is logged for analysis:

```python
{
    "step": 42,
    "timestamp": 1234567890.123,
    "events": [
        {
            "type": "agent_action",
            "agent_id": 5,
            "agent_type": "rabbit",
            "action": "move",
            "details": {"from": [10, 15], "to": [11, 15]}
        },
        {
            "type": "interaction",
            "agents": [12, 5],
            "interaction_type": "predation_attempt",
            "outcome": "failed",
            "reason": "prey_too_fast"
        },
        {
            "type": "state_change",
            "agent_id": 5,
            "attribute": "energy",
            "old_value": 15,
            "new_value": 14,
            "cause": "movement_cost"
        },
        {
            "type": "agent_birth",
            "parent_id": 23,
            "child_id": 45,
            "agent_type": "rabbit"
        }
    ]
}
```

## Directory Structure

```
llm_abm/
├── core/
│   ├── simulation.py          # Main simulation engine
│   ├── environment.py         # Environment management
│   ├── agent_system.py        # Agent lifecycle
│   ├── behavior_engine.py     # Execute agent behaviors
│   ├── event_logger.py        # Event logging system
│   └── action_processor.py    # Process agent actions
├── generation/
│   ├── validator.py           # Validate LLM code
│   ├── compiler.py            # Compile spec to simulation
│   └── safety.py              # Safe code execution
├── prompts/
│   ├── system_prompt.py       # Main LLM system prompt
│   └── examples.py            # Example specifications
├── api.py                     # Public API functions
└── __init__.py                # Package exports
```

## API Design

### Simple API (5 functions)

```python
import llm_abm as abm

# 1. Create simulation from specification
sim = abm.create_simulation(spec_dict)

# 2. Run simulation
results = abm.run(sim, steps=100, log_level="detailed")

# 3. Stream simulation (real-time)
for state in abm.run_stream(sim, steps=100):
    print(f"Step {state['step']}: {state['agent_counts']}")

# 4. Export results
abm.export(results, "simulation.json", format="json")
abm.export(results, "events.csv", format="csv")

# 5. Validate specification
is_valid, errors = abm.validate_spec(spec_dict)
```

## Backwards Compatibility

Keep old API working for existing users:

```python
# Old API (v1.0) - still works
config = {"grid": {...}, "agents": {...}}
model = abm.create_model(config)
model = abm.add_rule(model, "predator_prey", {...})
results = abm.run(model, steps=100)

# New API (v2.0) - full power
spec = {"environment": {...}, "agent_types": {...}}
sim = abm.create_simulation(spec)
results = abm.run(sim, steps=100)
```

## System Prompt Strategy

The LLM system prompt will contain:
1. **Core concepts** (~500 tokens) - What a simulation spec looks like
2. **Behavior function guide** (~800 tokens) - How to write agent behaviors
3. **Complete example** (~1200 tokens) - Working predator-prey simulation
4. **Common patterns** (~500 tokens) - Movement, interaction, reproduction
5. **Safety guidelines** (~200 tokens) - What's allowed/forbidden

**Total: ~3200 tokens** - Fits in context, LLM learns through examples

## Implementation Phases

### Phase 1: Core Engine (Current)
- Simulation execution loop
- Environment system
- Agent behavior execution
- Event logging

### Phase 2: Code Generation (Next)
- Validator and compiler
- System prompts
- Example specifications

### Phase 3: Integration (Final)
- Update web app
- Migration guide
- Documentation
