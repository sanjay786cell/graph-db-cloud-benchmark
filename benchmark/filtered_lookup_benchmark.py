import os
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


QUERY = """
MATCH (p:Person)
WHERE p.group = $group
RETURN count(p) AS count
"""


with driver.session() as session:

    print("Warming up...")

    for _ in range(WARMUP_ITERATIONS):

        session.run(
            QUERY,
            group=50
        ).consume()


    print("Running filtered lookup benchmark...")

    latencies = []

    for _ in range(ITERATIONS):

        start = time.perf_counter()

        session.run(
            QUERY,
            group=50
        ).consume()

        end = time.perf_counter()

        latencies.append(
            (end - start) * 1000
        )


p50 = percentile(latencies, 50)
p95 = percentile(latencies, 95)


print()
print("==============================")
print("FILTERED LOOKUP RESULTS")
print("==============================")
print(f"Iterations: {ITERATIONS}")
print(f"p50:         {p50:.2f} ms")
print(f"p95:         {p95:.2f} ms")
print(f"min:         {min(latencies):.2f} ms")
print(f"max:         {max(latencies):.2f} ms")
print(f"mean:        {statistics.mean(latencies):.2f} ms")


driver.close()
