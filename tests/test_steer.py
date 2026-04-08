"""Tests for AI Steerer (mocked LLM, no real API calls)."""
import json
from unittest.mock import patch, MagicMock
from agentstan import Simulation
from agentstan.ai.steer import Steerer, STEERER_SYSTEM_PROMPT

SPEC = {
    "environment": {"type": "grid_2d", "dimensions": {"width": 15, "height": 15}},
    "agent_types": {
        "rabbit": {
            "initial_count": 20,
            "initial_state": {"energy": 25, "perception_radius": 4},
            "behavior_code": "def rabbit_behavior(a,m,n):\n    return [{'type':'move_random'}]",
        },
        "wolf": {
            "initial_count": 5,
            "initial_state": {"energy": 40, "perception_radius": 6},
            "behavior_code": "def wolf_behavior(a,m,n):\n    return [{'type':'move_random'}]",
        },
    },
}


def _mock_llm_response(interventions, reasoning="test"):
    """Create a mock OpenAI response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "interventions": interventions,
        "reasoning": reasoning,
    })
    return mock_response


def test_steerer_attaches_correctly():
    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5)
    steerer.attach(sim)

    assert steerer.observer is not None
    assert steerer.intervention_engine is not None
    assert sim.intervention_engine is not None
    assert steerer.observer in sim.collectors


@patch("agentstan.ai.steer.Steerer._call_llm")
def test_steerer_fires_at_correct_frequency(mock_call):
    mock_call.return_value = json.dumps({"interventions": [], "reasoning": "all good"})

    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5)
    steerer.attach(sim)
    sim.run(12)

    # Steps 5 and 10 should trigger checks (12 steps, check every 5)
    assert mock_call.call_count == 2
    assert len(steerer.log) == 2
    assert steerer.log[0]["step"] == 5
    assert steerer.log[1]["step"] == 10


@patch("agentstan.ai.steer.Steerer._call_llm")
def test_steerer_adds_agents(mock_call):
    mock_call.return_value = json.dumps({
        "interventions": [{"action": "add_agents", "agent_type": "wolf", "count": 3}],
        "reasoning": "wolves declining",
    })

    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5)
    steerer.attach(sim)

    initial_wolves = len(sim.agent_manager.get_agents_by_type("wolf"))
    sim.run(6)  # Run past the check at step 5, interventions applied at step 6

    # 3 wolves should have been added
    current_wolves = len(sim.agent_manager.get_agents_by_type("wolf"))
    assert current_wolves == initial_wolves + 3


@patch("agentstan.ai.steer.Steerer._call_llm")
def test_steerer_removes_agents(mock_call):
    mock_call.return_value = json.dumps({
        "interventions": [{"action": "remove_agents", "agent_type": "rabbit", "count": 5}],
        "reasoning": "too many rabbits",
    })

    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5)
    steerer.attach(sim)

    sim.run(6)

    # 5 rabbits should have been removed
    current_rabbits = len(sim.agent_manager.get_agents_by_type("rabbit"))
    assert current_rabbits == 15  # 20 - 5


@patch("agentstan.ai.steer.Steerer._call_llm")
def test_steerer_none_action(mock_call):
    mock_call.return_value = json.dumps({
        "interventions": [{"action": "none"}],
        "reasoning": "everything is fine",
    })

    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5)
    steerer.attach(sim)
    sim.run(6)

    # No interventions applied, but log entry exists
    assert len(steerer.log) == 1
    assert steerer.log[0]["interventions"] == []
    assert steerer.log[0]["reasoning"] == "everything is fine"


@patch("agentstan.ai.steer.Steerer._call_llm")
def test_steerer_log_records_reasoning(mock_call):
    mock_call.return_value = json.dumps({
        "interventions": [{"action": "add_agents", "agent_type": "wolf", "count": 1}],
        "reasoning": "wolf population critically low",
    })

    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5)
    steerer.attach(sim)
    sim.run(6)

    assert steerer.log[0]["reasoning"] == "wolf population critically low"
    assert steerer.log[0]["counts"]["rabbit"] > 0


@patch("agentstan.ai.steer.Steerer._call_llm")
def test_steerer_respects_max_interventions(mock_call):
    mock_call.return_value = json.dumps({
        "interventions": [
            {"action": "add_agents", "agent_type": "wolf", "count": 1},
            {"action": "add_agents", "agent_type": "wolf", "count": 1},
            {"action": "add_agents", "agent_type": "wolf", "count": 1},
            {"action": "add_agents", "agent_type": "wolf", "count": 1},
            {"action": "add_agents", "agent_type": "wolf", "count": 1},
        ],
        "reasoning": "adding many wolves",
    })

    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5, max_interventions_per_check=3)
    steerer.attach(sim)
    sim.run(6)

    # Only 3 should have been applied (max_interventions=3)
    current_wolves = len(sim.agent_manager.get_agents_by_type("wolf"))
    assert current_wolves == 5 + 3  # initial 5 + max 3


@patch("agentstan.ai.steer.Steerer._call_llm")
def test_steerer_modifies_environment(mock_call):
    mock_call.return_value = json.dumps({
        "interventions": [{"action": "modify_environment", "property": "food_level", "value": 0.5}],
        "reasoning": "reducing food",
    })

    sim = Simulation(SPEC)
    steerer = Steerer(goal="test", check_every=5)
    steerer.attach(sim)
    sim.run(6)

    assert sim.environment.get_property("food_level") == 0.5
