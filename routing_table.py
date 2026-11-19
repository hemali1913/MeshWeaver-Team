
class RoutingTable:

    def __init__(self):
        # Store discovered nodes using Node ID as key
        self.nodes = {}

    def add_node(self, node_info):
        node_id = node_info["node_id"]

        # Prevent adding duplicate nodes
        if node_id in self.nodes:
            print("Node already exists in routing table.")
            return False

        self.nodes[node_id] = node_info

        print("Node added successfully.")
        return True

    def remove_node(self, node_id):

        if node_id in self.nodes:
            del self.nodes[node_id]
            print("Node removed successfully.")
            return True

        print("Node not found.")
        return False

    def get_node(self, node_id):

        return self.nodes.get(node_id)

    def get_all_nodes(self):

        return list(self.nodes.values())

    def display_table(self):

        print("\n========== ROUTING TABLE ==========")

        if not self.nodes:
            print("Routing table is empty.")

        else:
            for node_id, info in self.nodes.items():
                print("Node ID:", node_id)
                print("Host:", info["host"])
                print("Port:", info["port"])
                print("--------------------------------")

        print("Total Nodes:", len(self.nodes))
        print("===================================")
