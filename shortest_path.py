import networkx as nx


def shortest_path_routing(graph, commodities):
    """
    Shortest Path Baseline.

    Routes each commodity using the shortest feasible path.
    Path length is measured by number of hops.
    """

    routing_results = []

    for name, source, destination, demand in commodities:

        remaining_demand = demand
        commodity_routes = []

        try:
            candidate_paths = nx.shortest_simple_paths(
                graph,
                source,
                destination
            )
        except nx.NetworkXNoPath:
            candidate_paths = []

        for path in candidate_paths:

            if remaining_demand <= 0:
                break

            residual_capacity = float("inf")

            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]

                capacity = graph[u][v]["capacity"]
                used = graph[u][v]["used"]

                residual_capacity = min(
                    residual_capacity,
                    capacity - used
                )

            if residual_capacity <= 0:
                continue

            flow = min(
                remaining_demand,
                residual_capacity
            )

            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]

                graph[u][v]["used"] += flow

            remaining_demand -= flow

            commodity_routes.append({
                "path": path,
                "flow": flow
            })

        routed_flow = demand - remaining_demand

        routing_results.append({
            "commodity": name,
            "source": source,
            "destination": destination,
            "demand": demand,
            "routed": routed_flow,
            "remaining": remaining_demand,
            "routes": commodity_routes
        })

    return routing_results


if __name__ == "__main__":

    from routing import create_network, create_commodities

    graph = create_network()
    commodities = create_commodities()

    results = shortest_path_routing(
        graph,
        commodities
    )

    print("SHORTEST PATH BASELINE")
    print("=" * 40)

    for result in results:

        print(
            f"\n{result['commodity']}: "
            f"{result['source']} -> {result['destination']}"
        )

        print(f"Demand: {result['demand']}")
        print(f"Routed: {result['routed']}")
        print(f"Remaining: {result['remaining']}")

        for route in result["routes"]:
            print(
                f"  Path: {' -> '.join(route['path'])}"
            )
            print(
                f"  Flow: {route['flow']}"
            )

    print("\nFINAL LINK UTILIZATION")
    print("=" * 40)

    for source, destination, data in graph.edges(data=True):

        print(
            f"{source} -> {destination}: "
            f"{data['used']} / {data['capacity']}"
        )