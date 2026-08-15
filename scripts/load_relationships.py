import csv
import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


RELATIONSHIPS_FILE = "data/processed/relationships.csv"
BATCH_SIZE = 250


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

    with open(RELATIONSHIPS_FILE, newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            batch.append({
                "source": int(row["source"]),
                "target": int(row["target"])
            })

            if len(batch) >= BATCH_SIZE:

                session.run("""
                    UNWIND $rows AS row
                    MATCH (a:Person {id: row.source})
                    MATCH (b:Person {id: row.target})
                    CREATE (a)-[:CONNECTED_TO]->(b)
                """, rows=batch).consume()

                total += len(batch)

                if total % 5000 == 0:
                    elapsed = time.perf_counter() - start
                    rate = total / elapsed

                    print(
                        f"Relationships loaded: "
                        f"{total:,} / 150,000 "
                        f"({rate:.2f} rel/sec)",
                        flush=True
                    )

                batch.clear()

        if batch:

            session.run("""
                UNWIND $rows AS row
                MATCH (a:Person {id: row.source})
                MATCH (b:Person {id: row.target})
                CREATE (a)-[:CONNECTED_TO]->(b)
            """, rows=batch).consume()

            total += len(batch)


elapsed = time.perf_counter() - start

print()
print("==============================")
print("RELATIONSHIP LOAD COMPLETE")
print("==============================")
print(f"Relationships: {total:,}")
print(f"Time:          {elapsed:.2f} seconds")
print(f"Throughput:    {total / elapsed:.2f} relationships/sec")


driver.close()

