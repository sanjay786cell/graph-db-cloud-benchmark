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

    print("Adding group property...")

    session.run("""
        MATCH (p:Person)
        SET p.group = p.id % 100
    """).consume()

    print("Group property added.")


driver.close()
