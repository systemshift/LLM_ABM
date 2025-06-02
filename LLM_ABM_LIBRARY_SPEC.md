# LLM-ABM: Agent-Based Modeling Library for LLMs

## Project Overview

**Goal**: Create an Agent-Based Modeling library specifically designed for LLM code generation, not human developers.

**Key Insight**: Existing ABM libraries (Mesa, NetLogo, etc.) are designed for humans with complex OOP patterns. LLMs struggle with object-oriented complexity, inheritance, and scattered documentation. We need a radically simplified, functional approach.

## Core Design Philosophy

### 1. **Functional, Not Object-Oriented**
- No classes, inheritance, or complex OOP patterns
- Pure functions with predictable inputs/outputs
- All state as simple dictionaries and lists
- No hidden object state or side effects

### 2. **Documentation-First Design**
- **Critical Constraint**: All documentation must fit in 2-4K tokens (system prompt space)
- Every function self-explanatory from signature alone
- No cross-references or "see other sections"
- Complete, copy-pasteable examples

### 3. **JSON-Native Configuration**
- All model configuration as simple dictionaries
- No complex configuration objects or builders
- Easy serialization/deserialization
- Human and LLM readable

### 4. **Template-Heavy Approach**
- Pre-built rule templates for common ABM patterns
- Simple rule composition and combination
- Minimal custom code required

## API Design

### Core Functions (5 Total)

```python
import llm_abm as abm

# 1. Create model from simple config
model = abm.create_model(config)

# 2. Add behavioral rules
model = abm.add_rule(model, rule_name, params={})

# 3. Advance simulation one step
model = abm.step(model)

# 4. Run simulation for multiple steps
results = abm.run(model, steps=100)

# 5. Export data in various formats
data = abm.export(results, format="json")
```

### Configuration Format

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
            "position": "random",  # or "center", "edges"
            "properties": {
                "speed": 1,
                "vision_range": 2
            }
        },
        "wolf": {
            "count": 20,
            "energy": 40,
            "position": "random"
        }
    },
    "environment": {
        "carrying_capacity": 200,
        "resource_regeneration": 0.1
    }
}
```

### Available Rule Templates

```python
# Movement Rules
abm.add_rule(model, "random_movement", {"species": "all"})
abm.add_rule(model, "directed_movement", {"species": "wolf", "target": "rabbit"})
abm.add_rule(model, "flocking", {"species": "bird", "radius": 5})
abm.add_rule(model, "avoidance", {"species": "rabbit", "avoid": "wolf", "radius": 3})

# Interaction Rules  
abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit", "success_rate": 0.8})
abm.add_rule(model, "competition", {"species": ["rabbit"], "resource": "grass"})
abm.add_rule(model, "cooperation", {"species": "ant", "task": "foraging"})

# Life Cycle Rules
abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 30, "rate": 0.1})
abm.add_rule(model, "energy_decay", {"species": "all", "rate": 1})
abm.add_rule(model, "aging", {"species": "all", "death_age": 100})

# Environmental Rules
abm.add_rule(model, "resource_growth", {"type": "grass", "rate": 0.05})
abm.add_rule(model, "seasonal_change", {"parameter": "temperature", "cycle": 365})
```

## Architecture

### Layer 1: Core Engine (Functional)

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
│   ├── lifecycle.py     # Birth/death rule templates
│   └── environment.py   # Environmental rule templates
└── utils/
    ├── export.py        # Data export functions
    └── validation.py    # Config validation
```

### Layer 2: Data Structures

All state as simple dictionaries:

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
            "properties": {...}
        }
    ],
    "grid": {
        "width": 50,
        "height": 50,
        "cells": {...}
    },
    "rules": [
        {"name": "random_movement", "params": {...}},
        {"name": "predator_prey", "params": {...}}
    ],
    "step": 0,
    "metrics": {...}
}
```

### Layer 3: Rule System

Rules as pure functions:

```python
def random_movement(model, params):
    """Move agents randomly to adjacent cells"""
    new_model = model.copy()
    for agent in new_model["agents"]:
        if params.get("species", "all") in ["all", agent["type"]]:
            # Calculate new position
            agent["position"] = get_random_adjacent(agent["position"], model["grid"])
    return new_model
