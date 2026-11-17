"""Unit tests for the MeshWeaver Week 1 UDP server."""

import json
import unittest

from network.network_server import UDPServer


class FakeTransport:
    def __init__(self):
        self.sent = []

    def sendto(self, data, addr):
        self.sent.append((data, addr))


class UDPServerTests(unittest.TestCase):
    def setUp(self):
        self.server = UDPServer()
        self.transport = FakeTransport()
        self.server.transport = self.transport
        self.client = ("127.0.0.1", 54321)

    def response(self):
        self.assertTrue(self.transport.sent)
        raw, address = self.transport.sent[-1]
        self.assertEqual(address, self.client)
        return json.loads(raw.decode("utf-8"))

    def test_ping_returns_pong(self):
        self.server.datagram_received(b'{"type":"PING"}', self.client)
        response = self.response()
        self.assertEqual(response["type"], "PONG")
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["node_id"], "meshweaver-server")

    def test_unknown_type_returns_error(self):
        self.server.datagram_received(b'{"type":"HELLO"}', self.client)
        response = self.response()
        self.assertEqual(response["type"], "ERROR")
        self.assertEqual(response["status"], "failed")

    def test_invalid_json_returns_error(self):
        self.server.datagram_received(b'{"type":', self.client)
        self.assertEqual(self.response()["message"], "Invalid JSON message")

    def test_invalid_utf8_returns_error(self):
        self.server.datagram_received(b"\xff\xfe", self.client)
        self.assertEqual(
            self.response()["message"], "Message must use UTF-8 encoding"
        )

    def test_non_object_json_returns_error(self):
        self.server.datagram_received(b'["PING"]', self.client)
        self.assertEqual(
            self.response()["message"], "Message must be a JSON object"
        )

    def test_message_counters_increment(self):
        self.server.datagram_received(b'{"type":"PING"}', self.client)
        self.assertEqual(self.server.messages_received, 1)
        self.assertEqual(self.server.responses_sent, 1)

    def test_missing_type_returns_error(self):
        self.server.datagram_received(b"{}", self.client)
        response = self.response()
        self.assertEqual(response["type"], "ERROR")
        self.assertIn("Unsupported message type", response["message"])

    def test_empty_type_returns_error(self):
        self.server.datagram_received(b'{"type":""}', self.client)
        response = self.response()
        self.assertEqual(response["type"], "ERROR")

    def test_numeric_type_returns_error(self):
        self.server.datagram_received(b'{"type":123}', self.client)
        response = self.response()
        self.assertEqual(response["type"], "ERROR")

    def test_list_type_returns_error(self):
        self.server.datagram_received(b'{"type":["PING"]}', self.client)
        response = self.response()
        self.assertEqual(response["type"], "ERROR")

    def test_null_json_returns_error(self):
        self.server.datagram_received(b"null", self.client)
        response = self.response()
        self.assertEqual(response["type"], "ERROR")
        self.assertEqual(response["message"], "Message must be a JSON object")

    def test_empty_datagram_returns_error(self):
        self.server.datagram_received(b"", self.client)
        response = self.response()
        self.assertEqual(response["type"], "ERROR")
        self.assertEqual(response["message"], "Invalid JSON message")


if __name__ == "__main__":
    unittest.main()
