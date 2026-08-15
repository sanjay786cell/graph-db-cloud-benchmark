import os
from neo4j import GraphDatabase

URI = "bolt://localhost:7689"

driver = GraphDatabase.driver(
    URI,
    auth=("", "")
)

try:
    with driver.session() as session:
        print("Creating Person ID index...")

        session.run(
            "CREATE INDEX person_id_index IF NOT EXISTS "
            "FOR (p:Person) ON (p.id)"
        )

        print("Index created successfully.")

finally:
    driver.close()
