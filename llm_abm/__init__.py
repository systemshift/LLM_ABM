"""
LLM-ABM: Agent-Based Modeling Library for LLMs

A functional, documentation-first ABM library designed specifically for LLM code generation.
All functions are pure with predictable inputs/outputs, using simple dictionaries for state.
"""

from .core.model import create_model, step, run
from .core.agent import add_rule
from .utils.export import export

__version__ = "0.1.0"
__all__ = ["create_model", "add_rule", "step", "run", "export"]

# Main API - exactly 5 functions as specified
def create_model(config):
    """Create model from simple config dictionary"""
    from .core.model import create_model as _create_model
    return _create_model(config)

def add_rule(model, rule_name, params=None):
    """Add behavioral rule to model"""
    from .core.agent import add_rule as _add_rule
    return _add_rule(model, rule_name, params or {})

def step(model):
    """Advance simulation one step"""
    from .core.model import step as _step
    return _step(model)

def run(model, steps=100):
    """Run simulation for multiple steps"""
    from .core.model import run as _run
    return _run(model, steps)

def export(results, format="json"):
    """Export data in various formats"""
    from .utils.export import export as _export
    return _export(results, format)
