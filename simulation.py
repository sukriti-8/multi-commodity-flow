import random
import networkx as nx
import time
import os
import psutil

random.seed(42)

def generate_network(num_nodes, num_edges):
    """
    Generate a random data center network.

    Each edge is assigned a random capacity.
    """

    graph = nx.gnm_random_graph(
        num_nodes,
        num_edges,
        seed=42
    )

    # Make sure every edge has a positive capacity
    for u, v in graph.edges():
        graph[u][v]["capacity"] = random.randint(5, 20)
        graph[u][v]["used"] = 0

    return graph


def generate_commodities(graph, num_commodities):
    """
    Generate random source-destination traffic demands.
    """

    nodes = list(graph.nodes())
    commodities = []

    for i in range(num_commodities):

        source, destination = random.sample(nodes, 2)

        # Only create a commodity if a path exists
        if nx.has_path(graph, source, destination):

            demand = random.randint(2, 10)

            commodities.append(
                (
                    f"C{i + 1}",
                    source,
                    destination,
                    demand
                )
            )

    return commodities


def reset_network(graph):
    """
    Reset all link usage values to zero.
    """

    for u, v in graph.edges():
        graph[u][v]["used"] = 0


if __name__ == "__main__":

    from routing import greedy_capacity_aware_routing

    graph = generate_network(
        num_nodes=10,
        num_edges=15
    )

    commodities = generate_commodities(
        graph,
        num_commodities=5
    )

    print("SIMULATION NETWORK")
    print("=" * 40)

    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")

    print("\nLINK CAPACITIES")
    print("=" * 40)

    for u, v, data in graph.edges(data=True):
        print(
            f"{u} -> {v}: "
            f"capacity = {data['capacity']}"
        )

    print("\nCOMMODITIES")
    print("=" * 40)

    for commodity in commodities:
        name, source, destination, demand = commodity

        print(
            f"{name}: "
            f"{source} -> {destination}, "
            f"demand = {demand}"
        )

    # Measure runtime and memory
    process = psutil.Process(os.getpid())

    memory_before = process.memory_info().rss

    start_time = time.perf_counter()

    results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    end_time = time.perf_counter()

    memory_after = process.memory_info().rss

    runtime = end_time - start_time
    memory_used = max(0, memory_after - memory_before)

    print("\nROUTING RESULTS")
    print("=" * 40)

    for result in results:
        print(
            f"{result['commodity']}: "
            f"{result['source']} -> {result['destination']} | "
            f"Demand = {result['demand']} | "
            f"Routed = {result['routed']} | "
            f"Remaining = {result['remaining']}"
        )


    # Calculate overall metrics
    total_demand = sum(
        result["demand"] for result in results
    )

    total_routed = sum(
        result["routed"] for result in results
    )

    satisfied_commodities = sum(
        1
        for result in results
        if result["remaining"] == 0
    )

    max_utilization = 0

    for u, v, data in graph.edges(data=True):

        if data["capacity"] > 0:

            utilization = (
                data["used"] / data["capacity"]
            )

            max_utilization = max(
                max_utilization,
                utilization
            )


    print("\nPERFORMANCE METRICS")
    print("=" * 40)

    print(f"Total demand: {total_demand}")
    print(f"Total routed: {total_routed}")

    print(
        f"Satisfied commodities: "
        f"{satisfied_commodities} / {len(results)}"
    )

    print(
        f"Maximum link utilization: "
        f"{max_utilization * 100:.2f}%"
    )

    print(
        f"Runtime: "
        f"{runtime * 1000:.4f} ms"
    )

    print(
        f"Memory change: "
        f"{memory_used / 1024:.2f} KB"
    )
    print("\nFINAL LINK UTILIZATION")
    print("=" * 40)

    for u, v, data in graph.edges(data=True):
        print(
            f"{u} -> {v}: "
            f"{data['used']} / {data['capacity']}"
        )