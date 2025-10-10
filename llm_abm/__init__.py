"""
LLM-ABM: Agent-Based Modeling Library for LLMs

A functional, documentation-first ABM library designed specifically for LLM code generation.

Two APIs available:
- v1.0 (legacy): Rule-based composition system
- v2.0 (new): General-purpose framework with full LLM-generated environments and behaviors
"""

# v1.0 API (legacy - rule-based)
from .core.model import create_model as _create_model_v1
from .core.model import step as _step_v1
from .core.model import run as _run_v1
from .core.agent import add_rule as _add_rule_v1
from .utils.export import export as _export_v1
from .utils.export import run_stream as _run_stream_v1
from .utils.export import export_stream_json, export_stream_csv
from .core.rule_engine import add_custom_rule, rule_engine
from .docs import get_system_prompt_docs, get_rule_reference

# v2.0 API (new - general-purpose)
from .api_v2 import (
    create_simulation,
    run as run_v2,
    run_stream as run_stream_v2,
    export as export_v2,
    validate_specification,
    get_state,
    quick_simulation
)

__version__ = "0.2.0"

# Expose v1.0 API as default for backwards compatibility
__all__ = [
    # v1.0 API
    "create_model", "add_rule", "step", "run", "export",
    "run_stream", "export_stream_json", "export_stream_csv",
    "add_custom_rule", "list_custom_rules",
    "get_system_prompt_docs", "get_rule_reference",
    # v2.0 API
    "create_simulation", "validate_specification", "get_state", "quick_simulation"
]

# v1.0 API wrapper functions (for backwards compatibility)
def create_model(config):
    """Create model from simple config dictionary (v1.0 API)"""
    return _create_model_v1(config)

def add_rule(model, rule_name, params=None):
    """Add behavioral rule to model (v1.0 API)"""
    return _add_rule_v1(model, rule_name, params or {})

def step(model):
    """Advance simulation one step (v1.0 API)"""
    return _step_v1(model)

def run(model, steps=100):
    """Run simulation for multiple steps (v1.0 API)"""
    return _run_v1(model, steps)

def export(results, format="json"):
    """Export data in various formats (v1.0 API)"""
    return _export_v1(results, format)

def run_stream(model, steps=100, delay=0.1, callback=None):
    """Run simulation with streaming output (v1.0 API)"""
    return _run_stream_v1(model, steps, delay, callback)

def list_custom_rules():
    """List all custom rules with metadata"""
    return rule_engine.list_rules()
