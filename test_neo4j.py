import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")


print("Connecting to Neo4j...")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)


with driver.session() as session:

    result = session.run(
        "RETURN 1 AS result"
    )

    print("Result:", result.single()["result"])


driver.close()

print("Connection successful!")
