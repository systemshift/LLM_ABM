"""Tests for network environment topologies and edge support."""
import pytest
from agentstan import Simulation
from agentstan.core.environment import Environment


def test_explicit_edges():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
    )
    assert sorted(env._adjacency[1]) == [0, 2]
    assert env.distance(0, 3) == 3
    assert env.distance(0, 0) == 0


def test_complete_topology():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 5, "topology": "complete"},
    )
    # Every node connected to every other
    assert len(env.edges) == 5 * 4 // 2
    for i in range(5):
        assert len(env._adjacency[i]) == 4


def test_ring_topology():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 6, "topology": "ring"},
    )
    assert len(env.edges) == 6
    for i in range(6):
        assert len(env._adjacency[i]) == 2
    assert env.distance(0, 3) == 3  # half-way around ring of 6


def test_lattice_topology():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 9, "topology": "lattice", "lattice_dims": [3, 3]},
    )
    # 3x3 lattice has 12 edges (3 rows * 2 horizontal + 2 cols * 3 vertical)
    assert len(env.edges) == 12
    # Corner has 2 neighbors, edge has 3, center has 4
    assert len(env._adjacency[0]) == 2  # top-left corner
    assert len(env._adjacency[4]) == 4  # center (row 1, col 1)


def test_random_topology_runs():
    env = Environment(
        env_type="network",
        dimensions={
            "node_count": 10, "topology": "random", "edge_probability": 0.5,
        },
    )
    # Just check it produces edges and adjacency is consistent
    for a, b in env.edges:
        assert b in env._adjacency[a]
        assert a in env._adjacency[b]


def test_add_edge_idempotent():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 3},
    )
    env.add_edge(0, 1)
    env.add_edge(0, 1)  # duplicate
    env.add_edge(1, 0)  # reverse duplicate
    assert len(env.edges) == 1


def test_add_edge_rejects_invalid():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 3},
    )
    with pytest.raises(ValueError):
        env.add_edge(0, 99)


def test_get_nodes_within_hops():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 5, "topology": "ring"},
    )
    one_hop = set(env.get_nodes_within_hops(0, 1))
    assert one_hop == {1, 4}
    two_hop = set(env.get_nodes_within_hops(0, 2))
    assert two_hop == {1, 2, 3, 4}


def test_simulation_on_network_routes_proximity_via_graph():
    """Agents on a network see neighbors via graph hops, not Euclidean
    distance."""
    spec = {
        "environment": {
            "type": "network",
            "dimensions": {"node_count": 6, "topology": "ring"},
        },
        "agent_types": {
            "node_dweller": {
                "initial_count": 6,
                "initial_state": {"perception_radius": 1, "neighbor_count": 0},
                "behavior_code": (
                    "def node_dweller_behavior(agent, model, agents_nearby):\n"
                    "    return [{'type': 'modify_state',\n"
                    "             'attribute': 'neighbor_count',\n"
                    "             'value': len(agents_nearby)}]\n"
                ),
            }
        },
    }
    sim = Simulation(spec)
    # Force one agent per node so each has 2 neighbors on the ring
    living = sim.agent_manager.get_living_agents()
    for i, agent in enumerate(living):
        agent.set_attribute("position", i)

    sim.run_step()

    counts = [a.get_attribute("neighbor_count") for a in sim.agent_manager.get_living_agents()]
    # Each agent on the ring sees exactly 2 graph-adjacent neighbors
    assert all(c == 2 for c in counts)


def test_network_distance_disconnected():
    env = Environment(
        env_type="network",
        dimensions={"node_count": 4, "edges": [[0, 1]]},
    )
    assert env.distance(0, 2) == float("inf")
