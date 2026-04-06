"""Test the refactored LLM-ABM package."""
import json
import llm_abm
from llm_abm.chat import _extract_json, _spec_from_response
from llm_abm.core.agent_system import Agent


def test_agent_dict_access():
    """Agent supports both dict-style and method-style access."""
    agent = Agent("rabbit", {"energy": 25, "position": (5, 5)})

    # Dict style
    assert agent["energy"] == 25
    agent["energy"] = 30
    assert agent["energy"] == 30
    assert "energy" in agent

    # Method style still works
    assert agent.get_attribute("energy") == 30
    agent.set_attribute("energy", 20)
    assert agent["energy"] == 20

    print("  PASS: Agent dict access")


def test_json_extraction():
    """JSON extraction handles various LLM response formats."""
    # Clean JSON
    raw = '{"name": "test", "value": 42}'
    assert _extract_json(raw)["value"] == 42

    # With markdown fences
    raw = '```json\n{"name": "test", "value": 42}\n```'
    assert _extract_json(raw)["value"] == 42

    # With preamble text
    raw = 'Here is the result:\n{"name": "test", "value": 42}'
    assert _extract_json(raw)["value"] == 42

    print("  PASS: JSON extraction")


def test_spec_normalization():
    """Spec normalization handles LLM response variations."""
    # Standard format
    data = {
        "name": "Test",
        "description": "A test",
        "environment": {"type": "grid_2d", "dimensions": {"width": 20, "height": 20}},
        "agent_types": {
            "ant": {
                "initial_count": 10,
                "initial_state": {"energy": 5},
                "behavior_code": "def ant_behavior(a, m, n):\n    return []"
            }
        }
    }
    spec = _spec_from_response(data)
    assert "ant" in spec["agent_types"]
    assert spec["metadata"]["name"] == "Test"

    # 'agents' key instead of 'agent_types'
    data2 = {
        "environment": {"type": "grid_2d", "dimensions": {"width": 20, "height": 20}},
        "agents": {
            "fish": {
                "initial_count": 5,
                "initial_state": {"energy": 10},
                "behavior_code": "def fish_behavior(a, m, n):\n    return []"
            }
        }
    }
    spec2 = _spec_from_response(data2)
    assert "fish" in spec2["agent_types"]

    # Missing initial_count gets default
    data3 = {
        "environment": {"type": "grid_2d", "dimensions": {"width": 20, "height": 20}},
        "agent_types": {
            "bird": {
                "initial_state": {"energy": 10},
                "behavior_code": "def bird_behavior(a, m, n):\n    return []"
            }
        }
    }
    spec3 = _spec_from_response(data3)
    assert spec3["agent_types"]["bird"]["initial_count"] == 10

    print("  PASS: Spec normalization")


def test_simulation_engine():
    """Full simulation runs with dict-style agent access in behavior code."""
    spec = {
        "environment": {
            "type": "grid_2d",
            "dimensions": {"width": 20, "height": 20, "topology": "torus"}
        },
        "agent_types": {
            "rabbit": {
                "initial_count": 30,
                "initial_state": {"energy": 25, "perception_radius": 5},
                "behavior_code": (
                    "def rabbit_behavior(agent, model, agents_nearby):\n"
                    "    actions = []\n"
                    "    energy = agent['energy']\n"
                    "    if energy < 20:\n"
                    "        actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': 2})\n"
                    "    actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})\n"
                    "    if energy > 30 and random.random() < 0.08:\n"
                    "        actions.append({'type': 'reproduce', 'energy_cost': 15, 'offspring_count': 1})\n"
                    "    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -0.8})\n"
                    "    if energy <= 0:\n"
                    "        actions.append({'type': 'die', 'cause': 'starvation'})\n"
                    "    return actions\n"
                )
            },
            "wolf": {
                "initial_count": 5,
                "initial_state": {"energy": 40, "perception_radius": 7},
                "behavior_code": (
                    "def wolf_behavior(agent, model, agents_nearby):\n"
                    "    actions = []\n"
                    "    energy = agent['energy']\n"
                    "    position = agent['position']\n"
                    "    rabbits = [a for a in agents_nearby if a.type == 'rabbit' and a.alive]\n"
                    "    if rabbits:\n"
                    "        r = rabbits[0]\n"
                    "        rpos = r['position']\n"
                    "        if position == rpos:\n"
                    "            actions.append({'type': 'interact', 'target_id': r.id, 'interaction_type': 'predation', 'params': {'success_rate': 0.4, 'energy_gain': 12}})\n"
                    "        else:\n"
                    "            actions.append({'type': 'move_to', 'target': (rpos[0], rpos[1])})\n"
                    "    else:\n"
                    "        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})\n"
                    "    if energy > 50 and random.random() < 0.04:\n"
                    "        actions.append({'type': 'reproduce', 'energy_cost': 20, 'offspring_count': 1})\n"
                    "    actions.append({'type': 'modify_state', 'attribute': 'energy', 'delta': -1.0})\n"
                    "    if energy <= 0:\n"
                    "        actions.append({'type': 'die', 'cause': 'starvation'})\n"
                    "    return actions\n"
                )
            }
        }
    }

    sim = llm_abm.create_simulation(spec)
    results = llm_abm.run(sim, steps=50)

    assert results["final_step"] >= 1
    assert "summary" in results
    assert "final_counts" in results["summary"]

    print(f"  PASS: Simulation engine (final counts: {results['summary']['final_counts']})")


def test_export():
    """Export works."""
    spec = {
        "environment": {"type": "grid_2d", "dimensions": {"width": 10, "height": 10}},
        "agent_types": {
            "dot": {
                "initial_count": 5,
                "initial_state": {"energy": 10},
                "behavior_code": "def dot_behavior(a, m, n):\n    return [{'type': 'move_random'}]"
            }
        }
    }
    sim = llm_abm.create_simulation(spec)
    results = llm_abm.run(sim, steps=5)

    llm_abm.export(results, "/tmp/test_abm_results.json", format="json")
    with open("/tmp/test_abm_results.json") as f:
        loaded = json.load(f)
    assert "summary" in loaded

    print("  PASS: Export")


def test_system_prompt():
    """System prompt is available."""
    prompt = llm_abm.get_system_prompt()
    assert "behavior_code" in prompt
    assert "agent_types" in prompt
    assert len(prompt) > 500

    print(f"  PASS: System prompt ({len(prompt)} chars)")


if __name__ == "__main__":
    print("Testing refactored LLM-ABM...")
    test_agent_dict_access()
    test_json_extraction()
    test_spec_normalization()
    test_simulation_engine()
    test_export()
    test_system_prompt()
    print("\nAll tests passed!")
