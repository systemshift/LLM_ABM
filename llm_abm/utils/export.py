"""
Data export utilities
"""
import json

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
