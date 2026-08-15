import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")


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
    """).consume()

    print("Index created successfully.")


driver.close()
