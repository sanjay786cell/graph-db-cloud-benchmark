import os
import random
import statistics
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


ITERATIONS = 100
WARMUP_ITERATIONS = 10


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


def get_start_nodes():

    with driver.session() as session:

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


def percentile(values, percentile):

    values = sorted(values)

    index = (percentile / 100) * (len(values) - 1)

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    fraction = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * fraction
    )


QUERIES = {

    "1-hop": """
        MATCH (p:Person {id: $person_id})
              -[:CONNECTED_TO]->
              (friend)
        RETURN count(friend) AS count
    """,

    "2-hop": """
        MATCH (p:Person {id: $person_id})
              -[:CONNECTED_TO]->
              (friend)
              -[:CONNECTED_TO]->
              (friend2)
        RETURN count(friend2) AS count
    """,

    "3-hop": """
        MATCH (p:Person {id: $person_id})
              -[:CONNECTED_TO]->
              (friend)
              -[:CONNECTED_TO]->
              (friend2)
              -[:CONNECTED_TO]->
              (friend3)
        RETURN count(friend3) AS count
    """
}


start_nodes = get_start_nodes()

print(f"Available start nodes: {len(start_nodes):,}")
print()


with driver.session() as session:

    for name, query in QUERIES.items():

        print(f"Benchmarking {name} traversal...")

        # Warm-up
        for _ in range(WARMUP_ITERATIONS):

            person_id = random.choice(start_nodes)

            session.run(
                query,
                person_id=person_id
            ).consume()

        # Measurement
        latencies = []

        for _ in range(ITERATIONS):

            person_id = random.choice(start_nodes)

            latency = run_query(
                session,
                query,
                person_id
            )

            latencies.append(latency)

        p50 = percentile(latencies, 50)
        p95 = percentile(latencies, 95)

        print(f"  p50: {p50:.2f} ms")
        print(f"  p95: {p95:.2f} ms")
        print(f"  min: {min(latencies):.2f} ms")
        print(f"  max: {max(latencies):.2f} ms")
        print(f"  mean: {statistics.mean(latencies):.2f} ms")
        print()


driver.close()
