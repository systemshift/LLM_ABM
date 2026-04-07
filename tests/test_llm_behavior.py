"""Tests for LLM behavior engine (no real API calls — tests parsing and memory)."""
from agentstan.ai.llm_behavior import parse_llm_actions, build_agent_prompt, _summarize_perception
from agentstan.ai.llm_memory import AgentMemory
from agentstan.ai.llm_budget import LLMBudget
from agentstan.core.agent import Agent


def test_parse_clean_json_array():
    actions = parse_llm_actions('[{"type": "move", "direction": [1, 0]}]')
    assert len(actions) == 1
    assert actions[0]["type"] == "move"


def test_parse_json_object_with_actions_key():
    actions = parse_llm_actions('{"actions": [{"type": "move_random"}]}')
    assert len(actions) == 1
    assert actions[0]["type"] == "move_random"


def test_parse_markdown_fences():
    text = '```json\n{"actions": [{"type": "die", "cause": "test"}]}\n```'
    actions = parse_llm_actions(text)
    assert actions[0]["type"] == "die"


def test_parse_with_preamble():
    text = 'Here are my actions:\n[{"type": "move", "direction": [0, 1]}]'
    actions = parse_llm_actions(text)
    assert actions[0]["type"] == "move"


def test_parse_fallback_on_garbage():
    actions = parse_llm_actions("I don't know what to do!")
    assert actions == [{"type": "move_random"}]


def test_memory_add_and_retrieve():
    mem = AgentMemory(max_entries=5)
    mem.add(1, "saw 2 rabbits", "moved east")
    mem.add(2, "no agents nearby", "moved random")

    recent = mem.get_recent(2)
    assert len(recent) == 2
    assert recent[0]["step"] == 1


def test_memory_compression():
    mem = AgentMemory(max_entries=5, summary_threshold=3)
    for i in range(10):
        mem.add(i, f"obs {i}", f"action {i}")

    # Should have compressed, keeping ~3 recent entries
    assert len(mem.entries) <= 5
    assert mem.summary is not None


def test_memory_to_prompt_text():
    mem = AgentMemory()
    mem.add(1, "saw wolf", "fled south")
    mem.add(2, "no threats", "grazed")

    text = mem.to_prompt_text()
    assert "saw wolf" in text
    assert "fled south" in text


def test_memory_serialization():
    mem = AgentMemory(max_entries=10)
    mem.add(1, "test obs", "test action")
    mem.summary = "earlier stuff"

    d = mem.to_dict()
    restored = AgentMemory.from_dict(d)
    assert len(restored.entries) == 1
    assert restored.summary == "earlier stuff"


def test_budget_enforcement():
    budget = LLMBudget(max_calls_per_step=3, max_calls_total=10)

    assert budget.can_call()
    for _ in range(3):
        budget.record_call(100, 50, "gpt-5", 1)

    assert not budget.can_call()  # per-step limit hit

    budget.reset_step()
    assert budget.can_call()  # per-step reset

    assert budget.calls_total == 3


def test_budget_total_limit():
    budget = LLMBudget(max_calls_total=5)
    for _ in range(5):
        budget.record_call(10, 5, "gpt-5", 1)

    assert budget.exhausted
    assert not budget.can_call()


def test_build_prompt():
    agent = Agent("wolf", {"energy": 30, "position": (5, 5), "perception_radius": 7})
    sim_state = {"step": 10, "environment": {}, "agent_counts": {"wolf": 3, "rabbit": 20}}
    memory = AgentMemory()

    nearby_agent = Agent("rabbit", {"energy": 15, "position": (6, 5)})

    prompt = build_agent_prompt(
        agent, sim_state, [nearby_agent], memory,
        personality="patient hunter",
        goals="hunt rabbits",
    )

    assert "wolf #" in prompt
    assert "patient hunter" in prompt
    assert "hunt rabbits" in prompt
    assert "energy=30" in prompt
    assert "rabbit" in prompt
