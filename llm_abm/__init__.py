"""
LLM-ABM: Agent-Based Modeling Library for LLMs

A functional, documentation-first ABM library designed specifically for LLM code generation.
All functions are pure with predictable inputs/outputs, using simple dictionaries for state.
"""

from .core.model import create_model, step, run
from .core.agent import add_rule
from .utils.export import export, run_stream, export_stream_json, export_stream_csv
from .core.rule_engine import add_custom_rule, rule_engine
from .docs import get_system_prompt_docs, get_rule_reference

__version__ = "0.1.0"
__all__ = ["create_model", "add_rule", "step", "run", "export", "run_stream", "export_stream_json", "export_stream_csv", "add_custom_rule", "list_custom_rules", "get_system_prompt_docs", "get_rule_reference"]

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

def run_stream(model, steps=100, delay=0.1, callback=None):
    """Run simulation with streaming output and time control"""
    from .utils.export import run_stream as _run_stream
    return _run_stream(model, steps, delay, callback)

def export_stream_json(stream_states):
    """Convert stream states to JSON format"""
    from .utils.export import export_stream_json as _export_stream_json
    return _export_stream_json(stream_states)

def export_stream_csv(stream_states):
    """Convert stream states to CSV format"""
    from .utils.export import export_stream_csv as _export_stream_csv
    return _export_stream_csv(stream_states)

def add_custom_rule(model, rule_name, rule_definition, rule_type="code"):
    """Add a custom rule from LLM-generated code or DSL"""
    from .core.rule_engine import add_custom_rule as _add_custom_rule
    return _add_custom_rule(model, rule_name, rule_definition, rule_type)

def list_custom_rules():
    """List all custom rules with metadata"""
    from .core.rule_engine import rule_engine
    return rule_engine.list_rules()

def get_system_prompt_docs():
    """Get complete LLM-ABM documentation for system prompts (≤2K tokens)"""
    from .docs import get_system_prompt_docs as _get_docs
    return _get_docs()

def get_rule_reference():
    """Get quick rule reference for LLMs (≤1K tokens)"""
    from .docs import get_rule_reference as _get_ref
    return _get_ref()
