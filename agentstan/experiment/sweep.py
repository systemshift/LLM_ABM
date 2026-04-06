"""
Parameter sweep: vary one parameter, run multiple times per value.
"""

from typing import Dict, Any, List
from .batch import batch_run


def sweep(
    spec: Dict[str, Any],
    param: str,
    values: list,
    steps: int = 200,
    n_runs: int = 10,
    max_workers: int = 4,
) -> Dict[Any, List[Dict[str, Any]]]:
    """
    Sweep a single parameter across values with replications.

    Args:
        spec: Base simulation specification.
        param: Dot-path to the parameter (e.g. "agent_types.wolf.initial_count").
        values: List of values to try.
        steps: Steps per run.
        n_runs: Replications per value.
        max_workers: Parallel threads.

    Returns:
        Dict mapping each value to a list of run results.

    Example:
        results = sweep(spec, "agent_types.wolf.initial_count",
                        values=[5, 10, 15, 20], n_runs=10)
        for val, runs in results.items():
            avg_wolves = sum(r["summary"]["final_counts"].get("wolf", 0) for r in runs) / len(runs)
            print(f"wolves={val}: avg final = {avg_wolves:.1f}")
    """
    all_results = batch_run(
        spec,
        n_runs=n_runs,
        steps=steps,
        vary={param: list(values)},
        max_workers=max_workers,
    )

    # Group by parameter value
    grouped: Dict[Any, List[Dict[str, Any]]] = {}
    for result in all_results:
        val = result["params"].get(param)
        if val not in grouped:
            grouped[val] = []
        grouped[val].append(result)

    return grouped
