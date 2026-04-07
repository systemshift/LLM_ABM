"""Tests for observation system."""
from agentstan import Simulation
from agentstan.core.observer import Observer, AgentSnapshot, SimulationSnapshot

SPEC = {
    "environment": {"type": "grid_2d", "dimensions": {"width": 15, "height": 15}},
    "agent_types": {
        "rabbit": {
            "initial_count": 10,
            "initial_state": {"energy": 20, "perception_radius": 5},
            "behavior_code": "def rabbit_behavior(a,m,n):\n    return [{'type':'move_random'}]",
        }
    },
}


def test_observer_collects_snapshots():
    sim = Simulation(SPEC)
    observer = Observer(every_n_steps=1)
    sim.add_observer(observer)
    sim.run(5)

    assert len(observer.history) == 5
    snap = observer.history[0]
    assert snap.step == 1
    assert len(snap.agents) == 10
    assert "rabbit" in snap.counts


def test_agent_snapshot_has_state():
    sim = Simulation(SPEC)
    observer = Observer()
    sim.add_observer(observer)
    sim.run(1)

    snap = observer.get_latest()
    agent_snap = list(snap.agents.values())[0]
    assert agent_snap.agent_type == "rabbit"
    assert agent_snap.position is not None
    assert "energy" in agent_snap.state
    assert isinstance(agent_snap.narrative, str)
    assert "rabbit" in agent_snap.narrative


def test_observer_watches_specific_type():
    spec = {
        "environment": {"type": "grid_2d", "dimensions": {"width": 10, "height": 10}},
        "agent_types": {
            "rabbit": {"initial_count": 5, "initial_state": {"energy": 20},
                       "behavior_code": "def rabbit_behavior(a,m,n):\n    return []"},
            "wolf": {"initial_count": 3, "initial_state": {"energy": 30},
                     "behavior_code": "def wolf_behavior(a,m,n):\n    return []"},
        },
    }
    sim = Simulation(spec)
    observer = Observer(watch_types=["wolf"])
    sim.add_observer(observer)
    sim.run(1)

    snap = observer.get_latest()
    assert all(a.agent_type == "wolf" for a in snap.agents.values())
    assert len(snap.agents) == 3


def test_observer_callback_fires():
    sim = Simulation(SPEC)
    observer = Observer()
    snapshots_received = []
    observer.on_snapshot(lambda s: snapshots_received.append(s))
    sim.add_observer(observer)
    sim.run(3)

    assert len(snapshots_received) == 3


def test_agent_history():
    sim = Simulation(SPEC)
    observer = Observer()
    sim.add_observer(observer)
    sim.run(5)

    # Get first agent's ID
    first_id = list(observer.history[0].agents.keys())[0]
    history = observer.get_agent_history(first_id)
    assert len(history) == 5
    assert all(h.agent_id == first_id for h in history)


def test_snapshot_to_dict():
    sim = Simulation(SPEC)
    observer = Observer()
    sim.add_observer(observer)
    sim.run(1)

    snap = observer.get_latest()
    d = snap.to_dict()
    assert "step" in d
    assert "agents" in d
    assert "counts" in d
