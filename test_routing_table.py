
import unittest

from routing_table import RoutingTable


class TestRoutingTable(unittest.TestCase):

    def setUp(self):
        self.table = RoutingTable()

        self.node1 = {
            "node_id": "abc123",
            "host": "127.0.0.1",
            "port": 5001
        }

        self.node2 = {
            "node_id": "xyz456",
            "host": "127.0.0.1",
            "port": 5002
        }

    def test_add_node(self):
        self.assertTrue(self.table.add_node(self.node1))

    def test_duplicate_node(self):
        self.table.add_node(self.node1)
        self.assertFalse(self.table.add_node(self.node1))

    def test_remove_node(self):
        self.table.add_node(self.node1)
        self.assertTrue(self.table.remove_node("abc123"))

    def test_get_node(self):
        self.table.add_node(self.node1)
        self.assertEqual(
            self.table.get_node("abc123"),
            self.node1
        )

    def test_get_all_nodes(self):
        self.table.add_node(self.node1)
        self.table.add_node(self.node2)

        self.assertEqual(len(self.table.get_all_nodes()), 2)

    def test_remove_missing_node(self):
        self.assertFalse(self.table.remove_node("unknown"))

    def test_get_missing_node(self):
        self.assertIsNone(self.table.get_node("unknown"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
