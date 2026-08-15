import csv
import gzip
from pathlib import Path


RAW_FILE = Path("data/raw/pokec_relationships.txt.gz")
OUTPUT_DIR = Path("data/processed")

TARGET_RELATIONSHIPS = 150_000


def prepare_dataset():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    edges_file = OUTPUT_DIR / "relationships.csv"
    nodes_file = OUTPUT_DIR / "nodes.csv"

    edges = []
    nodes = set()

    print(f"Reading: {RAW_FILE}")
    print(f"Target relationships: {TARGET_RELATIONSHIPS:,}")

    with gzip.open(RAW_FILE, "rt") as file:

        for line_number, line in enumerate(file):

            if len(edges) >= TARGET_RELATIONSHIPS:
                break

            line = line.strip()

            if not line:
                continue

            source, target = line.split()

            source = int(source)
            target = int(target)

            edges.append((source, target))

            nodes.add(source)
            nodes.add(target)

    print()
    print("Dataset prepared")
    print("----------------")
    print(f"Nodes:         {len(nodes):,}")
    print(f"Relationships: {len(edges):,}")

    # Write nodes
    with nodes_file.open("w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(["id"])

        for node_id in sorted(nodes):
            writer.writerow([node_id])

    # Write relationships
    with edges_file.open("w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(["source", "target"])

        for source, target in edges:
            writer.writerow([source, target])

    print()
    print(f"Nodes written to: {nodes_file}")
    print(f"Relationships written to: {edges_file}")


if __name__ == "__main__":
    prepare_dataset()
