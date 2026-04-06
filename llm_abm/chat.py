"""
Chat-to-ABM: Send natural language to an LLM, get back a running simulation.
"""

import json
import re
from typing import Dict, Any, Optional

from .prompt import get_system_prompt
from .core.simulation import Simulation


DEFAULT_MODEL = "gpt-5"


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON from LLM response, handling markdown fences and preamble."""
    # Strip markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        text = re.sub(r"^```\w*\n?", "", text)
        # Remove closing fence
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    # Look for first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(
        f"Could not parse JSON from LLM response. Response starts with: {text[:200]}"
    )


def _spec_from_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize LLM response into a valid simulation specification."""
    # The LLM response should already be close to our spec format.
    # Normalize any variations.
    spec = {}

    # Metadata
    spec["metadata"] = {
        "name": data.get("name", data.get("metadata", {}).get("name", "Simulation")),
        "description": data.get("description", data.get("metadata", {}).get("description", "")),
    }

    # Environment
    if "environment" in data:
        spec["environment"] = data["environment"]
    else:
        spec["environment"] = {
            "type": "grid_2d",
            "dimensions": {"width": 40, "height": 40, "topology": "torus"},
        }

    # Ensure environment has required fields
    env = spec["environment"]
    if "type" not in env:
        env["type"] = "grid_2d"
    if "dimensions" not in env:
        env["dimensions"] = {"width": 40, "height": 40}

    # Agent types
    if "agent_types" in data:
        spec["agent_types"] = data["agent_types"]
    elif "agents" in data:
        spec["agent_types"] = data["agents"]
    else:
        raise ValueError("LLM response missing 'agent_types' or 'agents' field")

    # Validate each agent type has required fields
    for agent_type, type_spec in spec["agent_types"].items():
        if "initial_count" not in type_spec:
            type_spec["initial_count"] = 10
        if "initial_state" not in type_spec:
            type_spec["initial_state"] = {"energy": 20}
        if "behavior_code" not in type_spec:
            raise ValueError(f"Agent type '{agent_type}' missing behavior_code")

    return spec


def generate(
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Send a natural language prompt to an LLM and get back a simulation spec.

    Args:
        user_prompt: Natural language description of the desired simulation
        model: OpenAI model name (default: gpt-5)
        api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        base_url: Optional API base URL for compatible endpoints
        temperature: Sampling temperature

    Returns:
        Parsed simulation specification dict ready for create_simulation()
    """
    from openai import OpenAI

    client_kwargs = {}
    if api_key:
        client_kwargs["api_key"] = api_key
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = _extract_json(raw)
    return _spec_from_response(data)


def run_chat(
    user_prompt: str,
    steps: Optional[int] = None,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    End-to-end: natural language -> simulation spec -> run simulation -> results.

    Args:
        user_prompt: What to simulate
        steps: Override step count (default: use LLM's suggestion or 200)
        model: OpenAI model name
        api_key: OpenAI API key
        base_url: Optional API base URL
        temperature: Sampling temperature
        verbose: Print progress info

    Returns:
        Simulation results dict
    """
    if verbose:
        print(f"Generating simulation from: \"{user_prompt}\"")
        print(f"Using model: {model}")

    spec = generate(
        user_prompt,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
    )

    if verbose:
        name = spec.get("metadata", {}).get("name", "Unnamed")
        agent_types = list(spec.get("agent_types", {}).keys())
        total = sum(
            t.get("initial_count", 0)
            for t in spec.get("agent_types", {}).values()
        )
        print(f"Created: {name}")
        print(f"Agents: {agent_types} ({total} total)")

    # Determine steps
    run_steps = steps or spec.get("metadata", {}).get("steps", 200)
    # Also check top-level steps field from LLM
    if steps is None and "steps" in spec:
        run_steps = spec.pop("steps")

    sim = Simulation(spec)

    if verbose:
        print(f"Running {run_steps} steps...")

    results = sim.run(run_steps)

    if verbose:
        summary = results.get("summary", {})
        print(f"Done. Final population: {summary.get('final_counts', {})}")

    return results


class ChatSession:
    """
    Multi-turn chat session for iterating on simulations.

    Keeps conversation history so the LLM can refine simulations
    based on feedback.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.messages = [
            {"role": "system", "content": get_system_prompt()}
        ]
        self.last_spec = None
        self.last_results = None

    def send(self, message: str, run: bool = True, steps: Optional[int] = None) -> Dict[str, Any]:
        """
        Send a message and optionally run the resulting simulation.

        Args:
            message: User message (description or refinement)
            run: Whether to run the simulation (default True)
            steps: Override step count

        Returns:
            If run=True: simulation results
            If run=False: parsed specification
        """
        from openai import OpenAI

        self.messages.append({"role": "user", "content": message})

        client_kwargs = {}
        if self.api_key:
            client_kwargs["api_key"] = self.api_key
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": raw})

        data = _extract_json(raw)
        self.last_spec = _spec_from_response(data)

        if not run:
            return self.last_spec

        run_steps = steps or self.last_spec.get("metadata", {}).get("steps", 200)
        if steps is None and "steps" in data:
            run_steps = data["steps"]

        sim = Simulation(self.last_spec)
        self.last_results = sim.run(run_steps)

        # Add results context for next turn
        summary = self.last_results.get("summary", {})
        self.messages.append({
            "role": "user",
            "content": f"[System: Simulation completed. Results: {json.dumps(summary)}. "
                       f"If I ask for changes, update the full spec JSON.]"
        })

        return self.last_results

    def reset(self):
        """Reset conversation history."""
        self.messages = [
            {"role": "system", "content": get_system_prompt()}
        ]
        self.last_spec = None
        self.last_results = None
