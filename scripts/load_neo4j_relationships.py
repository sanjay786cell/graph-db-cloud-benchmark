import csv
import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


BATCH_SIZE = 5000


load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


def load_relationships(session):

    print("Loading relationships...")

    start_time = time.perf_counter()

    batch = []
    total = 0

    with open(
        "data/processed/relationships.csv",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            batch.append({
                "source": int(row["source"]),
                "target": int(row["target"])
            })

            if len(batch) >= BATCH_SIZE:

                session.run(
                    """
                    UNWIND $rows AS row

                    MATCH (source:Person {id: row.source})
                    MATCH (target:Person {id: row.target})

                    CREATE (source)-[:CONNECTED_TO]->(target)
                    """,
                    rows=batch
                ).consume()

                total += len(batch)

                elapsed = time.perf_counter() - start_time
                throughput = total / elapsed

                if total % 25000 == 0:
                    print(
                        f"Relationships loaded: "
                        f"{total:,} / 150,000 "
                        f"({throughput:.2f} rel/sec)"
                    )

                batch = []

        if batch:

            session.run(
                """
                UNWIND $rows AS row

                MATCH (source:Person {id: row.source})
                MATCH (target:Person {id: row.target})

                CREATE (source)-[:CONNECTED_TO]->(target)
                """,
                rows=batch
            ).consume()

            total += len(batch)

    elapsed = time.perf_counter() - start_time
    throughput = total / elapsed

    print()
    print("==============================")
    print("RELATIONSHIP LOAD COMPLETE")
    print("==============================")
    print(f"Relationships: {total:,}")
    print(f"Time:          {elapsed:.2f} seconds")
    print(f"Throughput:    {throughput:.2f} relationships/sec")

    return total, elapsed


with driver.session() as session:

    load_relationships(session)


driver.close()
