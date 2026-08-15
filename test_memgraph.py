from neo4j import GraphDatabase

URI = "bolt://localhost:7689"

driver = GraphDatabase.driver(
    URI,
    auth=("", "")
)

try:
    with driver.session() as session:
        result = session.run("RETURN 1 AS result").single()
        print(f"Result: {result['result']}")
        print("Memgraph connection successful!")
finally:
    driver.close()
