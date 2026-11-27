
"""
MeshWeaver - Week 3 Day 2
Task Router - CPU Load Management
Team Member: Hemali Kachhad
"""

from routing_table import RoutingTable


class TaskRouter:

    def __init__(self, routing_table=None):

        if routing_table is None:
            self.routing_table = RoutingTable()
        else:
            self.routing_table = routing_table

        # Store CPU load for each node
        self.cpu_loads = {}

        print("Task Router initialized successfully.")

    def get_registered_nodes(self):

        return self.routing_table.get_all_nodes()

    def update_cpu_load(self, node_id, cpu_load):

        # Validate CPU load value
        if isinstance(cpu_load, bool) or not isinstance(
            cpu_load, (int, float)
        ):
            print("Invalid CPU load. Must be a number.")
            return False

        if not 0 <= cpu_load <= 100:
            print("CPU load must be between 0 and 100.")
            return False

        # Check whether node is registered
        node = self.routing_table.get_node(node_id)

        if node is None:
            print("Node not found in routing table.")
            return False

        # Store CPU load
        self.cpu_loads[node_id] = cpu_load

        print("CPU load updated successfully.")
        return True

    def get_cpu_load(self, node_id):

        return self.cpu_loads.get(node_id)

    def display_cpu_loads(self):

        print("\n========== CPU LOAD STATUS ==========")

        nodes = self.get_registered_nodes()

        if not nodes:
            print("No nodes registered.")

        else:
            for node in nodes:

                node_id = node["node_id"]
                cpu_load = self.get_cpu_load(node_id)

                print("Node ID:", node_id)

                if cpu_load is None:
                    print("CPU Load: Not available")
                else:
                    print("CPU Load:", str(cpu_load) + "%")

                print("-----------------------------------")

        print("====================================")


if __name__ == "__main__":

    # Create routing table
    routing_table = RoutingTable()

    # Sample nodes
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

    node3 = {
        "node_id": "node003",
        "host": "127.0.0.1",
        "port": 5003
    }

    # Register nodes
    routing_table.add_node(node1)
    routing_table.add_node(node2)
    routing_table.add_node(node3)

    # Initialize Task Router
    router = TaskRouter(routing_table)

    # Update CPU loads
    router.update_cpu_load("node001", 75)
    router.update_cpu_load("node002", 25)
    router.update_cpu_load("node003", 60)

    # Display CPU loads
    router.display_cpu_loads()
