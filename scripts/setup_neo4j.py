import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

with driver.session() as session:
    print("Creating Person ID index...")

    session.run("""
        CREATE INDEX person_id_index IF NOT EXISTS
        FOR (p:Person)
        ON (p.id)
    """)

    print("Index created successfully.")

driver.close()
