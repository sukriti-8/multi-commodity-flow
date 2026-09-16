#it have 3 things -- Network, Commodity, and Capacity
#NetworkX -- use to present data center network
import networkx as nx


def create_network():
    """
    Create the data center network used for testing.
    Each edge has a capacity.
    """

    graph = nx.Graph()

    edges = [
        ("A", "B", 10),
        ("A", "C", 12),
        ("B", "C", 8),
        ("B", "D", 7),
        ("C", "D", 10),
        ("D", "F", 10),
        ("B", "E", 9),
    ]

    for source, destination, capacity in edges:
        graph.add_edge(
            source,
            destination,
            capacity=capacity,
            used=0
        )

    return graph

def create_commodities():
    """
    Create the data-flow requests.
    Format:
    (commodity_name, source, destination, demand)
    """

    commodities = [
        ("C1", "A", "F", 6),
        ("C2", "C", "D", 5),
        ("C3", "B", "E", 4),
    ]

    return commodities



#edge-cost fnc 
def edge_cost(graph, u, v, alpha=2.0):
    """
    Calculate the congestion-aware cost of an edge.

    Cost increases as the edge becomes more heavily utilized.
    """

    edge_data = graph[u][v]

    capacity = edge_data["capacity"]
    used = edge_data["used"]

    if capacity <= 0:
        return float("inf")

    utilization = used / capacity

    return 1 + alpha * utilization

#add path cost
def path_cost(graph, path, alpha=2.0):
    """
    Calculate the total congestion-aware cost of a path.
    """

    total_cost = 0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        total_cost += edge_cost(graph, u, v, alpha)

    return total_cost

#capacity checking ==> capacity = min(residual(e))
def path_residual_capacity(graph, path):
    """
    Find the maximum additional flow that can be sent
    through the given path.
    """

    residual_capacity = float("inf")

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        edge_data = graph[u][v]

        capacity = edge_data["capacity"]
        used = edge_data["used"]

        residual = capacity - used

        residual_capacity = min(
            residual_capacity,
            residual
        )

    return residual_capacity

#flow allocation
def allocate_flow(graph, path, flow):
    """
    Allocate flow along every edge of a selected path.
    """

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        graph[u][v]["used"] += flow

#candidate path
def get_candidate_paths(graph, source, destination, k=3):
    """
    Generate up to k shortest candidate paths between
    a commodity's source and destination.
    """

    try:
        paths = nx.shortest_simple_paths(
            graph,
            source,
            destination
        )

        candidate_paths = []

        for path in paths:
            candidate_paths.append(path)

            if len(candidate_paths) == k:
                break

        return candidate_paths

    except nx.NetworkXNoPath:
        return []

#feasible path
def select_best_path(graph, candidate_paths, alpha=2.0):
    """
    Select the lowest-cost path among feasible candidate paths.
    """

    feasible_paths = []

    for path in candidate_paths:
        residual_capacity = path_residual_capacity(
            graph,
            path
        )

        if residual_capacity > 0:
            cost = path_cost(
                graph,
                path,
                alpha
            )

            feasible_paths.append(
                (cost, path, residual_capacity)
            )

    if not feasible_paths:
        return None

    feasible_paths.sort(
        key=lambda item: item[0]
    )

    return feasible_paths[0]

#main fnc-- algorithm
def greedy_capacity_aware_routing(
    graph,
    commodities,
    k=3,
    alpha=2.0
):
    """
    Greedy Capacity-Aware Multi-Commodity Routing.

    Routes each commodity through feasible paths while
    considering current link congestion.
    """

    routing_results = []

    for name, source, destination, demand in commodities:

        remaining_demand = demand
        commodity_routes = []

        while remaining_demand > 0:

            candidate_paths = get_candidate_paths(
                graph,
                source,
                destination,
                k
            )

            best_path = select_best_path(
                graph,
                candidate_paths,
                alpha
            )

            if best_path is None:
                break

            cost, path, residual_capacity = best_path

            flow = min(
                remaining_demand,
                residual_capacity
            )

            allocate_flow(
                graph,
                path,
                flow
            )

            remaining_demand -= flow

            commodity_routes.append({
                "path": path,
                "flow": flow,
                "cost": cost
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

#test code
if __name__ == "__main__":
    graph = create_network()
    commodities = create_commodities()

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    print("GREEDY CAPACITY-AWARE ROUTING")
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
            print(
                f"  Cost: {route['cost']:.2f}"
            )

    print("\nFINAL LINK UTILIZATION")
    print("=" * 40)

    for source, destination, data in graph.edges(data=True):
        print(
            f"{source} -> {destination}: "
            f"{data['used']} / {data['capacity']}"
        )