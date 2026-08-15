import os
import random
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase


ITERATIONS = 100
START_NODE_COUNT = 10_000


load_dotenv()

uri = os.getenv("MEMGRAPH_URI")
username = os.getenv("MEMGRAPH_USERNAME")
password = os.getenv("MEMGRAPH_PASSWORD")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


def get_start_nodes(session):

    result = session.run("""
        MATCH (p:Person)
        RETURN p.id AS id
        LIMIT 10000
    """)

    return [record["id"] for record in result]


def run_query(session, query, person_id):

    start = time.perf_counter()

    session.run(
        query,
        person_id=person_id
    ).consume()

    end = time.perf_counter()

    return (end - start) * 1000


def benchmark(session, query, start_nodes, name):

    print()
    print(f"Benchmarking {name} traversal...")

    # Warm-up
    for person_id in start_nodes[:20]:

        run_query(
            session,
            query,
            person_id
        )

    latencies = []

    for _ in range(ITERATIONS):

        person_id = random.choice(start_nodes)

        latency = run_query(
            session,
            query,
            person_id
        )

        latencies.append(latency)

    latencies.sort()

    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95) - 1]

    print(f"  p50: {p50:.2f} ms")
    print(f"  p95: {p95:.2f} ms")
    print(f"  min: {min(latencies):.2f} ms")
    print(f"  max: {max(latencies):.2f} ms")
    print(f"  mean: {statistics.mean(latencies):.2f} ms")

    return {
        "p50": p50,
        "p95": p95,
        "min": min(latencies),
        "max": max(latencies),
        "mean": statistics.mean(latencies)
    }


with driver.session() as session:

    start_nodes = get_start_nodes(session)

    print(
        f"Available start nodes: {len(start_nodes):,}"
    )

    queries = {

        "1-hop": """
            MATCH (p:Person {id: $person_id})
                  -[:CONNECTED_TO]->(n)
            RETURN n.id
        """,

        "2-hop": """
            MATCH (p:Person {id: $person_id})
                  -[:CONNECTED_TO*2]->(n)
            RETURN n.id
        """,

        "3-hop": """
            MATCH (p:Person {id: $person_id})
                  -[:CONNECTED_TO*3]->(n)
            RETURN n.id
        """
    }

    results = {}

    for name, query in queries.items():

        results[name] = benchmark(
            session,
            query,
            start_nodes,
            name
        )


driver.close()