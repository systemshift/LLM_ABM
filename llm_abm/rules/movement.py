"""
Movement rule templates - pure functions for agent movement
"""
import copy
from ..core.grid import get_random_adjacent

def random_movement(model, params):
    """
    Move agents randomly to adjacent cells
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - species: "all" or specific agent type (default: "all")
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    species = params.get("species", "all")
    
    for agent in new_model["agents"]:
        if not agent["alive"]:
            continue
            
        # Check if this agent type should move
        if species != "all" and agent["type"] != species:
            continue
        
        # Calculate new position
        new_position = get_random_adjacent(agent["position"], new_model["grid"])
        agent["position"] = new_position
    
    return new_model

def directed_movement(model, params):
    """
    Move agents toward target agent type
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - species: Agent type that moves
            - target: Target agent type to move toward
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    species = params.get("species")
    target_type = params.get("target")
    
    if not species or not target_type:
        return new_model
    
    from ..core.agent import find_nearest_agent
    from ..core.grid import get_adjacent_positions
    
    for agent in new_model["agents"]:
        if not agent["alive"] or agent["type"] != species:
            continue
        
        # Find nearest target
        target = find_nearest_agent(new_model, agent, target_type)
        if not target:
            continue
        
        # Move toward target
        current_pos = agent["position"]
        adjacent_positions = get_adjacent_positions(current_pos, new_model["grid"])
        
        if adjacent_positions:
            # Find adjacent position closest to target
            from ..core.grid import distance
            
            best_pos = current_pos
            min_distance = distance(current_pos, target["position"], new_model["grid"])
            
            for pos in adjacent_positions:
                dist = distance(pos, target["position"], new_model["grid"])
                if dist < min_distance:
                    min_distance = dist
                    best_pos = pos
            
            agent["position"] = best_pos
    
    return new_model
