
import secrets
from routing_table import RoutingTable


class DHTNode:

    def __init__(self, host="127.0.0.1", port=5001):

        # Generate a unique 160-bit Kademlia Node ID
        self.node_id = secrets.token_hex(20)

        # Store node network details
        self.host = host
        self.port = port

        # Initialize routing table
        self.routing_table = RoutingTable()

    def calculate_distance(self, other_node_id):

        node1 = int(self.node_id, 16)
        node2 = int(other_node_id, 16)

        return node1 ^ node2

    def add_to_routing_table(self, node_info):

        return self.routing_table.add_node(node_info)

    def remove_from_routing_table(self, node_id):

        return self.routing_table.remove_node(node_id)

    def get_node_info(self):

        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port
        }

    def display_node_info(self):

        print("========== DHT NODE ==========")
        print("Node ID:", self.node_id)
        print("Host:", self.host)
        print("Port:", self.port)

        self.routing_table.display_table()

        print("==============================")


if __name__ == "__main__":

    node1 = DHTNode(port=5001)
    node2 = DHTNode(port=5002)

    print("\nAdding Node 2 to Node 1 Routing Table")
    node1.add_to_routing_table(node2.get_node_info())

    print("\nNODE 1 INFORMATION")
    node1.display_node_info()

    print("\nNODE 2 INFORMATION")
    node2.display_node_info()

    distance = node1.calculate_distance(node2.node_id)

    print("\n========== XOR DISTANCE ==========")
    print("XOR Distance:", distance)
    print("==================================")
