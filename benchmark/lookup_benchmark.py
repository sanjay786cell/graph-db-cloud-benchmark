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


def get_person_ids():

    with driver.session() as session:

        result = session.run("""
            MATCH (p:Person)
            RETURN p.id AS id
            LIMIT 10000
        """)

        return [record["id"] for record in result]


person_ids = get_person_ids()

print(f"Available person IDs: {len(person_ids):,}")
print()


QUERY = """
MATCH (p:Person {id: $person_id})
RETURN p.id AS id
"""


with driver.session() as session:

    # -------------------------
    # Warm-up
    # -------------------------

    print("Warming up...")

    for _ in range(WARMUP_ITERATIONS):

        person_id = random.choice(person_ids)

        session.run(
            QUERY,
            person_id=person_id
        ).consume()


    # -------------------------
    # Measurement
    # -------------------------

    print("Running point lookup benchmark...")

    latencies = []

    for _ in range(ITERATIONS):

        person_id = random.choice(person_ids)

        start = time.perf_counter()

        session.run(
            QUERY,
            person_id=person_id
        ).consume()

        end = time.perf_counter()

        latencies.append(
            (end - start) * 1000
        )


p50 = percentile(latencies, 50)
p95 = percentile(latencies, 95)


print()
print("==============================")
print("POINT LOOKUP RESULTS")
print("==============================")
print(f"Iterations: {ITERATIONS}")
print(f"p50:         {p50:.2f} ms")
print(f"p95:         {p95:.2f} ms")
print(f"min:         {min(latencies):.2f} ms")
print(f"max:         {max(latencies):.2f} ms")
print(f"mean:        {statistics.mean(latencies):.2f} ms")


driver.close()
