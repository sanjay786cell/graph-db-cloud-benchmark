import csv

cognodb_file = "results/cognodb_results.csv"
neo4j_file = "results/neo4j_results.csv"

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


cognodb = load_results(cognodb_file)
neo4j = load_results(neo4j_file)

print("=" * 80)
print("COGNODB vs NEO4J PERFORMANCE COMPARISON")
print("=" * 80)

print(
    f"{'Workload':<25}"
    f"{'CognoDB p50':>15}"
    f"{'Neo4j p50':>15}"
    f"{'Neo4j speedup':>18}"
)

print("-" * 80)

for key in cognodb:

    category, workload = key

    c = cognodb[key]
    n = neo4j[key]

    speedup = c["p50"] / n["p50"]

    print(
        f"{workload:<25}"
        f"{c['p50']:>15.2f}"
        f"{n['p50']:>15.2f}"
        f"{speedup:>17.2f}x"
    )

print("=" * 80)

print("\nP95 LATENCY COMPARISON")
print("-" * 80)

print(
    f"{'Workload':<25}"
    f"{'CognoDB p95':>15}"
    f"{'Neo4j p95':>15}"
    f"{'Difference':>18}"
)

print("-" * 80)

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
