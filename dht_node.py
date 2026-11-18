
import secrets


class DHTNode:

    def __init__(self, host="127.0.0.1", port=5001):

        # Generate a unique 160-bit Kademlia Node ID
        self.node_id = secrets.token_hex(20)

        # Store node network details
        self.host = host
        self.port = port

        # Store information about discovered nodes
        self.routing_table = {}

    def calculate_distance(self, other_node_id):

        # Convert hexadecimal Node IDs into integers
        node1 = int(self.node_id, 16)
        node2 = int(other_node_id, 16)

        # Calculate XOR distance
        distance = node1 ^ node2

        return distance

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
        print("Routing Table:", self.routing_table)
        print("==============================")


if __name__ == "__main__":

    # Create two DHT nodes
    node1 = DHTNode(port=5001)
    node2 = DHTNode(port=5002)

    # Display node information
    print("\nNODE 1 INFORMATION")
    node1.display_node_info()

    print("\nNODE 2 INFORMATION")
    node2.display_node_info()

    # Calculate XOR distance
    distance = node1.calculate_distance(node2.node_id)

    print("\n========== XOR DISTANCE ==========")
    print("Node 1 ID:", node1.node_id)
    print("Node 2 ID:", node2.node_id)
    print("XOR Distance:", distance)
    print("==================================")
