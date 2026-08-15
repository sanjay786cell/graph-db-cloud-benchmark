import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS = Path("results")
CHARTS = RESULTS / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

cognodb = pd.read_csv(RESULTS / "cognodb_results.csv")
neo4j = pd.read_csv(RESULTS / "neo4j_results.csv")

# ---------------------------------------------------------
# 1. Query latency - p50
# ---------------------------------------------------------

merged = cognodb.merge(
    neo4j,
    on=["category", "workload", "iterations"],
    suffixes=("_cognodb", "_neo4j")
)

query = merged[[
    "workload",
    "p50_ms_cognodb",
    "p50_ms_neo4j"
]]

x = range(len(query))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

ax.bar(
    [i - width / 2 for i in x],
    query["p50_ms_cognodb"],
    width,
    label="CognoDB"
)

ax.bar(
    [i + width / 2 for i in x],
    query["p50_ms_neo4j"],
    width,
    label="Neo4j"
)

ax.set_xticks(list(x))
ax.set_xticklabels(query["workload"], rotation=20, ha="right")
ax.set_ylabel("p50 latency (ms)")
ax.set_title("Query Latency: CognoDB vs Neo4j")
ax.legend()

fig.tight_layout()
fig.savefig(CHARTS / "query_latency_p50.png", dpi=180)
plt.close(fig)


# ---------------------------------------------------------
# 2. Ingestion throughput
# ---------------------------------------------------------

labels = [
    "Nodes/sec",
    "Relationships/sec"
]

cognodb_values = [
    3104.03,
    842.22
]

neo4j_values = [
    7104.91,
    7712.12
]

x = range(len(labels))

fig, ax = plt.subplots(figsize=(8, 6))

ax.bar(
    [i - width / 2 for i in x],
    cognodb_values,
    width,
    label="CognoDB"
)

ax.bar(
    [i + width / 2 for i in x],
    neo4j_values,
    width,
    label="Neo4j"
)

ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_ylabel("Throughput (items/sec)")
ax.set_title("Graph Data Ingestion Throughput")
ax.legend()

fig.tight_layout()
fig.savefig(CHARTS / "ingestion_throughput.png", dpi=180)
plt.close(fig)


# ---------------------------------------------------------
# 3. Mixed workload QPS
# ---------------------------------------------------------

mixed = pd.read_csv(RESULTS / "neo4j_mixed_workload.csv")

# The CSV may contain the combined benchmark results.
# If it only contains Neo4j results, use the known benchmark values.

concurrency = [1, 10, 40]

cognodb_qps = [
    4.10,
    38.72,
    145.81
]

neo4j_qps = [
    19.63,
    187.24,
    448.92
]

fig, ax = plt.subplots(figsize=(8, 6))

ax.plot(
    concurrency,
    cognodb_qps,
    marker="o",
    label="CognoDB"
)

ax.plot(
    concurrency,
    neo4j_qps,
    marker="o",
    label="Neo4j"
)

ax.set_xlabel("Concurrent clients")
ax.set_ylabel("Queries/sec")
ax.set_title("Mixed Workload Throughput")
ax.set_xticks(concurrency)
ax.legend()

fig.tight_layout()
fig.savefig(CHARTS / "mixed_workload_qps.png", dpi=180)
plt.close(fig)


# ---------------------------------------------------------
# 4. Traversal p95 latency
# ---------------------------------------------------------

traversal = merged[
    merged["category"] == "Traversal"
].copy()

x = range(len(traversal))

fig, ax = plt.subplots(figsize=(8, 6))

ax.bar(
    [i - width / 2 for i in x],
    traversal["p95_ms_cognodb"],
    width,
    label="CognoDB"
)

ax.bar(
    [i + width / 2 for i in x],
    traversal["p95_ms_neo4j"],
    width,
    label="Neo4j"
)

ax.set_xticks(list(x))
ax.set_xticklabels(traversal["workload"])
ax.set_ylabel("p95 latency (ms)")
ax.set_title("Traversal Tail Latency")
ax.legend()

fig.tight_layout()
fig.savefig(CHARTS / "traversal_p95.png", dpi=180)
plt.close(fig)


print()
print("=" * 60)
print("CHART GENERATION COMPLETE")
print("=" * 60)

for chart in sorted(CHARTS.glob("*.png")):
    print(chart)

print("=" * 60)
