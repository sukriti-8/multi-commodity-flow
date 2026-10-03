# Multi-Commodity Flow for Data Center Network Routing

A simulation-based implementation of capacity-aware routing for multiple simultaneous data flows in a data center network.

🌐 Live Demo: https://multi-commodity-flow.streamlit.app/

📂 GitHub: https://github.com/sukriti-8/multi-commodity-flow

## Overview

Data center networks handle multiple data flows over shared links with limited capacity. This project implements a Greedy Capacity-Aware Routing algorithm that routes multiple commodities while respecting link capacity constraints.

The project also compares the approach with a Shortest Path baseline and provides an interactive Streamlit simulation.

## Key Features

- Greedy capacity-aware multi-commodity routing
- Congestion-aware path selection
- Splittable traffic demands
- Link capacity constraint handling
- Shortest Path baseline comparison
- Random network simulation
- Interactive network visualization
- Routing and link-utilization metrics
- Runtime and memory measurements
- Automated testing and benchmarking

## How It Works

For each commodity, the algorithm:

1. Generates candidate paths.
2. Checks residual link capacity.
3. Calculates congestion-aware path cost.
4. Selects the lowest-cost feasible path.
5. Allocates flow and updates link usage.
6. Routes remaining demand through another feasible path when required.

Edge cost:

cost(e) = 1 + alpha × (used(e) / capacity(e))

Here, alpha controls the effect of congestion on path cost. The implementation uses alpha = 2.0.

## Comparison

The project uses Shortest Path routing as a baseline.

In one controlled experiment:

| Metric | Capacity-Aware | Shortest Path |
|---|---:|---:|
| Total Routed | 22 | 22 |
| Unrouted | 0 | 0 |
| Satisfied Commodities | 3/3 | 3/3 |
| Maximum Link Utilization | 80% | 100% |
| Average Link Utilization | 68.75% | 68.75% |

The result is test-case dependent. The capacity-aware approach considers current link congestion when making routing decisions.

## Benchmark

Average runtime from the implemented simulation:

| Network | Avg. Runtime |
|---|---:|
| 10 nodes, 15 edges, 5 commodities | 0.4384 ms |
| 20 nodes, 30 edges, 10 commodities | 1.1963 ms |
| 30 nodes, 45 edges, 15 commodities | 3.4612 ms |

Runtime increased across these tested configurations as network size and the number of commodities increased.

## Testing

The project includes tests for:

- Capacity constraints
- Shared bottlenecks
- Insufficient capacity
- Disconnected nodes
- Splittable demand
- Equal-cost paths
- Zero demand

Test result: 7/7 tests passed.

## Complexity

Let V = nodes, E = links, K = commodities, and P = candidate paths.

| Approach | Simplified Complexity |
|---|---|
| Shortest Path | O((V + E) log V) |
| Greedy Capacity-Aware | O(KP(V + E)) |
| Brute Force | O(P^K) |

The exact runtime of the implemented greedy approach also depends on candidate-path generation and routing iterations.

## Project Structure

multi-commodity-flow/
├── app.py
├── routing.py
├── shortest_path.py
├── simulation.py
├── compare.py
├── benchmark.py
├── benchmark_plot.py
├── requirements.txt
└── tests/
    ├── conftest.py
    └── test_routing.py

## File Description

- app.py — Streamlit user interface
- routing.py — Greedy Capacity-Aware Routing algorithm
- shortest_path.py — Shortest Path baseline
- simulation.py — Network and commodity generation
- compare.py — Routing comparison
- benchmark.py — Performance benchmarking
- benchmark_plot.py — Benchmark visualization
- tests/ — Automated routing and edge-case tests

## Tech Stack

- Python
- NetworkX
- Streamlit
- Plotly
- Pandas
- Pytest
- PSUtil
- Matplotlib

## Run Locally

Clone the repository:

git clone https://github.com/sukriti-8/multi-commodity-flow.git

cd multi-commodity-flow

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py

Run tests:

pytest -q

## Limitations

This is a simplified educational implementation. Routing decisions are greedy and depend on the network topology, candidate paths, and commodity ordering. The benchmark results are based on relatively small simulated networks.

## Future Scope

- Custom user-defined network input
- Uploaded network and traffic datasets
- Additional routing algorithms
- Larger-scale experiments
- Optimization-based multi-commodity flow methods

## Author

Sukriti Gupta

Design and Analysis of Algorithms (DAA) Project
