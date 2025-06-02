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
    Execute a specific rule
    
    Args:
        model: Model dictionary
        rule_name: Name of rule to execute
        params: Rule parameters
        
    Returns:
        model: Updated model dictionary
    """
    # Import rule functions dynamically
    from ..rules.movement import random_movement
    from ..rules.interaction import predator_prey
    from ..rules.lifecycle import energy_decay, reproduction, death
    
    # Rule dispatch table
    rule_functions = {
        "random_movement": random_movement,
        "predator_prey": predator_prey,
        "energy_decay": energy_decay,
        "reproduction": reproduction,
        "death": death
    }
    
    if rule_name not in rule_functions:
        raise ValueError(f"Unknown rule: {rule_name}")
    
    # Execute the rule function
    rule_function = rule_functions[rule_name]
    return rule_function(model, params)
