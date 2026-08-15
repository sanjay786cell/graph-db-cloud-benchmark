import os
import random
import threading
import time

from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from neo4j import GraphDatabase


DURATION = 30

CONCURRENCIES = [1, 10, 40]


load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


def run_read(session):

    person_id = random.randint(
        1,
        74062
    )

    session.run(
        """
        MATCH (p:Person {id: $person_id})
              -[:CONNECTED_TO]->(n)
        RETURN n.id
        LIMIT 10
        """,
        person_id=person_id
    ).consume()


def run_write(session):

    source = random.randint(
        1,
        74062
    )

    target = random.randint(
        1,
        74062
    )

    session.run(
        """
        MATCH (a:Person {id: $source})
        MATCH (b:Person {id: $target})
        CREATE (a)-[:BENCHMARK_REL]->(b)
        """,
        source=source,
        target=target
    ).consume()


def worker(stop_event, counter, errors):

    local_count = 0

    try:

        with driver.session() as session:

            while not stop_event.is_set():

                # 80% reads, 20% writes
                if random.random() < 0.8:

                    run_read(session)

                else:

                    run_write(session)

                local_count += 1

    except Exception:

        errors.append(1)

    counter.append(local_count)


def run_test(concurrency):

    print()
    print(
        f"Testing {concurrency} concurrent clients..."
    )

    stop_event = threading.Event()

    counter = []

    errors = []

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
                    counter,
                    errors
                )
            )

        time.sleep(DURATION)

        stop_event.set()

        for future in futures:
            future.result()

    elapsed = time.perf_counter() - start

    completed = sum(counter)

    qps = completed / elapsed

    print(
        f"Duration:       {elapsed:.2f} sec"
    )

    print(
        f"Completed:      {completed:,}"
    )

    print(
        f"Errors:         {len(errors)}"
    )

    print(
        f"Throughput:     {qps:.2f} queries/sec"
    )

    return qps, len(errors)


for concurrency in CONCURRENCIES:

    run_test(concurrency)


driver.close()
