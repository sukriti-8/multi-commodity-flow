import matplotlib.pyplot as plt


nodes = [10, 20, 30]
runtime = [0.4384, 1.1963, 3.4612]

plt.figure(figsize=(7, 4.5))

plt.plot(
    nodes,
    runtime,
    marker="o"
)

plt.xlabel("Number of Nodes")
plt.ylabel("Average Runtime (ms)")
plt.title(
    "Greedy Capacity-Aware Routing: "
    "Runtime vs Network Size"
)

plt.xticks(nodes)
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "benchmark_runtime.png",
    dpi=300
)

plt.show()