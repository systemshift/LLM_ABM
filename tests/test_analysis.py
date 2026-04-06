"""Tests for the analysis module."""
from agentstan import Simulation
from agentstan.analysis import analyze_population, analyze_events


SPEC = {
    "environment": {"type": "grid_2d", "dimensions": {"width": 15, "height": 15}},
    "agent_types": {
        "rabbit": {
            "initial_count": 20,
            "initial_state": {"energy": 25, "perception_radius": 4},
            "behavior_code": (
                "def rabbit_behavior(agent, model, agents_nearby):\n"
                "    actions = []\n"
                "    energy = agent['energy']\n"
                "    if energy < 20:\n"
                "        actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': 1.5})\n"
                "    actions.append({'type': 'move_random'})\n"
                "    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -0.8})\n"
                "    if energy > 30 and random.random() < 0.05:\n"
                "        actions.append({'type': 'reproduce', 'energy_cost': 12, 'offspring_count': 1})\n"
                "    if energy <= 0:\n"
                "        actions.append({'type': 'die', 'cause': 'starvation'})\n"
                "    return actions\n"
            ),
        },
    },
}


def test_population_analysis():
    sim = Simulation(SPEC)
    results = sim.run(50)
    report = analyze_population(results)

    assert "agent_types" in report
    assert "rabbit" in report["agent_types"]
    rabbit = report["agent_types"]["rabbit"]
    assert "initial" in rabbit
    assert "final" in rabbit
    assert "stability" in rabbit
    assert rabbit["stability"] in ("stable", "growing", "declining", "oscillating", "crashed", "insufficient_data")
    assert "overall" in report


def test_event_analysis():
    sim = Simulation(SPEC)
    results = sim.run(50)
    report = analyze_events(results)

    assert "total_events" in report
    assert report["total_events"] >= 0
    assert "deaths" in report
    assert "births" in report
