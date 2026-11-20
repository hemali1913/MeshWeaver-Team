
import unittest
from unittest.mock import patch, MagicMock
import json

from dht_node import DHTNode
from node_discovery import NodeDiscovery


class TestNodeDiscovery(unittest.TestCase):

    def setUp(self):
        self.node = DHTNode(host="127.0.0.1", port=5001)
        self.discovery = NodeDiscovery(self.node)

        self.bootstrap_node = {
            "node_id": "4c224b932076caa67ff73cae8b53905e9865144e",
            "host": "127.0.0.1",
            "port": 5000
        }

    @patch("node_discovery.socket.socket")
    def test_successful_discovery(self, mock_socket):
        mock_client = MagicMock()
        mock_socket.return_value = mock_client

        response = {
            "type": "JOIN_RESPONSE",
            "status": "success",
            "node_info": self.bootstrap_node
        }

        mock_client.recvfrom.return_value = (
            json.dumps(response).encode("utf-8"),
            ("127.0.0.1", 5000)
        )

        result = self.discovery.discover_node("127.0.0.1", 5000)

        self.assertTrue(result)
        self.assertIsNotNone(
            self.node.routing_table.get_node(
                self.bootstrap_node["node_id"]
            )
        )

    @patch("node_discovery.socket.socket")
    def test_invalid_response(self, mock_socket):
        mock_client = MagicMock()
        mock_socket.return_value = mock_client

        response = {"type": "INVALID"}

        mock_client.recvfrom.return_value = (
            json.dumps(response).encode("utf-8"),
            ("127.0.0.1", 5000)
        )

        result = self.discovery.discover_node("127.0.0.1", 5000)

        self.assertFalse(result)

    @patch("node_discovery.socket.socket")
    def test_discovery_timeout(self, mock_socket):
        mock_client = MagicMock()
        mock_socket.return_value = mock_client

        mock_client.recvfrom.side_effect = TimeoutError()

        result = self.discovery.discover_node("127.0.0.1", 5000)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
