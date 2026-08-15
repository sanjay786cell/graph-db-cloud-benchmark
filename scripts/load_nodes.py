import csv
import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


NODES_FILE = "data/processed/nodes.csv"
BATCH_SIZE = 1000


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


start = time.perf_counter()

with driver.session() as session:

    batch = []
    total = 0

    with open(NODES_FILE, newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            batch.append({
                "id": int(row["id"])
            })

            if len(batch) >= BATCH_SIZE:

                session.run("""
                    UNWIND $rows AS row
                    CREATE (:Person {id: row.id})
                """, rows=batch).consume()

                total += len(batch)

                print(f"Nodes loaded: {total:,}", flush=True)

                batch.clear()

        if batch:

            session.run("""
                UNWIND $rows AS row
                CREATE (:Person {id: row.id})
            """, rows=batch).consume()

            total += len(batch)

elapsed = time.perf_counter() - start

print()
print("==============================")
print("NODE LOAD COMPLETE")
print("==============================")
print(f"Nodes:       {total:,}")
print(f"Time:        {elapsed:.2f} seconds")
print(f"Throughput:  {total / elapsed:.2f} nodes/sec")


driver.close()
