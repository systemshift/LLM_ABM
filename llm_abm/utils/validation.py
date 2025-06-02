"""
Configuration validation utilities
"""

def validate_config(config):
    """
    Validate model configuration dictionary
    
    Args:
        config: Dictionary with grid, agents, and environment settings
        
    Raises:
        ValueError: If configuration is invalid
        
    Returns:
        bool: True if valid
    """
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary")
    
    # Validate grid configuration
    if "grid" not in config:
        raise ValueError("Config must contain 'grid' section")
    
    grid = config["grid"]
    if not isinstance(grid, dict):
        raise ValueError("Grid must be a dictionary")
    
    if "width" not in grid or "height" not in grid:
        raise ValueError("Grid must have 'width' and 'height'")
    
    if not isinstance(grid["width"], int) or not isinstance(grid["height"], int):
        raise ValueError("Grid width and height must be integers")
    
    if grid["width"] <= 0 or grid["height"] <= 0:
        raise ValueError("Grid width and height must be positive")
    
    # Validate agents configuration
    if "agents" not in config:
        raise ValueError("Config must contain 'agents' section")
    
    agents = config["agents"]
    if not isinstance(agents, dict):
        raise ValueError("Agents must be a dictionary")
    
    if len(agents) == 0:
        raise ValueError("Must define at least one agent type")
    
    for agent_type, agent_config in agents.items():
        if not isinstance(agent_config, dict):
            raise ValueError(f"Agent config for '{agent_type}' must be a dictionary")
        
        if "count" not in agent_config:
            raise ValueError(f"Agent '{agent_type}' must have 'count'")
        
        if not isinstance(agent_config["count"], int) or agent_config["count"] < 0:
            raise ValueError(f"Agent '{agent_type}' count must be non-negative integer")
    
    return True