```

### Layer 4: Visualization (Optional)

```
llm_abm/visual/
├── __init__.py          # Main visual API
├── exporters/
│   ├── d3.py           # D3.js code generation
│   ├── plotly.py       # Plotly charts
│   └── canvas.py       # HTML5 Canvas
└── templates/
    ├── grid.html       # Grid visualization template
    ├── network.html    # Network visualization template
    └── chart.html      # Chart visualization template
```

## Development Timeline

### Phase 1: Core Engine (2-3 weeks)
**Week 1-2: Foundation**
- Basic model state management
- Agent creation and placement
- Grid/space data structures
- Step execution framework

**Week 3: Basic Rules**
- Random movement
- Simple interactions
- Energy decay
- Data collection

**Deliverable**: Working predator-prey model

### Phase 2: Rule Templates (2-3 weeks)
**Week 4: Movement Rules**
- Random movement
- Directed movement
- Flocking behaviors
- Avoidance behaviors

**Week 5: Interaction Rules**
- Predator-prey
- Competition
- Cooperation
- Resource consumption

**Week 6: Lifecycle Rules**
- Reproduction
- Aging and death
- Energy management

**Deliverable**: 15-20 core rule templates

### Phase 3: Model Types (2 weeks)
**Week 7: Spatial Models**
- Grid models (cellular automata style)
- Continuous space models
- Network models

**Week 8: Non-Spatial Models**
- Chart/data models
- Population dynamics
- Economic models

**Deliverable**: Support for 4 model types

### Phase 4: Integration & Testing (1-2 weeks)
**Week 9: LLM Testing**
- Prompt engineering
- Error message optimization
- Validation and edge cases

**Week 10: Performance**
- Optimization for large models
- Memory efficiency
- Speed improvements

**Deliverable**: Production-ready core library

### Phase 5: Visualization (1-2 weeks)
**Week 11: Basic Visualization**
- Automatic D3.js generation
- Grid and agent rendering
- Basic animations

**Week 12: Advanced Features**
- Custom styling
- Interactive controls
- Multi-format export

**Deliverable**: Complete visualization system

## Key Success Criteria

### 1. LLM Usability
- [ ] LLM can generate working models from documentation alone
- [ ] No external references needed in prompts
- [ ] Clear error messages with fix suggestions
- [ ] Every example is complete and runnable

### 2. Documentation Constraints
- [ ] Complete API documentation ≤ 2K tokens
- [ ] Rule catalog ≤ 1.5K tokens
- [ ] Examples ≤ 500 tokens total
- [ ] No cross-references between sections

### 3. Functional Requirements
- [ ] Support grid, network, and particle models
- [ ] Handle 1000+ agents efficiently
- [ ] Real-time visualization (optional)
- [ ] Export to JSON, CSV, visualization formats

### 4. Code Quality
- [ ] 100% pure functions (no side effects)
- [ ] Comprehensive type hints
- [ ] 90%+ test coverage
- [ ] Clear separation of concerns

## Example Models

### 1. Predator-Prey (Classic)
```python
config = {
    "grid": {"width": 50, "height": 50},
    "agents": {
        "rabbit": {"count": 100, "energy": 20},
        "wolf": {"count": 20, "energy": 40}
    }
}

model = abm.create_model(config)
model = abm.add_rule(model, "random_movement", {})
model = abm.add_rule(model, "predator_prey", {"predator": "wolf", "prey": "rabbit"})
model = abm.add_rule(model, "reproduction", {"species": "rabbit", "energy_threshold": 30})
model = abm.add_rule(model, "energy_decay", {"species": "all", "rate": 1})

