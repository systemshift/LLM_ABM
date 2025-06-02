"""
Agent management and rule addition
"""
import copy

def add_rule(model, rule_name, params=None):
    """
    Add behavioral rule to model
    
    Args:
        model: Model dictionary
        rule_name: Name of rule to add
        params: Rule parameters dictionary
        
    Returns:
        model: Updated model dictionary with new rule
    """
    if params is None:
        params = {}
    
    # Create copy to avoid mutation
    new_model = copy.deepcopy(model)
    
    # Validate rule name (check both built-in and custom rules)
    built_in_rules = {
        "random_movement", "predator_prey", "energy_decay", 
        "reproduction", "death"
    }
    
    # Import rule engine to check for custom rules
    from .rule_engine import rule_engine
    custom_rules = set(rule_engine.list_rules().keys())
    valid_rules = built_in_rules | custom_rules
    
    if rule_name not in valid_rules:
        raise ValueError(f"Unknown rule: {rule_name}. Available rules: {valid_rules}")
    
    # Create rule entry
    rule = {
        "name": rule_name,
        "params": params
    }
    
    # Add rule to model
    new_model["rules"].append(rule)
    
    return new_model

def get_agents_by_type(model, agent_type):
    """
    Get all living agents of specific type
    
    Args:
        model: Model dictionary
        agent_type: Type of agent to filter for
        
    Returns:
        agents: List of agent dictionaries
    """
    return [agent for agent in model["agents"] 
            if agent["type"] == agent_type and agent["alive"]]

def get_agents_at_position(model, position):
    """
    Get all living agents at specific position
    
    Args:
        model: Model dictionary
        position: Position dictionary with x, y
        
    Returns:
        agents: List of agent dictionaries
    """
    return [agent for agent in model["agents"]
            if (agent["position"]["x"] == position["x"] and 
                agent["position"]["y"] == position["y"] and 
                agent["alive"])]

def find_nearest_agent(model, agent, target_type):
    """
    Find nearest agent of target type
    
    Args:
        model: Model dictionary
        agent: Source agent dictionary
        target_type: Type of target agent
        
    Returns:
        agent: Nearest target agent or None
    """
    from .grid import distance
    
    targets = get_agents_by_type(model, target_type)
    if not targets:
        return None
    
    nearest = None
    min_distance = float('inf')
    
    for target in targets:
        dist = distance(agent["position"], target["position"], model["grid"])
        if dist < min_distance:
            min_distance = dist
            nearest = target
    
    return nearest
