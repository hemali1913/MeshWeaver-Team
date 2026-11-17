
import asyncio
import json
import unittest

from network.network_server import UDPServer


class TestClientProtocol(asyncio.DatagramProtocol):
    """Temporary UDP client for integration testing."""

    def __init__(self, loop):
        self.response_future = loop.create_future()

    def datagram_received(self, data, addr):
        try:
            response = json.loads(data.decode("utf-8"))

            if not self.response_future.done():
                self.response_future.set_result(response)

        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            if not self.response_future.done():
                self.response_future.set_exception(exc)


class UDPIntegrationTests(unittest.IsolatedAsyncioTestCase):

    async def test_client_ping_receives_server_pong(self):
        loop = asyncio.get_running_loop()

        # Start the UDP server on an available port.
        server_transport, _ = await loop.create_datagram_endpoint(
            UDPServer,
            local_addr=("127.0.0.1", 0),
        )

        try:
            server_address = server_transport.get_extra_info("sockname")

            # Create a separate UDP client.
            client_transport, client_protocol = (
                await loop.create_datagram_endpoint(
                    lambda: TestClientProtocol(loop),
                    local_addr=("127.0.0.1", 0),
                )
            )

            try:
                ping_message = {
                    "type": "PING",
                    "node_id": "integration-test-client",
                }

                client_transport.sendto(
                    json.dumps(ping_message).encode("utf-8"),
                    server_address,
                )

                response = await asyncio.wait_for(
                    client_protocol.response_future,
                    timeout=2,
                )

                self.assertEqual(response["type"], "PONG")
                self.assertEqual(
                    response["node_id"], "meshweaver-server"
                )
                self.assertEqual(response["status"], "success")

            finally:
                client_transport.close()

        finally:
            server_transport.close()


if __name__ == "__main__":
    unittest.main()
