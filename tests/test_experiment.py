"""Tests for the experiment module."""
from agentstan.experiment import batch_run, sweep

SPEC = {
    "environment": {"type": "grid_2d", "dimensions": {"width": 10, "height": 10}},
    "agent_types": {
        "dot": {
            "initial_count": 10,
            "initial_state": {"energy": 15},
            "behavior_code": (
                "def dot_behavior(agent, model, agents_nearby):\n"
                "    actions = []\n"
                "    actions.append({'type': 'move_random'})\n"
                "    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -0.5})\n"
                "    if agent['energy'] <= 0:\n"
                "        actions.append({'type': 'die', 'cause': 'starvation'})\n"
                "    return actions\n"
            ),
        }
    },
}


def test_batch_run_basic():
    results = batch_run(SPEC, n_runs=3, steps=10, max_workers=2)
    assert len(results) == 3
    assert all("summary" in r for r in results)
    assert all("run_id" in r for r in results)


def test_batch_run_with_vary():
    results = batch_run(
        SPEC,
        n_runs=2,
        steps=10,
        vary={"agent_types.dot.initial_count": [5, 10]},
        max_workers=2,
    )
    # 2 values x 2 runs = 4 total
    assert len(results) == 4


def test_sweep():
    results = sweep(
        SPEC,
        param="agent_types.dot.initial_count",
        values=[5, 10, 15],
        steps=10,
        n_runs=2,
        max_workers=2,
    )
    assert set(results.keys()) == {5, 10, 15}
    assert all(len(runs) == 2 for runs in results.values())
