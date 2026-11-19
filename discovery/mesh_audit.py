import sys
from pathlib import Path

# Find dht_node.py from the project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dht_node import DHTNode


def create_nodes(count):
    nodes = []

    for i in range(count):
        port = 5001 + i
        node = DHTNode(host="127.0.0.1", port=port)
        nodes.append(node)

    return nodes


def audit_nodes(nodes):
    print("\n========== MESH NODE AUDIT ==========")
    print(f"Nodes created: {len(nodes)}\n")

    node_ids = set()
    ports = set()

    for i, node in enumerate(nodes, start=1):
        node_ids.add(node.node_id)
        ports.add(node.port)

        print(f"Node-{i}")
        print(f"  Node ID: {node.node_id}")
        print(f"  Host: {node.host}")
        print(f"  Port: {node.port}")
        print(f"  Routing Table: {node.routing_table}")
        print()

    print("========== AUDIT SUMMARY ==========")

    if len(node_ids) == len(nodes):
        print("PASS: All node IDs are unique")
    else:
        print("FAIL: Duplicate node IDs detected")

    if len(ports) == len(nodes):
        print("PASS: All node ports are unique")
    else:
        print("FAIL: Duplicate node ports detected")

    print("NOTE: Automatic peer discovery is not implemented yet.")


if __name__ == "__main__":
    nodes = create_nodes(10)
    audit_nodes(nodes)