import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import time
import psutil

from routing import greedy_capacity_aware_routing
from shortest_path import shortest_path_routing
from simulation import generate_network, generate_commodities


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Multi-Commodity Flow Routing",
    page_icon="🌐",
    layout="wide"
)


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def reset_network(graph):
    """Reset all link usage to zero."""
    for u, v, data in graph.edges(data=True):
        data["used"] = 0


def calculate_metrics(graph, results):
    """Calculate routing performance metrics."""

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
        "satisfied": satisfied,
        "max_utilization": max_utilization,
        "average_utilization": average_utilization
    }


def draw_network(graph, results=None):
    """Create a Plotly visualization of the network."""

    if len(graph.nodes) == 0:
        return go.Figure()

    positions = nx.spring_layout(
        graph,
        seed=42
    )

    edge_x = []
    edge_y = []

    for u, v in graph.edges():

        x0, y0 = positions[u]
        x1, y1 = positions[v]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1),
        hoverinfo="none"
    )

    node_x = []
    node_y = []
    node_text = []

    for node in graph.nodes():

        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)

        node_text.append(
            f"Node: {node}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(graph.nodes()),
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=18
        )
    )

    fig = go.Figure(
        data=[
            edge_trace,
            node_trace
        ]
    )

    fig.update_layout(
        height=500,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )
    )

    return fig


def results_table(results):

    rows = []

    for result in results:

        status = (
            "Satisfied"
            if result["remaining"] == 0
            else "Partially Routed"
        )

        rows.append(
            {
                "Commodity": result["commodity"],
                "Source": result["source"],
                "Destination": result["destination"],
                "Demand": result["demand"],
                "Routed": result["routed"],
                "Remaining": result["remaining"],
                "Status": status
            }
        )

    return rows


def route_details(results):

    details = []

    for result in results:

        for route in result["routes"]:

            details.append(
                {
                    "Commodity": result["commodity"],
                    "Path": " → ".join(
                        route["path"]
                    ),
                    "Flow": route["flow"]
                }
            )

    return details


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title(
    "Multi-Commodity Flow for Data Center Network Routing"
)

st.write(
    "A capacity-aware routing system for handling "
    "multiple simultaneous data flows while respecting "
    "network link capacities."
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Network Configuration")

num_nodes = st.sidebar.slider(
    "Number of Nodes",
    min_value=6,
    max_value=50,
    value=10
)

num_edges = st.sidebar.slider(
    "Number of Edges",
    min_value=5,
    max_value=100,
    value=15
)

num_commodities = st.sidebar.slider(
    "Number of Commodities",
    min_value=1,
    max_value=20,
    value=5
)

st.sidebar.markdown("---")

run_button = st.sidebar.button(
    "Run Routing",
    type="primary"
)


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "graph" not in st.session_state:

    graph = generate_network(
        num_nodes,
        num_edges
    )

    commodities = generate_commodities(
        graph,
        num_commodities
    )

    st.session_state.graph = graph
    st.session_state.commodities = commodities
    st.session_state.has_run = False


# ---------------------------------------------------------
# Generate New Network
# ---------------------------------------------------------

if st.sidebar.button("Generate New Network"):

    graph = generate_network(
        num_nodes,
        num_edges
    )

    commodities = generate_commodities(
        graph,
        num_commodities
    )

    st.session_state.graph = graph
    st.session_state.commodities = commodities
    st.session_state.has_run = False

    st.rerun()


graph = st.session_state.graph
commodities = st.session_state.commodities


# ---------------------------------------------------------
# Network Section
# ---------------------------------------------------------

st.header("1. Network")

st.plotly_chart(
    draw_network(graph),
    use_container_width=True
)


# ---------------------------------------------------------
# Network Information
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Nodes",
        len(graph.nodes)
    )

with col2:
    st.metric(
        "Links",
        len(graph.edges)
    )

with col3:
    st.metric(
        "Commodities",
        len(commodities)
    )


# ---------------------------------------------------------
# Commodities
# ---------------------------------------------------------

st.header("2. Data Flow Requests")

commodity_rows = []

for name, source, destination, demand in commodities:

    commodity_rows.append(
        {
            "Commodity": name,
            "Source": source,
            "Destination": destination,
            "Demand": demand
        }
    )

