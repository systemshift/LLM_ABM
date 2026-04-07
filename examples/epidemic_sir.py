"""
SIR Epidemic Model

Agents are Susceptible, Infected, or Recovered. Infected agents spread
the disease to nearby susceptible agents with some probability. After
an infection period, agents recover and become immune.

Shows classic epidemic curves: exponential growth, peak, decline as
herd immunity builds. Try varying infection_rate and recovery_time.
"""

from agentstan import Simulation, DataCollector
from agentstan.experiment import sweep

susceptible_code = """
def susceptible_behavior(agent, model, agents_nearby):
    actions = []

    # Check if any nearby agent is infected
    infected_nearby = [a for a in agents_nearby if a.type == 'infected' and a.alive]
    if infected_nearby:
        # Chance of getting infected per infected neighbor
        for inf in infected_nearby:
            if random.random() < 0.15:  # infection probability
                # Become infected: die as susceptible, new infected agent spawns
                # We use modify_state to flag ourselves, handled by global check
                actions.append({'type': 'modify_state', 'attribute': '_become_infected', 'value': True})
                break

    actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})
    return actions
"""

infected_code = """
def infected_behavior(agent, model, agents_nearby):
    actions = []

    # Track infection duration
    days_infected = agent.get_attribute('days_infected', 0)
    actions.append({'type': 'modify_state', 'attribute': 'days_infected', 'delta': 1})

    # Recover after recovery_time steps
    if days_infected >= agent.get_attribute('recovery_time', 14):
        actions.append({'type': 'modify_state', 'attribute': '_become_recovered', 'value': True})

    # Move (infected agents move slower)
    if random.random() < 0.5:
        actions.append({'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]})

    return actions
"""

recovered_code = """
def recovered_behavior(agent, model, agents_nearby):
    # Recovered agents are immune, just wander
    return [{'type': 'move', 'direction': [random.choice([-1,0,1]), random.choice([-1,0,1])]}]
"""

spec = {
    "environment": {
        "type": "grid_2d",
        "dimensions": {"width": 30, "height": 30, "topology": "torus"},
    },
    "agent_types": {
        "susceptible": {
            "initial_count": 290,
            "initial_state": {"perception_radius": 2},
            "behavior_code": susceptible_code,
        },
        "infected": {
            "initial_count": 10,
            "initial_state": {"perception_radius": 2, "days_infected": 0, "recovery_time": 14},
            "behavior_code": infected_code,
        },
        "recovered": {
            "initial_count": 0,
            "initial_state": {"perception_radius": 2},
            "behavior_code": recovered_code,
        },
    },
}


class SIRTransitionCollector:
    """
    Custom collector that handles SIR state transitions.

    Agents flag themselves with _become_infected or _become_recovered.
    This collector processes those flags and creates new agents of the
    appropriate type, removing the old ones.
    """

    def __init__(self):
        self.model_data = []

    def collect(self, simulation):
        to_infect = []
        to_recover = []

        for agent in simulation.agent_manager.get_living_agents():
            if agent.get_attribute("_become_infected"):
                to_infect.append(agent)
            if agent.get_attribute("_become_recovered"):
                to_recover.append(agent)

        from agentstan.core.agent import Agent

        for agent in to_infect:
            # Create infected agent at same position
            new_agent = Agent(
                agent_type="infected",
                initial_state={
                    "position": agent.get_attribute("position"),
                    "perception_radius": 2,
                    "days_infected": 0,
                    "recovery_time": 14,
                },
                behavior_function=simulation._compile_behavior_function("infected", infected_code),
            )
            simulation.agent_manager.add_agent(new_agent)
            agent.kill()

        for agent in to_recover:
            new_agent = Agent(
                agent_type="recovered",
                initial_state={
                    "position": agent.get_attribute("position"),
                    "perception_radius": 2,
                },
                behavior_function=simulation._compile_behavior_function("recovered", recovered_code),
            )
            simulation.agent_manager.add_agent(new_agent)
            agent.kill()

        # Record SIR counts
        counts = simulation.agent_manager.get_counts()
        self.model_data.append({
            "step": simulation.step,
            "S": counts.get("susceptible", 0),
            "I": counts.get("infected", 0),
            "R": counts.get("recovered", 0),
        })

    def get_model_data(self):
        return self.model_data


def run_single():
    print("=== SIR Epidemic Model ===")
    print("300 agents (290 susceptible, 10 infected)")
    print("Infection rate: 15% per contact, Recovery: 14 steps")
    print()

    sim = Simulation(spec)
    sir_collector = SIRTransitionCollector()
    sim.add_collector(sir_collector)
    results = sim.run(100)

    data = sir_collector.get_model_data()

    # Find peak infection
    peak_infected = max(data, key=lambda d: d["I"])

    print(f"Peak infection: {peak_infected['I']} at step {peak_infected['step']}")
    print(f"Final: S={data[-1]['S']}, I={data[-1]['I']}, R={data[-1]['R']}")
    print(f"Attack rate: {data[-1]['R'] / 300:.0%} infected over the epidemic")
    print()

    # Print SIR curve
    print("SIR Curve:")
    for i in range(0, len(data), 5):
        d = data[i]
        s_bar = "S" * (d["S"] // 10)
        i_bar = "I" * (d["I"] // 5)
        r_bar = "R" * (d["R"] // 10)
        print(f"  Step {d['step']:3d}: {s_bar}|{i_bar}|{r_bar}  (S={d['S']} I={d['I']} R={d['R']})")


if __name__ == "__main__":
    run_single()
