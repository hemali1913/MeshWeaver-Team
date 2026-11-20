
"""
MeshWeaver - Week 2 Day 4
UDP-based DHT Node Discovery
"""

import socket
import json

from dht_node import DHTNode


class NodeDiscovery:

    def __init__(self, node, timeout=5):
        self.node = node
        self.timeout = timeout

    def discover_node(self, bootstrap_host, bootstrap_port):

        print("\n========== NODE DISCOVERY ==========")
        print("Contacting Bootstrap Node...")

        try:
            client = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )

            client.settimeout(self.timeout)

            request = {
                "type": "JOIN",
                "node_info": self.node.get_node_info()
            }

            payload = json.dumps(request).encode("utf-8")

            client.sendto(
                payload,
                (bootstrap_host, bootstrap_port)
            )

            data, address = client.recvfrom(4096)

            response = json.loads(data.decode("utf-8"))

            client.close()

            if response.get("type") != "JOIN_RESPONSE":
                print("Discovery failed:", response)
                return False

            if response.get("status") != "success":
                print("Bootstrap node rejected request.")
                return False

            discovered_node = response.get("node_info")

            if not isinstance(discovered_node, dict):
                print("Invalid node information received.")
                return False

            required_fields = {"node_id", "host", "port"}

            if not required_fields.issubset(discovered_node):
                print("Incomplete node information.")
                return False

            node_id = discovered_node["node_id"]
            host = discovered_node["host"]
            port = discovered_node["port"]

            if not isinstance(node_id, str) or len(node_id) != 40:
                print("Invalid Node ID received.")
                return False

            try:
                int(node_id, 16)
                if not isinstance(host, str) or not host:
                    return False
                if not isinstance(port, int) or not 1 <= port <= 65535:
                    return False
            except ValueError:
                print("Invalid node information.")
                return False

            if node_id == self.node.node_id:
                print("Bootstrap node is the current node.")
                return False

            print("\nBootstrap Node Discovered!")
            print("Node ID:", node_id)
            print("Host:", host)
            print("Port:", port)

            added = self.node.add_to_routing_table(
                discovered_node
            )

            if added:
                print("Node added to Routing Table.")
            else:
                print("Node already exists in Routing Table.")

            print("====================================")

            return added

        except socket.timeout:
            print("Discovery timeout: Bootstrap node did not respond.")
            return False

        except (OSError, json.JSONDecodeError) as error:
            print("Discovery error:", error)
            return False

        finally:
            if "client" in locals():
                client.close()


if __name__ == "__main__":

    my_node = DHTNode(
        host="127.0.0.1",
        port=5001
    )

    discovery = NodeDiscovery(my_node)

    discovery.discover_node(
        bootstrap_host="127.0.0.1",
        bootstrap_port=5000
    )

    print("\nFINAL NODE INFORMATION")
    my_node.display_node_info()
