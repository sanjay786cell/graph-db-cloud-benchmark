import csv
import time

from neo4j import GraphDatabase


BATCH_SIZE = 1000

MEMGRAPH_URI = "bolt://localhost:7689"


driver = GraphDatabase.driver(
    MEMGRAPH_URI,
    auth=("", "")
)


def load_nodes(session):

    print("Loading nodes...")

    start_time = time.perf_counter()

    batch = []
    total = 0

    with open(
        "data/processed/nodes.csv",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            batch.append({
                "id": int(row["id"])
            })

            if len(batch) >= BATCH_SIZE:

                session.run(
                    """
                    UNWIND $rows AS row
                    CREATE (p:Person {id: row.id})
                    """,
                    rows=batch
                ).consume()

                total += len(batch)

                if total % 1000 == 0:
                    print(f"Nodes loaded: {total:,}")

                batch = []

        if batch:

            session.run(
                """
                UNWIND $rows AS row
                CREATE (p:Person {id: row.id})
                """,
                rows=batch
            ).consume()

            total += len(batch)

    elapsed = time.perf_counter() - start_time

    throughput = total / elapsed

    print()
    print("==============================")
    print("NODE LOAD COMPLETE")
    print("==============================")
    print(f"Nodes:       {total:,}")
    print(f"Time:        {elapsed:.2f} seconds")
    print(f"Throughput:  {throughput:.2f} nodes/sec")

    return total, elapsed


with driver.session() as session:

    load_nodes(session)


driver.close()
