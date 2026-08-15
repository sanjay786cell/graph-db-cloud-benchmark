import os
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase


ITERATIONS = 100


load_dotenv()

uri = os.getenv("MEMGRAPH_URI")
username = os.getenv("MEMGRAPH_USERNAME")
password = os.getenv("MEMGRAPH_PASSWORD")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


def run_aggregation(session):

    start = time.perf_counter()

    session.run(
        """
        MATCH (p:Person)
        WITH p.group AS group_value, count(*) AS count
        RETURN group_value, count
        ORDER BY group_value
        """
    ).consume()

    end = time.perf_counter()

    return (end - start) * 1000


with driver.session() as session:

    print("Warming up...")

    for _ in range(20):
        run_aggregation(session)

    print("Running aggregation benchmark...")

    latencies = []

    for _ in range(ITERATIONS):

        latency = run_aggregation(session)

        latencies.append(latency)

    latencies.sort()

    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95) - 1]

    print()
    print("==============================")
    print("MEMGRAPH AGGREGATION RESULTS")
    print("==============================")
    print(f"Iterations: {ITERATIONS}")
    print(f"p50:         {p50:.2f} ms")
    print(f"p95:         {p95:.2f} ms")
    print(f"min:         {min(latencies):.2f} ms")
    print(f"max:         {max(latencies):.2f} ms")
    print(f"mean:        {statistics.mean(latencies):.2f} ms")


driver.close()