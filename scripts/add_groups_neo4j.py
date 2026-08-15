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

    print("Adding group property...")

    session.run("""
        MATCH (p:Person)
        SET p.group = CASE
            WHEN p.id % 5 = 0 THEN 0
            WHEN p.id % 5 = 1 THEN 1
            WHEN p.id % 5 = 2 THEN 2
            WHEN p.id % 5 = 3 THEN 3
            ELSE 4
        END
    """).consume()

    print("Group property added.")


driver.close()