st.dataframe(
    commodity_rows,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# Routing
# ---------------------------------------------------------

if run_button:

    # ---------------------------------------------
    # Greedy Capacity-Aware Routing
    # ---------------------------------------------

    reset_network(graph)

    process_before = psutil.Process().memory_info().rss

    start_time = time.perf_counter()

    greedy_results = greedy_capacity_aware_routing(
        graph,
        commodities
    )

    greedy_runtime = (
        time.perf_counter() - start_time
    )

    process_after = psutil.Process().memory_info().rss

    greedy_memory = (
        process_after - process_before
    )

    greedy_metrics = calculate_metrics(
        graph,
        greedy_results
    )

    # ---------------------------------------------
    # Shortest Path Baseline
    # ---------------------------------------------

    baseline_graph = graph.copy()

    reset_network(baseline_graph)

    start_time = time.perf_counter()

    shortest_results = shortest_path_routing(
        baseline_graph,
        commodities
    )

    shortest_runtime = (
        time.perf_counter() - start_time
    )

    shortest_metrics = calculate_metrics(
        baseline_graph,
        shortest_results
    )

    st.session_state.greedy_results = greedy_results
    st.session_state.greedy_metrics = greedy_metrics

    st.session_state.shortest_results = shortest_results
    st.session_state.shortest_metrics = shortest_metrics

    st.session_state.greedy_runtime = greedy_runtime
    st.session_state.shortest_runtime = shortest_runtime

    st.session_state.greedy_memory = greedy_memory

    st.session_state.has_run = True


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

if st.session_state.has_run:

    greedy_results = st.session_state.greedy_results
    greedy_metrics = st.session_state.greedy_metrics

    shortest_results = st.session_state.shortest_results
    shortest_metrics = st.session_state.shortest_metrics

    greedy_runtime = st.session_state.greedy_runtime
    shortest_runtime = st.session_state.shortest_runtime

    greedy_memory = st.session_state.greedy_memory

    st.header(
        "3. Greedy Capacity-Aware Routing"
    )

    # ---------------------------------------------
    # Metrics
    # ---------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Demand",
            greedy_metrics["total_demand"]
        )

    with c2:
        st.metric(
            "Total Routed",
            greedy_metrics["total_routed"]
        )

    with c3:
        st.metric(
            "Satisfied",
            f"{greedy_metrics['satisfied']} / "
            f"{len(greedy_results)}"
        )

    with c4:
        st.metric(
            "Max Utilization",
            f"{greedy_metrics['max_utilization'] * 100:.1f}%"
        )

    # ---------------------------------------------
    # Routing Results
    # ---------------------------------------------

    st.subheader("Routing Results")

    st.dataframe(
        results_table(greedy_results),
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------
    # Selected Paths
    # ---------------------------------------------

    st.subheader("Selected Paths")

    details = route_details(
        greedy_results
    )

    if details:

        st.dataframe(
            details,
            use_container_width=True,
            hide_index=True
        )

    # ---------------------------------------------
    # Link Utilization
    # ---------------------------------------------

    st.subheader("Link Utilization")

    utilization_rows = []

    for u, v, data in graph.edges(data=True):

        utilization = (
            data["used"] /
            data["capacity"]
            if data["capacity"] > 0
            else 0
        )

        utilization_rows.append(
            {
                "Link": f"{u} → {v}",
                "Used": data["used"],
                "Capacity": data["capacity"],
                "Utilization": (
                    f"{utilization * 100:.1f}%"
                )
            }
        )

    st.dataframe(
        utilization_rows,
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------
    # Performance
    # ---------------------------------------------

    st.subheader("Performance")

    p1, p2, p3 = st.columns(3)

    with p1:

        st.metric(
            "Runtime",
            f"{greedy_runtime * 1000:.3f} ms"
        )

    with p2:

        st.metric(
            "Memory Change",
            f"{greedy_memory / 1024:.1f} KB"
        )

    with p3:

        st.metric(
            "Average Utilization",
            f"{greedy_metrics['average_utilization'] * 100:.1f}%"
        )

    # ---------------------------------------------
    # Comparison
    # ---------------------------------------------

    st.header(
        "4. Comparison with Shortest Path"
    )

    comparison_rows = [

        {
            "Metric": "Total Demand",
            "Greedy Capacity-Aware":
                greedy_metrics["total_demand"],
            "Shortest Path":
                shortest_metrics["total_demand"]
        },

        {
            "Metric": "Total Routed",
            "Greedy Capacity-Aware":
                greedy_metrics["total_routed"],
            "Shortest Path":
                shortest_metrics["total_routed"]
        },

        {
            "Metric": "Unrouted",
            "Greedy Capacity-Aware":
                greedy_metrics["unrouted"],
            "Shortest Path":
                shortest_metrics["unrouted"]
        },

        {
            "Metric": "Satisfied Commodities",
            "Greedy Capacity-Aware":
                f"{greedy_metrics['satisfied']} / {len(greedy_results)}",
            "Shortest Path":
                f"{shortest_metrics['satisfied']} / {len(shortest_results)}"
        },

        {
            "Metric": "Maximum Utilization",
            "Greedy Capacity-Aware":
                f"{greedy_metrics['max_utilization'] * 100:.1f}%",
            "Shortest Path":
                f"{shortest_metrics['max_utilization'] * 100:.1f}%"
        },

        {
            "Metric": "Average Utilization",
            "Greedy Capacity-Aware":
                f"{greedy_metrics['average_utilization'] * 100:.1f}%",
            "Shortest Path":
                f"{shortest_metrics['average_utilization'] * 100:.1f}%"
        },

        {
            "Metric": "Runtime",
            "Greedy Capacity-Aware":
                f"{greedy_runtime * 1000:.3f} ms",
            "Shortest Path":
                f"{shortest_runtime * 1000:.3f} ms"
        }
    ]

    st.dataframe(
        comparison_rows,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "The comparison is test-case dependent. "
        "The capacity-aware approach considers current "
        "link congestion when selecting among candidate paths."
    )

else:

    st.info(
        "Configure the network and click "
        "'Run Routing' to start the simulation."
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "Multi-Commodity Flow for Data Center Network Routing "
    "| DAA Project"
)