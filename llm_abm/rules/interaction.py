"""
Interaction rule templates - pure functions for agent interactions
"""
import copy
import random

def predator_prey(model, params):
    """
    Handle predator-prey interactions with energy transfer
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - predator: Predator agent type
            - prey: Prey agent type
            - success_rate: Probability of successful predation (default: 0.8)
            - energy_gain: Energy gained by predator (default: prey's energy)
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    predator_type = params.get("predator")
    prey_type = params.get("prey")
    success_rate = params.get("success_rate", 0.8)
    
    if not predator_type or not prey_type:
        return new_model
    
    from ..core.agent import get_agents_at_position
    
    # Find all predators
    predators = [agent for agent in new_model["agents"] 
                if agent["type"] == predator_type and agent["alive"]]
    
    for predator in predators:
        # Find prey at same position
        prey_at_position = [agent for agent in new_model["agents"]
                           if (agent["type"] == prey_type and 
                               agent["alive"] and
                               agent["position"]["x"] == predator["position"]["x"] and
                               agent["position"]["y"] == predator["position"]["y"])]
        
        if prey_at_position:
            # Attempt predation on random prey
            prey = random.choice(prey_at_position)
            
            if random.random() < success_rate:
                # Successful predation
                energy_gain = params.get("energy_gain", prey["energy"])
                predator["energy"] += energy_gain
                prey["alive"] = False
    
    return new_model

def competition(model, params):
    """
    Handle resource competition between agents
    
    Args:
        model: Model dictionary
        params: Rule parameters
            - species: List of competing species
            - resource: Resource being competed for
            - energy_per_resource: Energy gained per resource unit
            
    Returns:
        model: Updated model dictionary
    """
    new_model = copy.deepcopy(model)
    species_list = params.get("species", [])
    energy_per_resource = params.get("energy_per_resource", 5)
    
    if not species_list:
        return new_model
    
    # Group agents by position
    position_agents = {}
    for agent in new_model["agents"]:
        if agent["type"] in species_list and agent["alive"]:
            pos_key = (agent["position"]["x"], agent["position"]["y"])
            if pos_key not in position_agents:
                position_agents[pos_key] = []
            position_agents[pos_key].append(agent)
    
    # Handle competition at each position
    for position, agents in position_agents.items():
        if len(agents) > 1:
            # Competition - split resources
            energy_each = energy_per_resource // len(agents)
            for agent in agents:
                agent["energy"] += energy_each
        elif len(agents) == 1:
            # No competition - full resources
            agents[0]["energy"] += energy_per_resource
    
    return new_model
