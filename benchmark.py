import time
import statistics
import networkx as nx

from routing import greedy_capacity_aware_routing
from simulation import generate_network, generate_commodities


def calculate_metrics(graph, results):
    total_demand = sum(
        result["demand"]
        for result in results
    )

    total_routed = sum(
        result["routed"]
        for result in results
    )

    satisfied = sum(
        1
        for result in results
        if result["remaining"] == 0
    )

    utilizations = []

    for _, _, data in graph.edges(data=True):
        if data["capacity"] > 0:
            utilizations.append(
                data["used"] / data["capacity"]
            )

    max_utilization = (
        max(utilizations)
        if utilizations
        else 0
    )

    return {
        "total_demand": total_demand,
        "total_routed": total_routed,
        "satisfied": satisfied,
        "max_utilization": max_utilization
    }


def run_benchmark(
    num_nodes,
    num_edges,
    num_commodities,
    runs=10
):
    runtimes = []
    routed_values = []
    demand_values = []
    satisfied_values = []
    utilization_values = []

    for run in range(runs):

        graph = generate_network(
            num_nodes,
            num_edges
        )

        commodities = generate_commodities(
            graph,
            num_commodities
        )

        start_time = time.perf_counter()

        results = greedy_capacity_aware_routing(
            graph,
            commodities
        )

        end_time = time.perf_counter()

        runtime_ms = (
            end_time - start_time
        ) * 1000

        metrics = calculate_metrics(
            graph,
            results
        )

        runtimes.append(runtime_ms)
        routed_values.append(
            metrics["total_routed"]
        )
        demand_values.append(
            metrics["total_demand"]
        )
        satisfied_values.append(
            metrics["satisfied"]
        )
        utilization_values.append(
            metrics["max_utilization"]
        )

    return {
        "nodes": num_nodes,
        "edges": num_edges,
        "commodities": num_commodities,
        "runtime_ms": statistics.mean(runtimes),
        "total_demand": statistics.mean(demand_values),
        "total_routed": statistics.mean(routed_values),
        "satisfied": statistics.mean(satisfied_values),
        "max_utilization": statistics.mean(
            utilization_values
        )
    }


def main():

    benchmark_cases = [
        (10, 15, 5),
        (20, 30, 10),
        (30, 45, 15)
    ]

    print("GREEDY CAPACITY-AWARE BENCHMARK")
    print("=" * 70)

    results = []

    for nodes, edges, commodities in benchmark_cases:

        result = run_benchmark(
            nodes,
            edges,
            commodities,
            runs=10
        )

        results.append(result)

        print(
            f"\nNetwork: "
            f"{nodes} nodes, "
            f"{edges} edges, "
            f"{commodities} commodities"
        )

        print(
            f"Average runtime: "
            f"{result['runtime_ms']:.4f} ms"
        )

        print(
            f"Average total demand: "
            f"{result['total_demand']:.2f}"
        )

        print(
            f"Average total routed: "
            f"{result['total_routed']:.2f}"
        )

        print(
            f"Average satisfied commodities: "
            f"{result['satisfied']:.2f}"
        )

        print(
            f"Average maximum utilization: "
            f"{result['max_utilization'] * 100:.2f}%"
        )

    print("\nSUMMARY")
    print("=" * 70)

    print(
        "Nodes | Edges | Commodities | "
        "Runtime(ms) | Demand | Routed | Satisfied | Max Util"
    )

    print("-" * 70)

    for result in results:

        print(
            f"{result['nodes']:5} | "
            f"{result['edges']:5} | "
            f"{result['commodities']:11} | "
            f"{result['runtime_ms']:10.4f} | "
            f"{result['total_demand']:6.2f} | "
            f"{result['total_routed']:6.2f} | "
            f"{result['satisfied']:9.2f} | "
            f"{result['max_utilization'] * 100:7.2f}%"
        )


if __name__ == "__main__":
    main()