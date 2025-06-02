"""
Data export utilities
"""
import json
import time
import copy

def export(results, format="json"):
    """
    Export simulation results in various formats
    
    Args:
        results: Results dictionary from run() function
        format: Export format ("json", "csv", "summary")
        
    Returns:
        data: Exported data in requested format
    """
    if format == "json":
        return export_json(results)
    elif format == "csv":
        return export_csv(results)
    elif format == "summary":
        return export_summary(results)
    else:
        raise ValueError(f"Unknown export format: {format}")

def export_json(results):
    """
    Export complete results as JSON
    
    Args:
        results: Results dictionary
        
    Returns:
        json_str: JSON string of results
    """
    # Create serializable copy
    export_data = {
        "final_step": results["final_step"],
        "summary": results["summary"],
        "metrics": results["metrics"],
        "final_agents": [
            {
                "id": agent["id"],
                "type": agent["type"],
                "position": agent["position"],
                "energy": agent["energy"],
                "age": agent["age"],
                "alive": agent["alive"]
            }
            for agent in results["model"]["agents"]
        ]
    }
    
    return json.dumps(export_data, indent=2)

def export_csv(results):
    """
    Export time series data as CSV
    
    Args:
        results: Results dictionary
        
    Returns:
        csv_str: CSV string of time series data
    """
    history = results["metrics"]["history"]
    
    if not history:
        return "step,total_agents\n"
    
    # Get all agent types
    all_types = set()
    for step_data in history:
        all_types.update(step_data["agent_counts"].keys())
    
    all_types = sorted(all_types)
    
    # Create header
    header = ["step", "total_agents"] + all_types
    csv_lines = [",".join(header)]
    
    # Add data rows
    for step_data in history:
        row = [
            str(step_data["step"]),
            str(step_data["total_agents"])
        ]
        
        for agent_type in all_types:
            count = step_data["agent_counts"].get(agent_type, 0)
            row.append(str(count))
        
        csv_lines.append(",".join(row))
    
    return "\n".join(csv_lines)

def export_summary(results):
    """
    Export human-readable summary
    
    Args:
        results: Results dictionary
        
    Returns:
        summary_str: Human-readable summary
    """
    summary = results["summary"]
    
    summary_text = f"""
Simulation Summary
=================

Initial Setup:
- Total agents: {summary['initial_agents']}
- Steps completed: {summary['steps_completed']}

Final Results:
- Total agents: {summary['final_agents']}
- Final counts: {summary['final_counts']}

Population Change:
- Net change: {summary['final_agents'] - summary['initial_agents']}
- Survival rate: {summary['final_agents'] / summary['initial_agents'] * 100:.1f}%

Agent Type Details:
"""
    
    for agent_type, count in summary['final_counts'].items():
        summary_text += f"- {agent_type}: {count} agents\n"
    
    return summary_text.strip()

def run_stream(model, steps=100, delay=0.1, callback=None):
    """
    Run simulation with streaming output and time control
    
    Args:
        model: Model dictionary
        steps: Number of steps to run
        delay: Delay between steps in seconds (controls speed)
        callback: Optional function called after each step with current state
        
    Yields:
        state: Dictionary with current simulation state after each step
    """
    from ..core.model import step
    
    current_model = copy.deepcopy(model)
    
    for step_num in range(steps):
        # Execute one simulation step
        current_model = step(current_model)
        
        # Create state snapshot
        alive_agents = [agent for agent in current_model["agents"] if agent["alive"]]
        
        state = {
            "step": current_model["step"],
            "timestamp": time.time(),
            "total_agents": len(alive_agents),
            "agent_counts": {},
            "agents": [
                {
                    "id": agent["id"],
                    "type": agent["type"],
                    "position": agent["position"],
                    "energy": agent["energy"],
                    "age": agent["age"],
                    "alive": agent["alive"]
                }
                for agent in current_model["agents"]
            ],
            "grid": current_model["grid"],
            "rules": current_model["rules"]
        }
        
        # Calculate agent counts by type
        for agent in alive_agents:
            agent_type = agent["type"]
            state["agent_counts"][agent_type] = state["agent_counts"].get(agent_type, 0) + 1
        
        # Call callback if provided
        if callback:
            callback(state)
        
        # Yield current state
        yield state
        
        # Check if simulation should stop (no agents left)
        if len(alive_agents) == 0:
            break
        
        # Add delay for time control
        if delay > 0:
            time.sleep(delay)

def export_stream_json(stream_states):
    """
    Convert stream states to JSON format
    
    Args:
        stream_states: List of state dictionaries from run_stream
        
    Returns:
        json_str: JSON string of streaming data
    """
    return json.dumps(stream_states, indent=2)

def export_stream_csv(stream_states):
    """
    Convert stream states to CSV format
    
    Args:
        stream_states: List of state dictionaries from run_stream
        
    Returns:
        csv_str: CSV string of streaming time series data
    """
    if not stream_states:
        return "step,timestamp,total_agents\n"
    
    # Get all agent types from all states
    all_types = set()
    for state in stream_states:
        all_types.update(state["agent_counts"].keys())
    
    all_types = sorted(all_types)
    
    # Create header
    header = ["step", "timestamp", "total_agents"] + all_types
    csv_lines = [",".join(header)]
    
    # Add data rows
    for state in stream_states:
        row = [
            str(state["step"]),
            str(state["timestamp"]),
            str(state["total_agents"])
        ]
        
        for agent_type in all_types:
            count = state["agent_counts"].get(agent_type, 0)
            row.append(str(count))
        
        csv_lines.append(",".join(row))
    
    return "\n".join(csv_lines)
