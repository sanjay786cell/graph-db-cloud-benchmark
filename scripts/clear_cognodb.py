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
    result = session.run("""
        MATCH (n)
        DETACH DELETE n
        RETURN count(n) AS deleted
    """)

    record = result.single()

    print(f"Deleted nodes: {record['deleted']}")


driver.close()
