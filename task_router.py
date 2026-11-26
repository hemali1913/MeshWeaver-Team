
"""
MeshWeaver - Week 3
Task Routing Algorithm
Team Member: Hemali Kachhad
"""

from routing_table import RoutingTable


class TaskRouter:

    def __init__(self, routing_table=None):

        # Connect with existing DHT Routing Table
        if routing_table is None:
            self.routing_table = RoutingTable()
        else:
            self.routing_table = routing_table

        print("Task Router initialized successfully.")

    def get_registered_nodes(self):

        # Get all registered nodes
        nodes = self.routing_table.get_all_nodes()

        return nodes

    def display_registered_nodes(self):

        nodes = self.get_registered_nodes()

        print("\n========== TASK ROUTER ==========")

        if not nodes:
            print("No nodes available.")

        else:
            for node in nodes:

                print("Node ID:", node["node_id"])
                print("Host:", node["host"])
                print("Port:", node["port"])
                print("--------------------------------")

        print("Total Nodes:", len(nodes))
        print("=================================")


if __name__ == "__main__":

    # Create routing table
    routing_table = RoutingTable()

    # Add sample nodes
    node1 = {
        "node_id": "node001",
        "host": "127.0.0.1",
        "port": 5001
    }

    node2 = {
        "node_id": "node002",
        "host": "127.0.0.1",
        "port": 5002
    }

    routing_table.add_node(node1)
    routing_table.add_node(node2)

    # Initialize Task Router
    router = TaskRouter(routing_table)

    # Display registered nodes
    router.display_registered_nodes()