results = abm.run(model, steps=1000)
```

### 2. Flocking Birds
```python
config = {
    "space": {"type": "continuous", "width": 200, "height": 200},
    "agents": {"bird": {"count": 50, "speed": 2}}
}

model = abm.create_model(config)
model = abm.add_rule(model, "flocking", {"species": "bird", "radius": 10})
model = abm.add_rule(model, "boundary_wrap", {"species": "bird"})

results = abm.run(model, steps=500)
```

### 3. Disease Spread
```python
config = {
    "grid": {"width": 100, "height": 100},
    "agents": {
        "person": {"count": 1000, "state": "susceptible"},
        "infected": {"count": 10, "state": "infected"}
    }
}

model = abm.create_model(config)
model = abm.add_rule(model, "random_movement", {"species": "all"})
model = abm.add_rule(model, "disease_spread", {"infection_rate": 0.1, "recovery_rate": 0.05})

results = abm.run(model, steps=365)
```

## Implementation Notes

### Performance Considerations
- Use NumPy for agent arrays when count > 1000
- Spatial indexing for efficient neighbor queries
- Vectorized operations where possible
- Memory-efficient state updates

### Error Handling
- Validate all configs before simulation
- Provide specific fix suggestions in error messages
- Graceful degradation for invalid parameters
- Comprehensive logging for debugging

### Extensibility
- Plugin system for custom rules
- Hook system for custom metrics
- Template system for new model types
- Custom visualization renderers

### Testing Strategy
- Unit tests for all core functions
- Integration tests for complete models
- LLM testing with real prompts
- Performance benchmarks
- Cross-platform compatibility

## Documentation Structure

### Core Documentation (≤2K tokens)
```markdown
# LLM-ABM Quick Reference

## Core Functions
create_model(config) → model
add_rule(model, rule, params) → model  
run(model, steps) → results

## Config Format
{"grid": {"width": N, "height": N}, "agents": {"type": {"count": N}}}

## Basic Example
model = create_model({"grid": {"width": 20, "height": 20}, "agents": {"ant": {"count": 100}}})
model = add_rule(model, "random_movement", {})
results = run(model, steps=100)

## Available Rules
random_movement, predator_prey, reproduction, energy_decay, flocking, avoidance
```

### Rule Catalog (≤1.5K tokens)
Each rule documented with:
- Purpose (1 sentence)
- Parameters (with defaults)
- Complete example
- Expected behavior

### Advanced Patterns (≤1K tokens)
- Combining multiple rules
- Custom rule creation
- Performance optimization
- Troubleshooting guide

## Future Enhancements

### Version 2.0 Features
- GPU acceleration for large models
- Distributed simulation
- Real-time parameter adjustment
- Advanced visualization features
- Integration with ML libraries

### LLM Integration Features
- Automatic rule suggestion based on model description
- Natural language rule creation
- Model validation and optimization
- Automatic documentation generation

## Success Metrics

### Adoption Metrics
- LLM success rate in generating working models
- Time from prompt to working simulation
- Error rate and debugging time
- Community adoption and contributions

### Technical Metrics
- Performance: 10K agents at 60 FPS
- Memory usage: <100MB for typical models
- Load time: <1 second for model creation
- Documentation coverage: 100% of API

## Risk Mitigation

### Technical Risks
- **Performance**: Early optimization, benchmarking
- **Complexity**: Strict API limits, regular LLM testing
- **Bugs**: Comprehensive testing, gradual rollout

### Adoption Risks
- **LLM Compatibility**: Test with multiple LLM providers
- **Documentation**: User testing, iterative improvement
- **Ecosystem**: Integration with existing tools

This specification serves as the complete roadmap for creating an LLM-optimized ABM library that prioritizes simplicity, predictability, and documentation efficiency over traditional software engineering flexibility.
