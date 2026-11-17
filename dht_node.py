
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

    node = DHTNode()

    node.display_node_info()
