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

def flocking(model, params):
    """
    Implement flocking behavior (alignment, cohesion, separation)
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - species: Agent type that flocks
            - radius: Vision radius for flocking (default: 3)
            - alignment_weight: Weight for alignment behavior (default: 1.0)
            - cohesion_weight: Weight for cohesion behavior (default: 1.0)
            - separation_weight: Weight for separation behavior (default: 1.5)
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    species = params.get("species")
    radius = params.get("radius", 3)
    alignment_weight = params.get("alignment_weight", 1.0)
    cohesion_weight = params.get("cohesion_weight", 1.0)
    separation_weight = params.get("separation_weight", 1.5)
    
    if not species:
        return new_model
    
    from ..core.grid import distance, get_adjacent_positions
    import random
    
    # Get all flocking agents
    flocking_agents = [agent for agent in new_model["agents"]
                      if agent["type"] == species and agent["alive"]]
    
    for agent in flocking_agents:
        # Find neighbors within radius
        neighbors = []
        for other in flocking_agents:
            if other["id"] != agent["id"]:
                dist = distance(agent["position"], other["position"], new_model["grid"])
                if dist <= radius:
                    neighbors.append(other)
        
        if not neighbors:
            # No neighbors - random movement
            adjacent = get_adjacent_positions(agent["position"], new_model["grid"])
            if adjacent:
                agent["position"] = random.choice(adjacent)
            continue
        
        # Calculate flocking forces
        alignment_x = alignment_y = 0
        cohesion_x = cohesion_y = 0
        separation_x = separation_y = 0
        
        # Cohesion: move toward center of neighbors
        for neighbor in neighbors:
            cohesion_x += neighbor["position"]["x"]
            cohesion_y += neighbor["position"]["y"]
        
        cohesion_x = cohesion_x / len(neighbors) - agent["position"]["x"]
        cohesion_y = cohesion_y / len(neighbors) - agent["position"]["y"]
        
        # Separation: move away from close neighbors
        for neighbor in neighbors:
            dx = agent["position"]["x"] - neighbor["position"]["x"]
            dy = agent["position"]["y"] - neighbor["position"]["y"]
            dist = distance(agent["position"], neighbor["position"], new_model["grid"])
            if dist > 0:
                separation_x += dx / dist
                separation_y += dy / dist
        
        # Combine forces
        total_x = (cohesion_x * cohesion_weight + 
                  separation_x * separation_weight)
        total_y = (cohesion_y * cohesion_weight + 
                  separation_y * separation_weight)
        
        # Choose best adjacent position based on forces
        adjacent = get_adjacent_positions(agent["position"], new_model["grid"])
        if adjacent:
            best_pos = agent["position"]
            best_score = float('-inf')
            
            for pos in adjacent:
                # Score based on alignment with desired direction
                score = (pos["x"] - agent["position"]["x"]) * total_x + \
                       (pos["y"] - agent["position"]["y"]) * total_y
                if score > best_score:
                    best_score = score
                    best_pos = pos
            
            agent["position"] = best_pos
    
    return new_model
