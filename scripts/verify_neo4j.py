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

    node_result = session.run("""
        MATCH (p:Person)
        RETURN count(p) AS count
    """)

    relationship_result = session.run("""
        MATCH ()-[r:CONNECTED_TO]->()
        RETURN count(r) AS count
    """)

    nodes = node_result.single()["count"]
    relationships = relationship_result.single()["count"]


print("==============================")
print("NEO4J DATASET VERIFICATION")
print("==============================")
print(f"Nodes:         {nodes:,}")
print(f"Relationships: {relationships:,}")


if nodes == 74062 and relationships == 150000:

    print()
    print("Verification successful!")

else:

    print()
    print("WARNING: Dataset size does not match expected values!")


driver.close()
