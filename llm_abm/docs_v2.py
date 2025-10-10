"""
LLM System Prompt Documentation for v2.0

Complete documentation for general-purpose ABM framework where LLMs
generate full simulation specifications with agent behavior code.
"""

def get_v2_system_prompt():
    """
    Return complete v2.0 documentation for system prompts

    Returns:
        str: Complete documentation for v2.0 framework
    """
    return """# LLM-ABM v2.0: General-Purpose Agent-Based Modeling

## Overview
Generate complete agent-based simulations with custom behaviors, not just configurations.
You write the full agent behavior code, environment properties, and interaction logic.

## Core API
```python
import llm_abm

# Create simulation from complete specification
sim = llm_abm.create_simulation(spec)

# Run simulation
results = llm_abm.run_v2(sim, steps=200)

# Export results
llm_abm.export_v2(results, "simulation.json")
```

## Simulation Specification Format

```python
spec = {
    "metadata": {
        "name": "Predator-Prey Ecosystem",
        "description": "Wolves hunt rabbits with emergent dynamics"
    },
    "environment": {
        "type": "grid_2d",  # or "continuous_2d", "network", "custom"
        "dimensions": {"width": 30, "height": 30, "topology": "torus"},
        "properties": {
            "season": "spring",
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
            "behavior_code": "PYTHON_FUNCTION_CODE_HERE"
        }
    }
}
```

## Writing Agent Behavior Functions

Each agent type needs a behavior function that returns a list of actions:

```python
def rabbit_behavior(agent, model, agents_nearby):
    '''
    Define complete agent behavior

    Args:
        agent: Agent object with .id, .type, .state dict
        model: Current simulation state (step, environment, agent_counts)
        agents_nearby: List of agents within perception_radius

    Returns:
        actions: List of action dictionaries
    '''
    actions = []

    # Access agent attributes
    energy = agent.get_attribute('energy', 25)
    position = agent.get_attribute('position')

    # Make decisions based on state
    if energy < 15:
        # Gain energy from environment
        actions.append({
            'type': 'modify_state',
            'attribute': 'energy',
            'delta': 2
        })

    # React to nearby agents
    wolves = [a for a in agents_nearby if a.type == 'wolf' and a.alive]
    if wolves:
        # Flee from wolves
        wolf_pos = wolves[0].get_attribute('position')
        dx = 1 if position[0] < wolf_pos[0] else -1
        dy = 1 if position[1] < wolf_pos[1] else -1
        actions.append({
            'type': 'move',
            'direction': [dx, dy]
        })
    else:
        # Move randomly
        actions.append({
            'type': 'move',
            'direction': [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
        })

    # Reproduction
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

    # Death condition
    if energy <= 0:
        actions.append({'type': 'die', 'cause': 'starvation'})

    return actions
```

## Available Action Types

**Movement:**
- `{'type': 'move', 'direction': [dx, dy]}` - Move by direction
- `{'type': 'move_to', 'target': (x, y)}` - Move toward position
- `{'type': 'move_random'}` - Random movement

**State Modification:**
- `{'type': 'modify_state', 'attribute': 'energy', 'delta': 5}` - Change attribute
- `{'type': 'modify_state', 'attribute': 'color', 'value': 'red'}` - Set attribute

**Interactions:**
- `{'type': 'interact', 'target_id': agent_id, 'interaction_type': 'predation', 'params': {...}}` - Interact with agent

**Lifecycle:**
- `{'type': 'reproduce', 'energy_cost': 10, 'offspring_count': 1}` - Create offspring
- `{'type': 'die', 'cause': 'starvation'}` - Agent death

**Predation Interaction:**
```python
actions.append({
    'type': 'interact',
    'target_id': prey.id,
    'interaction_type': 'predation',
    'params': {
        'success_rate': 0.4,
        'energy_gain': 10
    }
})
```

## Built-in Modules Available

Your behavior code has access to:
- `random` module (random.random(), random.choice(), etc.)
- `math` module (math.sqrt(), math.sin(), etc.)
- Basic builtins: abs, len, max, min, sum, range, list, dict, etc.

**Do NOT use `import` statements** - modules are already available.

## Agent Attributes

Agents can have any attributes you define:
- `energy`, `age`, `health` (numeric)
- `state`, `color`, `role` (strings)
- `memory`, `inventory` (lists)
- `perception_radius` (affects agents_nearby)
- Custom attributes for your simulation

## Complete Working Example

```python
spec = {
    "environment": {
        "type": "grid_2d",
        "dimensions": {"width": 30, "height": 30, "topology": "torus"}
    },
    "agent_types": {
        "rabbit": {
            "initial_count": 80,
            "initial_state": {"energy": 25, "perception_radius": 5},
            "behavior_code": '''
def rabbit_behavior(agent, model, agents_nearby):
    actions = []
    energy = agent.get_attribute('energy', 25)

    # Graze for energy
    if energy < 15:
        actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': 2})

    # Flee from wolves
    wolves = [a for a in agents_nearby if a.type == 'wolf']
    if wolves:
        wolf_pos = wolves[0].get_attribute('position')
        position = agent.get_attribute('position')
        dx = 1 if position[0] < wolf_pos[0] else -1
        dy = 1 if position[1] < wolf_pos[1] else -1
        actions.append({'type': 'move', 'direction': [dx, dy]})
    else:
        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})

    # Reproduce
    if energy > 30 and random.random() < 0.08:
        actions.append({'type': 'reproduce', 'energy_cost': 15, 'offspring_count': 1})

    # Energy decay
    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -0.8})

    # Death
    if energy <= 0:
        actions.append({'type': 'die', 'cause': 'starvation'})

    return actions
'''
        },
        "wolf": {
            "initial_count": 15,
            "initial_state": {"energy": 40, "perception_radius": 7},
            "behavior_code": '''
def wolf_behavior(agent, model, agents_nearby):
    actions = []
    energy = agent.get_attribute('energy', 40)
    position = agent.get_attribute('position')

    # Hunt rabbits
    rabbits = [a for a in agents_nearby if a.type == 'rabbit' and a.alive]
    if rabbits:
        rabbit = rabbits[0]
        rabbit_pos = rabbit.get_attribute('position')

        if position == rabbit_pos:
            # Attack
            actions.append({
                'type': 'interact',
                'target_id': rabbit.id,
                'interaction_type': 'predation',
                'params': {'success_rate': 0.4, 'energy_gain': 10}
            })
        else:
            # Chase
            actions.append({'type': 'move_to', 'target': rabbit_pos})
    else:
        # Search
        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})

    # Reproduce
    if energy > 50 and random.random() < 0.04:
        actions.append({'type': 'reproduce', 'energy_cost': 20, 'offspring_count': 1})

    # Energy decay
    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -0.8})

    # Death
    if energy <= 0:
        actions.append({'type': 'die', 'cause': 'starvation'})

    return actions
'''
        }
    }
}
```

## Balance Tips

For sustainable ecosystems:
- Prey need energy INPUT (grazing/modify_state with positive delta)
- Predators should have lower reproduction rates (0.02-0.05 vs 0.08-0.15 for prey)
- Energy decay should match typical energy gain (0.8 decay with 1.5-2 gain)
- Predation success rate around 0.3-0.5 for balance
- Give prey faster reproduction than predators

## Key Differences from v1.0

**v1.0:** Pick from pre-defined rules (grazing, predator_prey, reproduction)
**v2.0:** Write complete behavior functions with full control

v2.0 gives you:
- Custom decision-making logic
- Agent memory and learning
- Complex interactions
- Arbitrary attributes
- Full flexibility

## Output Format

Always return valid Python dict with proper structure:
- Use triple quotes for behavior_code strings
- Ensure behavior functions have correct signature
- Return list of action dicts from behavior functions
- Include all required fields (environment, agent_types)"""


