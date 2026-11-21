"""Unit tests for the MeshWeaver Week 1 UDP server."""

import json
import unittest
import os
import subprocess
import sys

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
        self.assertEqual(self.server.invalid_messages, 1)
        self.assertEqual(self.server.errors_sent, 1)

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
        self.assertEqual(self.server.ping_requests, 1)
        self.assertEqual(self.server.invalid_messages, 0)
        self.assertEqual(self.server.errors_sent, 0)

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



class UDPServerLoggingTests(unittest.TestCase):

    def setUp(self):
        self.server = UDPServer()
        self.transport = FakeTransport()
        self.server.transport = self.transport
        self.client = ("127.0.0.1", 54321)

    def test_response_generates_info_log(self):
        with self.assertLogs(level="INFO") as captured:
            self.server._send_response(
                {"type": "PONG"}, self.client
            )

        self.assertTrue(
            any("Sent response" in message
                for message in captured.output)
        )

    def test_udp_socket_error_generates_error_log(self):
        with self.assertLogs(level="ERROR") as captured:
            self.server.error_received(
                OSError("Test socket error")
            )

        self.assertTrue(
            any("UDP socket error" in message
                for message in captured.output)
        )

    def test_connection_lost_logs_traffic_statistics(self):
        self.server.messages_received = 5
        self.server.responses_sent = 4
        self.server.ping_requests = 3

        with self.assertLogs(level="INFO") as captured:
            self.server.connection_lost(None)

        output = "\n".join(captured.output)

        self.assertIn("Messages received: 5", output)
        self.assertIn("Responses sent: 4", output)
        self.assertIn("PING requests: 3", output)




class UDPServerTransportTests(unittest.TestCase):

    def setUp(self):
        self.server = UDPServer()
        self.client = ("127.0.0.1", 54321)

    def test_missing_transport_generates_warning(self):
        self.server.transport = None

        with self.assertLogs(level="WARNING") as captured:
            self.server._send_response(
                {"type": "PONG"}, self.client
            )

        self.assertIn(
            "UDP transport is not available",
            captured.output[0]
        )
        self.assertEqual(self.server.responses_sent, 0)

    def test_json_encoding_error_generates_error_log(self):
        self.server.transport = FakeTransport()

        with self.assertLogs(level="ERROR") as captured:
            self.server._send_response(
                {"type": object()}, self.client
            )

        self.assertIn(
            "Response JSON encoding error",
            captured.output[0]
        )
        self.assertEqual(self.server.responses_sent, 0)

    def test_udp_send_error_generates_error_log(self):
        class FailingTransport:
            def sendto(self, data, addr):
                raise OSError("Test send failure")

        self.server.transport = FailingTransport()

        with self.assertLogs(level="ERROR") as captured:
            self.server._send_response(
                {"type": "PONG"}, self.client
            )

        self.assertIn(
            "UDP sending error",
            captured.output[0]
        )
        self.assertEqual(self.server.responses_sent, 0)

class ServerConfigurationTests(unittest.TestCase):

    def run_server_import(self, port):
        env = os.environ.copy()
        env["MESHWEAVER_SERVER_PORT"] = port

        return subprocess.run(
            [sys.executable, "-c", "import network.network_server"],
            env=env,
            capture_output=True,
            text=True
        )
    def test_non_numeric_port_is_rejected(self):
        result = self.run_server_import("abc")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be an integer", result.stderr)
    def test_port_above_range_is_rejected(self):
        result = self.run_server_import("70000")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("between 1 and 65535", result.stderr)
    def test_zero_port_is_rejected(self):
        result = self.run_server_import("0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("between 1 and 65535", result.stderr)
    def test_valid_port_is_accepted(self):
        result = self.run_server_import("5000")
        self.assertEqual(result.returncode, 0, result.stderr)
if __name__ == "__main__":
    unittest.main()
