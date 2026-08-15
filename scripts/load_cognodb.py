import csv
import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


NODES_FILE = "data/processed/nodes.csv"
RELATIONSHIPS_FILE = "data/processed/relationships.csv"

BATCH_SIZE = 1000


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")


driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


def load_nodes(session):

    with open(NODES_FILE, newline="") as file:

        reader = csv.DictReader(file)

        batch = []
        total = 0

        start = time.perf_counter()

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
                batch.clear()

        if batch:

            session.run("""
                UNWIND $rows AS row
                CREATE (:Person {id: row.id})
            """, rows=batch).consume()

            total += len(batch)

        elapsed = time.perf_counter() - start

    return total, elapsed


def load_relationships(session):

    with open(RELATIONSHIPS_FILE, newline="") as file:

        reader = csv.DictReader(file)

        batch = []
        total = 0

        start = time.perf_counter()

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

    return total, elapsed


with driver.session() as session:

    print("Loading nodes...")

    node_count, node_time = load_nodes(session)

    print(f"Nodes loaded: {node_count:,}")
    print(f"Node load time: {node_time:.2f} seconds")
    print(f"Node throughput: {node_count / node_time:.2f} nodes/sec")

    print()
    print("Loading relationships...")

    relationship_count, relationship_time = load_relationships(session)

    print(f"Relationships loaded: {relationship_count:,}")
    print(f"Relationship load time: {relationship_time:.2f} seconds")
    print(
        f"Relationship throughput: "
        f"{relationship_count / relationship_time:.2f} relationships/sec"
    )

    total_time = node_time + relationship_time

    print()
    print("==============================")
    print("LOAD SUMMARY")
    print("==============================")
    print(f"Nodes:          {node_count:,}")
    print(f"Relationships:  {relationship_count:,}")
    print(f"Total time:     {total_time:.2f} seconds")


driver.close()
