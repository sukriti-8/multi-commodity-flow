import networkx as nx

from routing import greedy_capacity_aware_routing
from shortest_path import shortest_path_routing


def create_comparison_network():
    """
    Create a small network where shortest-path routing
    and congestion-aware routing make different decisions.
    """

    graph = nx.Graph()

    edges = [
        # Short 2-hop path
        ("A", "B", 10),
        ("B", "D", 10),

        # Longer alternate path
        ("A", "C", 10),
        ("C", "E", 10),
        ("E", "D", 10),

        # Additional alternate route
        ("A", "F", 12),
        ("F", "G", 12),
        ("G", "D", 12),
    ]

    for source, destination, capacity in edges:
        graph.add_edge(
            source,
            destination,
            capacity=capacity,
            used=0
        )

    return graph


def create_comparison_commodities():
    """
    Multiple simultaneous traffic demands.
    """

    return [
        ("C1", "A", "D", 8),
        ("C2", "A", "D", 8),
        ("C3", "A", "D", 6),
    ]


def calculate_metrics(graph, results):
    """
    Calculate routing and link-utilization metrics.
    """

    total_demand = sum(
        result["demand"]
        for result in results
    )

    total_routed = sum(
        result["routed"]
        for result in results
    )

    satisfied_commodities = sum(
        1
        for result in results
        if result["remaining"] == 0
    )

    utilizations = []

    for u, v, data in graph.edges(data=True):

        if data["capacity"] > 0:

            utilization = (
                data["used"] / data["capacity"]
            )

            utilizations.append(utilization)

    max_utilization = (
        max(utilizations)
        if utilizations
        else 0
    )

    average_utilization = (
        sum(utilizations) / len(utilizations)
        if utilizations
        else 0
    )

    return {
        "total_demand": total_demand,
        "total_routed": total_routed,
        "unrouted": total_demand - total_routed,
        "satisfied": satisfied_commodities,
        "max_utilization": max_utilization,
        "average_utilization": average_utilization
    }


def print_results(title, results, graph):

    print(f"\n{title}")
    print("=" * 55)

    for result in results:

        print(
            f"{result['commodity']}: "
            f"Demand = {result['demand']}, "
            f"Routed = {result['routed']}, "
            f"Remaining = {result['remaining']}"
        )

        for route in result["routes"]:

            print(
                f"  Path: {' -> '.join(route['path'])}"
            )

            print(
                f"  Flow: {route['flow']}"
            )

    metrics = calculate_metrics(
        graph,
        results
    )

    print("\nSummary")
    print("-" * 55)

    print(
        f"Total demand: "
        f"{metrics['total_demand']}"
    )

    print(
        f"Total routed: "
        f"{metrics['total_routed']}"
    )

    print(
        f"Unrouted: "
        f"{metrics['unrouted']}"
    )

    print(
        f"Satisfied commodities: "
        f"{metrics['satisfied']} / {len(results)}"
    )

    print(
        f"Maximum link utilization: "
        f"{metrics['max_utilization'] * 100:.2f}%"
    )

    print(
        f"Average link utilization: "
        f"{metrics['average_utilization'] * 100:.2f}%"
    )

    print("\nLink Utilization")
    print("-" * 55)

    for u, v, data in graph.edges(data=True):

        print(
            f"{u} -> {v}: "
            f"{data['used']} / {data['capacity']}"
        )


def main():

    commodities = create_comparison_commodities()

    # --------------------------------
    # Shortest Path Baseline
    # --------------------------------

    graph_shortest = create_comparison_network()

    shortest_results = shortest_path_routing(
        graph_shortest,
        commodities
    )

    print_results(
        "SHORTEST PATH BASELINE",
        shortest_results,
        graph_shortest
    )

    # --------------------------------
    # Greedy Capacity-Aware Routing
    # --------------------------------

    graph_greedy = create_comparison_network()

    greedy_results = greedy_capacity_aware_routing(
        graph_greedy,
        commodities
    )

    print_results(
        "GREEDY CAPACITY-AWARE",
        greedy_results,
        graph_greedy
    )


if __name__ == "__main__":
    main()