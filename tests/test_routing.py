import networkx as nx

from routing import greedy_capacity_aware_routing


def test_capacity_constraint():
    """
    No link should exceed its capacity.
    """

    graph = nx.Graph()

    graph.add_edge("A", "B", capacity=10, used=0)
    graph.add_edge("B", "C", capacity=8, used=0)

    commodities = [
        ("C1", "A", "C", 6),
        ("C2", "A", "C", 5),
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    for u, v, data in graph.edges(data=True):
        assert data["used"] <= data["capacity"]


def test_shared_bottleneck():
    """
    Multiple commodities sharing a bottleneck
    must not exceed its capacity.
    """

    graph = nx.Graph()

    graph.add_edge("A", "B", capacity=10, used=0)
    graph.add_edge("B", "F", capacity=8, used=0)

    commodities = [
        ("C1", "A", "F", 6),
        ("C2", "A", "F", 5),
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    assert graph["B"]["F"]["used"] <= 8

    total_routed = sum(
        result["routed"]
        for result in results
    )

    assert total_routed <= 11


def test_insufficient_capacity():
    """
    Demand larger than available network capacity
    should be only partially routed.
    """

    graph = nx.Graph()

    graph.add_edge("A", "B", capacity=5, used=0)

    commodities = [
        ("C1", "A", "B", 10),
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    assert results[0]["routed"] == 5
    assert results[0]["remaining"] == 5


def test_disconnected_nodes():
    """
    A commodity with no path should not be routed.
    """

    graph = nx.Graph()

    graph.add_edge("A", "B", capacity=10, used=0)
    graph.add_edge("C", "D", capacity=10, used=0)

    commodities = [
        ("C1", "A", "D", 5),
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    assert results[0]["routed"] == 0
    assert results[0]["remaining"] == 5


def test_splittable_demand():
    """
    Demand should be allowed to split across
    multiple feasible paths.
    """

    graph = nx.Graph()

    graph.add_edge("A", "B", capacity=5, used=0)
    graph.add_edge("B", "D", capacity=5, used=0)

    graph.add_edge("A", "C", capacity=5, used=0)
    graph.add_edge("C", "D", capacity=5, used=0)

    commodities = [
        ("C1", "A", "D", 8),
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    assert results[0]["routed"] == 8
    assert len(results[0]["routes"]) >= 2


def test_equal_cost_paths():
    """
    Equal-cost paths should still produce a valid
    capacity-feasible routing.
    """

    graph = nx.Graph()

    graph.add_edge("A", "B", capacity=5, used=0)
    graph.add_edge("B", "D", capacity=5, used=0)

    graph.add_edge("A", "C", capacity=5, used=0)
    graph.add_edge("C", "D", capacity=5, used=0)

    commodities = [
        ("C1", "A", "D", 5),
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    assert results[0]["routed"] == 5

    for u, v, data in graph.edges(data=True):
        assert data["used"] <= data["capacity"]


def test_zero_demand():
    """
    Zero demand should require no routing.
    """

    graph = nx.Graph()

    graph.add_edge("A", "B", capacity=10, used=0)

    commodities = [
        ("C1", "A", "B", 0),
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    assert results[0]["routed"] == 0
    assert results[0]["remaining"] == 0