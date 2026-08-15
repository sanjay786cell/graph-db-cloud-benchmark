import os
import random
import time
import statistics

from dotenv import load_dotenv
from neo4j import GraphDatabase


ITERATIONS = 100


load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


def get_person_ids(session):

    result = session.run("""
        MATCH (p:Person)
        RETURN p.id AS id
        LIMIT 10000
    """)

    return [record["id"] for record in result]


def run_lookup(session, person_id):

    start = time.perf_counter()

    session.run(
        """
        MATCH (p:Person {id: $person_id})
        RETURN p.id
        """,
        person_id=person_id
    ).consume()

    end = time.perf_counter()

    return (end - start) * 1000


with driver.session() as session:

    person_ids = get_person_ids(session)

    print(
        f"Available person IDs: {len(person_ids):,}"
    )

    print()
    print("Warming up...")

    for person_id in person_ids[:20]:
        run_lookup(session, person_id)

    print("Running point lookup benchmark...")

    latencies = []

    for _ in range(ITERATIONS):

        person_id = random.choice(person_ids)

        latency = run_lookup(
            session,
            person_id
        )

        latencies.append(latency)

    latencies.sort()

    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95) - 1]

    print()
    print("==============================")
    print("NEO4J POINT LOOKUP RESULTS")
    print("==============================")
    print(f"Iterations: {ITERATIONS}")
    print(f"p50:         {p50:.2f} ms")
    print(f"p95:         {p95:.2f} ms")
    print(f"min:         {min(latencies):.2f} ms")
    print(f"max:         {max(latencies):.2f} ms")
    print(f"mean:        {statistics.mean(latencies):.2f} ms")


driver.close()

