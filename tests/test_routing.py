from routing import (
    create_network,
    create_commodities,
    greedy_capacity_aware_routing
)


def test_capacity_constraint():
    """
    Verify that no network edge is used beyond its capacity.
    """

    graph = create_network()
    commodities = create_commodities()

    greedy_capacity_aware_routing(
        graph,
        commodities
    )

    for source, destination, data in graph.edges(data=True):
        assert data["used"] <= data["capacity"]

#bottleneck
def test_shared_bottleneck():
    """
    Verify that multiple commodities sharing a bottleneck
    do not cause the link capacity to be exceeded.
    """

    graph = create_network()

    commodities = [
        ("C1", "A", "F", 6),
        ("C2", "A", "F", 5)
    ]

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    # Verify that no edge exceeds its capacity
    for source, destination, data in graph.edges(data=True):
        assert data["used"] <= data["capacity"]

    # Total routed flow cannot exceed total demand
    total_demand = sum(
        commodity[3] for commodity in commodities
    )

    total_routed = sum(
        result["routed"] for result in results
    )

    assert total_routed <= total_demand