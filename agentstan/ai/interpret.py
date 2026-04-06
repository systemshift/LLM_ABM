"""
AI-powered result interpretation.

Send simulation results to an LLM and get a natural language
explanation of what happened and why.
"""

import json
from typing import Dict, Any, Optional


DEFAULT_MODEL = "gpt-5"


def interpret(
    results: Dict[str, Any],
    analysis: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> str:
    """
    Generate a natural language interpretation of simulation results.

    Args:
        results: Results dict from Simulation.run()
        analysis: Optional analysis dict from agentstan.analysis.analyze_population()
        model: OpenAI model name
        api_key: OpenAI API key (or set OPENAI_API_KEY env var)

    Returns:
        Natural language explanation string.
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key) if api_key else OpenAI()

    summary = results.get("summary", {})
    history = results.get("metrics", {}).get("history", [])

    # Build a compact representation for the LLM
    context = {
        "initial_counts": summary.get("initial_counts", {}),
        "final_counts": summary.get("final_counts", {}),
        "steps": results.get("final_step", 0),
        "duration_seconds": round(results.get("duration", 0), 2),
    }

    # Add population snapshots (sampled to keep token count low)
    if history:
        sample_points = _sample_history(history, max_points=10)
        context["population_snapshots"] = sample_points

    if analysis:
        context["analysis"] = analysis

    prompt = f"""You are analyzing the results of an agent-based model simulation.

Here are the results:
{json.dumps(context, indent=2)}

Write a clear, concise analysis (3-5 sentences) explaining:
1. What happened in the simulation (population trends, key events)
2. Why it happened (based on the dynamics you can infer)
3. Whether the outcome is realistic or surprising

Be specific about numbers and steps. Don't hedge — make direct observations."""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "text"},
    )

    return response.choices[0].message.content.strip()


def _sample_history(history: list, max_points: int = 10) -> list:
    """Sample evenly-spaced points from history to keep tokens low."""
    if len(history) <= max_points:
        return [{"step": h["step"], "counts": h["agent_counts"]} for h in history]

    step = len(history) / max_points
    indices = [int(i * step) for i in range(max_points)]
    indices.append(len(history) - 1)  # always include last

    return [
        {"step": history[i]["step"], "counts": history[i]["agent_counts"]}
        for i in sorted(set(indices))
    ]
