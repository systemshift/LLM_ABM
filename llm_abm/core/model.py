"""
Core model state management - all pure functions with dictionary state
"""
import random
import copy
from ..utils.validation import validate_config
from .grid import create_grid, get_random_position

def create_model(config):
    """
    Create model from simple config dictionary
    
    Args:
        config: Dictionary with grid, agents, and environment settings
        
    Returns:
        model: Dictionary containing complete model state
    """
    # Validate configuration
    validate_config(config)
    
    # Create grid
    grid_config = config["grid"]
    grid = create_grid(
        width=grid_config["width"], 
        height=grid_config["height"],
        topology=grid_config.get("topology", "torus")
    )
    
    # Create agents
    agents = []
    agent_id = 1
    
    for agent_type, agent_config in config["agents"].items():
        count = agent_config["count"]
        
        for _ in range(count):
            # Set default values
            energy = agent_config.get("energy", 20)
            position_type = agent_config.get("position", "random")
            
            # Determine position
            if position_type == "random":
                position = get_random_position(grid)
            elif position_type == "center":
                position = {"x": grid["width"] // 2, "y": grid["height"] // 2}
            else:
                position = get_random_position(grid)  # Default to random
            
            agent = {
                "id": agent_id,
                "type": agent_type,
                "position": position,
                "energy": energy,
                "age": 0,
                "alive": True,
                "properties": agent_config.get("properties", {})
            }
            
            agents.append(agent)
            agent_id += 1
    
    # Create model state
    model = {
        "config": config,
        "agents": agents,
        "grid": grid,
        "rules": [],
        "step": 0,
        "metrics": {
            "total_agents": len(agents),
            "agent_counts": {agent_type: config["agents"][agent_type]["count"] 
                           for agent_type in config["agents"]},
            "history": []
        },
        "environment": config.get("environment", {})
    }
    
    return model

def step(model):
    """
    Advance simulation one step
    
    Args:
        model: Model dictionary
        
    Returns:
        model: Updated model dictionary
    """
    from .scheduler import execute_step
    
    # Create copy to avoid mutation
    new_model = copy.deepcopy(model)
    
    # Execute all rules for this step
    new_model = execute_step(new_model)
    
    # Update step counter
    new_model["step"] += 1
    
    # Update metrics
    alive_agents = [agent for agent in new_model["agents"] if agent["alive"]]
    agent_counts = {}
    for agent in alive_agents:
        agent_type = agent["type"]
        agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1
    
    new_model["metrics"]["total_agents"] = len(alive_agents)
    new_model["metrics"]["agent_counts"] = agent_counts
    
    # Store history snapshot
    step_data = {
        "step": new_model["step"],
        "total_agents": len(alive_agents),
        "agent_counts": agent_counts.copy()
    }
    new_model["metrics"]["history"].append(step_data)
    
    return new_model

def run(model, steps=100):
    """
    Run simulation for multiple steps
    
    Args:
        model: Model dictionary
        steps: Number of steps to run
        
    Returns:
        results: Dictionary with final model state and run data
    """
    current_model = model
    
    for step_num in range(steps):
        current_model = step(current_model)
        
        # Check if simulation should stop (no agents left)
        alive_agents = [agent for agent in current_model["agents"] if agent["alive"]]
        if len(alive_agents) == 0:
            break
    
    results = {
        "model": current_model,
        "final_step": current_model["step"],
        "metrics": current_model["metrics"],
        "summary": {
            "initial_agents": model["metrics"]["total_agents"],
            "final_agents": current_model["metrics"]["total_agents"],
            "steps_completed": current_model["step"],
            "final_counts": current_model["metrics"]["agent_counts"]
        }
    }
    
    return results