def get_v2_quick_reference():
    """
    Quick reference for action types and patterns

    Returns:
        str: Quick reference guide
    """
    return """# v2.0 Quick Reference

## Action Types
- move: {'type': 'move', 'direction': [dx, dy]}
- move_to: {'type': 'move_to', 'target': (x, y)}
- modify_state: {'type': 'modify_state', 'attribute': 'energy', 'delta': 5}
- interact: {'type': 'interact', 'target_id': id, 'interaction_type': 'predation', 'params': {}}
- reproduce: {'type': 'reproduce', 'energy_cost': 10, 'offspring_count': 1}
- die: {'type': 'die', 'cause': 'reason'}

## Agent Methods
- agent.get_attribute('energy', default)
- agent.set_attribute('energy', value)
- agent.type (string)
- agent.id (int)
- agent.alive (bool)

## Common Patterns

**Energy Management:**
```python
if energy < threshold:
    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': gain})
```

**Fleeing:**
```python
predators = [a for a in agents_nearby if a.type == 'predator']
if predators:
    pred_pos = predators[0].get_attribute('position')
    dx = 1 if position[0] < pred_pos[0] else -1
    dy = 1 if position[1] < pred_pos[1] else -1
    actions.append({'type': 'move', 'direction': [dx, dy]})
```

**Hunting:**
```python
prey = [a for a in agents_nearby if a.type == 'prey' and a.alive]
if prey and position == prey[0].get_attribute('position'):
    actions.append({
        'type': 'interact',
        'target_id': prey[0].id,
        'interaction_type': 'predation',
        'params': {'success_rate': 0.4, 'energy_gain': 10}
    })
```"""
