import asyncio
import json
import unittest

from network.network_client import UDPClient


class FakeTransport:
    def __init__(self):
        self.sent_data = []
        self.error = None

    def sendto(self, data, addr):
        if self.error:
            raise self.error
        self.sent_data.append((data, addr))


class UDPClientTests(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.client = UDPClient()
        self.transport = FakeTransport()
        self.address = ("127.0.0.1", 5000)
        self.client.connection_made(self.transport)
        self.client.response_future = self.loop.create_future()

    def tearDown(self):
        self.loop.close()

    def test_connection_made_sets_transport(self):
        self.assertIs(self.client.transport, self.transport)

    def test_send_message_sends_json_data(self):
        message = {"type": "PING", "node_id": "test-client"}

        self.client.send_message(message, self.address)

        sent_data, sent_address = self.transport.sent_data[-1]

        self.assertEqual(json.loads(sent_data.decode("utf-8")), message)
        self.assertEqual(sent_address, self.address)

    def test_send_message_handles_encoding_error(self):
        message = {"type": object()}

        self.client.send_message(message, self.address)

        self.assertEqual(self.transport.sent_data, [])

    def test_send_message_handles_udp_error(self):
        self.transport.error = OSError("UDP send failed")

        self.client.send_message({"type": "PING"}, self.address)

        self.assertEqual(self.transport.sent_data, [])

    def test_datagram_received_sets_response(self):
        data = b'{"type": "PONG"}'

        self.client.datagram_received(data, self.address)

        self.assertEqual(
            self.client.response_future.result(),
            {"type": "PONG"}
        )

    def test_datagram_received_handles_invalid_json(self):
        self.client.datagram_received(b"invalid", self.address)

        with self.assertRaises(json.JSONDecodeError):
            self.client.response_future.result()

    def test_datagram_received_handles_invalid_utf8(self):
        self.client.datagram_received(b"\xff", self.address)

        with self.assertRaises(UnicodeDecodeError):
            self.client.response_future.result()

    def test_datagram_received_rejects_non_object_json(self):
        self.client.datagram_received(b'["PING"]', self.address)

        with self.assertRaises(ValueError):
            self.client.response_future.result()

    def test_error_received_sets_exception(self):
        error = OSError("Network error")

        self.client.error_received(error)

        self.assertIs(self.client.response_future.exception(), error)

    def test_connection_lost_handles_error(self):
        error = OSError("Connection lost")

        self.client.connection_lost(error)


    def test_send_message_handles_unavailable_transport(self):
        client = UDPClient()

        client.send_message(
            {"type": "PING"},
            ("127.0.0.1", 5000)
        )

        self.assertIsNone(client.transport)

if __name__ == "__main__":
    unittest.main()
