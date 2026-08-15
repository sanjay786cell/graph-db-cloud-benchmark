import csv


def load_results(filename):
    results = {}

    with open(filename, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            key = (row["category"], row["workload"])

            results[key] = {
                "p50": float(row["p50_ms"]),
                "p95": float(row["p95_ms"]),
                "mean": float(row["mean_ms"]),
            }

    return results


cognodb = load_results("results/cognodb_results.csv")
neo4j = load_results("results/neo4j_results.csv")


print("=" * 90)
print("GRAPH DATABASE BENCHMARK ANALYSIS")
print("=" * 90)


# ---------------------------------------------------------
# LATENCY
# ---------------------------------------------------------

print("\n1. QUERY LATENCY")
print("-" * 90)

print(
    f"{'Workload':<25}"
    f"{'CognoDB p50':>15}"
    f"{'Neo4j p50':>15}"
    f"{'Neo4j speedup':>18}"
    f"{'Latency reduction':>18}"
)

print("-" * 90)

for key in cognodb:

    category, workload = key

    c = cognodb[key]
    n = neo4j[key]

    speedup = c["p50"] / n["p50"]
    reduction = (1 - n["p50"] / c["p50"]) * 100

    print(
        f"{workload:<25}"
        f"{c['p50']:>15.2f}"
        f"{n['p50']:>15.2f}"
        f"{speedup:>17.2f}x"
        f"{reduction:>17.1f}%"
    )


# ---------------------------------------------------------
# P95
# ---------------------------------------------------------

print("\n\n2. P95 LATENCY")
print("-" * 90)

print(
    f"{'Workload':<25}"
    f"{'CognoDB p95':>15}"
    f"{'Neo4j p95':>15}"
    f"{'Difference':>18}"
)

print("-" * 90)

for key in cognodb:

    category, workload = key

    c = cognodb[key]
    n = neo4j[key]

    difference = c["p95"] - n["p95"]

    print(
        f"{workload:<25}"
        f"{c['p95']:>15.2f}"
        f"{n['p95']:>15.2f}"
        f"{difference:>17.2f} ms"
    )


# ---------------------------------------------------------
# TRAVERSAL SCALING
# ---------------------------------------------------------

print("\n\n3. TRAVERSAL SCALING")
print("-" * 90)

for database_name, database in [
    ("CognoDB", cognodb),
    ("Neo4j", neo4j),
]:

    one_hop = database[("Traversal", "1-hop")]["p50"]
    three_hop = database[("Traversal", "3-hop")]["p50"]

    increase = ((three_hop / one_hop) - 1) * 100

    print(
        f"{database_name:<12}"
        f"1-hop: {one_hop:.2f} ms    "
        f"3-hop: {three_hop:.2f} ms    "
        f"Increase: {increase:.2f}%"
    )


# ---------------------------------------------------------
# INGESTION
# ---------------------------------------------------------

print("\n\n4. DATA INGESTION")
print("-" * 90)

cognodb_nodes = 3104.03
neo4j_nodes = 7104.91

cognodb_relationships = 842.22
neo4j_relationships = 7712.12

print(
    f"Node throughput:\n"
    f"  CognoDB: {cognodb_nodes:.2f} nodes/sec\n"
    f"  Neo4j:   {neo4j_nodes:.2f} nodes/sec\n"
    f"  Neo4j advantage: {neo4j_nodes / cognodb_nodes:.2f}x"
)

print()

print(
    f"Relationship throughput:\n"
    f"  CognoDB: {cognodb_relationships:.2f} relationships/sec\n"
    f"  Neo4j:   {neo4j_relationships:.2f} relationships/sec\n"
    f"  Neo4j advantage: {neo4j_relationships / cognodb_relationships:.2f}x"
)


# ---------------------------------------------------------
# MIXED WORKLOAD
# ---------------------------------------------------------

print("\n\n5. MIXED WORKLOAD THROUGHPUT")
print("-" * 90)

mixed = {
    "CognoDB": {
        1: 4.10,
        10: 38.72,
        40: 145.81,
    },
    "Neo4j": {
        1: 19.63,
        10: 187.24,
        40: 448.92,
    },
}

print(
    f"{'Clients':<12}"
    f"{'CognoDB QPS':>18}"
    f"{'Neo4j QPS':>18}"
    f"{'Neo4j advantage':>20}"
)

print("-" * 70)

for clients in [1, 10, 40]:

    c = mixed["CognoDB"][clients]
    n = mixed["Neo4j"][clients]

    advantage = n / c

    print(
        f"{clients:<12}"
        f"{c:>18.2f}"
        f"{n:>18.2f}"
        f"{advantage:>19.2f}x"
    )


print("\n" + "=" * 90)
print("ANALYSIS COMPLETE")
print("=" * 90)
