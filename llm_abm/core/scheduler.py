"""
Step execution framework - coordinates rule execution
"""
import copy

def execute_step(model):
    """
    Execute all rules for one simulation step
    
    Args:
        model: Model dictionary
        
    Returns:
        model: Updated model dictionary
    """
    current_model = model
    
    # Execute each rule in order
    for rule in current_model["rules"]:
        rule_name = rule["name"]
        rule_params = rule["params"]
        
        # Import and execute the appropriate rule function
        current_model = execute_rule(current_model, rule_name, rule_params)
    
    return current_model

def execute_rule(model, rule_name, params):
    """
    Execute a specific rule (built-in or custom)
    
    Args:
        model: Model dictionary
        rule_name: Name of rule to execute
        params: Rule parameters
        
    Returns:
        model: Updated model dictionary
    """
    # Import rule functions dynamically
    from ..rules.movement import random_movement, directed_movement, flocking
    from ..rules.interaction import predator_prey
    from ..rules.lifecycle import energy_decay, reproduction, death
    from .rule_engine import rule_engine, execute_custom_rule
    
    # Built-in rule dispatch table
    built_in_rules = {
        "random_movement": random_movement,
        "directed_movement": directed_movement,
        "flocking": flocking,
        "predator_prey": predator_prey,
        "energy_decay": energy_decay,
        "reproduction": reproduction,
        "death": death
    }
    
    # Check if it's a built-in rule
    if rule_name in built_in_rules:
        rule_function = built_in_rules[rule_name]
        return rule_function(model, params)
    
    # Check if it's a custom rule
    try:
        return execute_custom_rule(model, rule_name, params)
    except ValueError:
        pass
    
    # Rule not found
    available_rules = list(built_in_rules.keys()) + list(rule_engine.list_rules().keys())
    raise ValueError(f"Unknown rule: {rule_name}. Available rules: {available_rules}")
