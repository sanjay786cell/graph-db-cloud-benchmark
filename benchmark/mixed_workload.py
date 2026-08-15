import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from neo4j import GraphDatabase


DURATION_SECONDS = 30
CONCURRENCIES = [1, 10, 40]

READ_PERCENT = 80


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
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


READ_QUERY = """
MATCH (p:Person {id: $person_id})
RETURN p.id
"""


WRITE_QUERY = """
MATCH (a:Person {id: $source})
MATCH (b:Person {id: $target})
CREATE (a)-[:BENCHMARK_CONNECTED]->(b)
"""


def worker(stop_event, counters, lock):

    local_count = 0
    local_errors = 0

    with driver.session() as session:

        while not stop_event.is_set():

            try:

                if random.randint(1, 100) <= READ_PERCENT:

                    person_id = random.choice(person_ids)

                    session.run(
                        READ_QUERY,
                        person_id=person_id
                    ).consume()

                else:

                    source = random.choice(person_ids)
                    target = random.choice(person_ids)

                    session.run(
                        WRITE_QUERY,
                        source=source,
                        target=target
                    ).consume()

                local_count += 1

            except Exception:

                local_errors += 1

    with lock:

        counters["completed"] += local_count
        counters["errors"] += local_errors


def run_test(concurrency):

    print()
    print(f"Testing {concurrency} concurrent clients...")

    stop_event = threading.Event()

    counters = {
        "completed": 0,
        "errors": 0
    }

    lock = threading.Lock()

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = []

        for _ in range(concurrency):

            futures.append(
                executor.submit(
                    worker,
                    stop_event,
                    counters,
                    lock
                )
            )

        time.sleep(DURATION_SECONDS)

        stop_event.set()

        for future in futures:
            future.result()

    elapsed = time.perf_counter() - start

    qps = counters["completed"] / elapsed

    print(f"Duration:       {elapsed:.2f} sec")
    print(f"Completed:      {counters['completed']:,}")
    print(f"Errors:         {counters['errors']:,}")
    print(f"Throughput:     {qps:.2f} queries/sec")

    return qps, counters["errors"]


results = []

for concurrency in CONCURRENCIES:

    qps, errors = run_test(concurrency)

    results.append(
        (
            concurrency,
            qps,
            errors
        )
    )


print()
print("==============================")
print("MIXED WORKLOAD RESULTS")
print("==============================")

print(
    f"{'Concurrency':<15}"
    f"{'QPS':<15}"
    f"{'Errors':<10}"
)

for concurrency, qps, errors in results:

    print(
        f"{concurrency:<15}"
        f"{qps:<15.2f}"
        f"{errors:<10}"
    )


# Cleanup benchmark relationships

print()
print("Cleaning up benchmark relationships...")

with driver.session() as session:

    result = session.run("""
        MATCH ()-[r:BENCHMARK_CONNECTED]->()
        DELETE r
        RETURN count(r) AS deleted
    """)

    deleted = result.single()["deleted"]

print(f"Deleted benchmark relationships: {deleted:,}")


driver.close()

