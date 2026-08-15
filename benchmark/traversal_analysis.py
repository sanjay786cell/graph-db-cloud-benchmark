cognodb_1 = 245.42
cognodb_3 = 266.05

neo4j_1 = 59.49
neo4j_3 = 182.32

print("=" * 60)
print("TRAVERSAL TAIL LATENCY ANALYSIS")
print("=" * 60)

print("\nCognoDB:")
print(f"1-hop p95: {cognodb_1:.2f} ms")
print(f"3-hop p95: {cognodb_3:.2f} ms")
print(f"Increase: {(cognodb_3 / cognodb_1 - 1) * 100:.1f}%")

print("\nNeo4j:")
print(f"1-hop p95: {neo4j_1:.2f} ms")
print(f"3-hop p95: {neo4j_3:.2f} ms")
print(f"Increase: {(neo4j_3 / neo4j_1 - 1) * 100:.1f}%")
print(f"3-hop / 1-hop ratio: {neo4j_3 / neo4j_1:.2f}x")

print("=" * 60)
