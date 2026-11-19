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

        info = node.get_node_info()

        print(f"  Node ID: {info['node_id']}")
        print(f"  Host: {info['host']}")
        print(f"  Port: {info['port']}")
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

    print("\n========== XOR DISTANCE AUDIT ==========")

    node_a = nodes[0]
    node_b = nodes[1]

    distance_ab = node_a.calculate_distance(node_b.node_id)
    distance_ba = node_b.calculate_distance(node_a.node_id)
    distance_self = node_a.calculate_distance(node_a.node_id)

    print(f"Distance A -> B: {distance_ab}")
    print(f"Distance B -> A: {distance_ba}")
    print(f"Distance A -> A: {distance_self}")

    if isinstance(distance_ab, int):
        print("PASS: XOR distance is an integer")
    else:
        print("FAIL: XOR distance is not an integer")

    if distance_ab == distance_ba:
        print("PASS: XOR distance is symmetric")
    else:
        print("FAIL: XOR distance is not symmetric")

    if distance_self == 0:
        print("PASS: Self-distance is zero")
    else:
        print("FAIL: Self-distance is not zero")

if __name__ == "__main__":
    nodes = create_nodes(10)
    audit_nodes(nodes)