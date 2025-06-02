"""
Lifecycle rule templates - pure functions for birth, death, and aging
"""
import copy
import random

def energy_decay(model, params):
    """
    Reduce agent energy each step
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - species: "all" or specific agent type (default: "all")
            - rate: Energy loss per step (default: 1)
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    species = params.get("species", "all")
    rate = params.get("rate", 1)
    
    for agent in new_model["agents"]:
        if not agent["alive"]:
            continue
            
        # Check if this agent type should lose energy
        if species != "all" and agent["type"] != species:
            continue
        
        # Reduce energy
        agent["energy"] -= rate
        
        # Ensure energy doesn't go below 0
        if agent["energy"] < 0:
            agent["energy"] = 0
    
    return new_model

def reproduction(model, params):
    """
    Spawn new agents when energy threshold is met
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - species: Agent type that reproduces
            - energy_threshold: Minimum energy to reproduce (default: 30)
            - rate: Probability of reproduction (default: 0.1)
            - energy_cost: Energy cost to parent (default: half of threshold)
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    species = params.get("species")
    energy_threshold = params.get("energy_threshold", 30)
    rate = params.get("rate", 0.1)
    energy_cost = params.get("energy_cost", energy_threshold // 2)
    
    if not species:
        return new_model
    
    from ..core.grid import get_random_adjacent
    
    # Find next available ID
    max_id = max([agent["id"] for agent in new_model["agents"]], default=0)
    next_id = max_id + 1
    
    # Find reproducing agents
    reproducing_agents = [agent for agent in new_model["agents"]
                         if (agent["type"] == species and 
                             agent["alive"] and
                             agent["energy"] >= energy_threshold)]
    
    new_agents = []
    for agent in reproducing_agents:
        if random.random() < rate:
            # Create offspring
            offspring_position = get_random_adjacent(agent["position"], new_model["grid"])
            
            offspring = {
                "id": next_id,
                "type": species,
                "position": offspring_position,
                "energy": energy_threshold // 2,  # Start with half threshold energy
                "age": 0,
                "alive": True,
                "properties": agent["properties"].copy()
            }
            
            new_agents.append(offspring)
            next_id += 1
            
            # Reduce parent energy
            agent["energy"] -= energy_cost
    
    # Add new agents to model
    new_model["agents"].extend(new_agents)
    
    return new_model

def death(model, params):
    """
    Handle agent death when energy reaches zero
    
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
            
        # Check if this agent type can die
        if species != "all" and agent["type"] != species:
            continue
        
        # Check death condition
        if agent["energy"] <= 0:
            agent["alive"] = False
    
    return new_model

def aging(model, params):
    """
    Age agents and handle death by old age
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - species: "all" or specific agent type (default: "all")
            - death_age: Age at which agents die (default: 100)
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    species = params.get("species", "all")
    death_age = params.get("death_age", 100)
    
    for agent in new_model["agents"]:
        if not agent["alive"]:
            continue
            
        # Check if this agent type ages
        if species != "all" and agent["type"] != species:
            continue
        
        # Increase age
        agent["age"] += 1
        
        # Check death by old age
        if agent["age"] >= death_age:
            agent["alive"] = False
    
    return new_model
