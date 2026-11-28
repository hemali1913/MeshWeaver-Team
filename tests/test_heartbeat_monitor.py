"""
Week 3 tests for MeshWeaver heartbeat monitoring.
"""

import asyncio
import socket
import unittest

from routing.heartbeat_monitor import check_peer


class MockPeer(asyncio.DatagramProtocol):
    """Simulates a peer that responds to heartbeat requests."""

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        response = {
            "type": "PONG",
            "node_id": "test-peer",
            "status": "success",
            "message": "Peer is active"
        }

        import json
        self.transport.sendto(json.dumps(response).encode("utf-8"), addr)


class TestHeartbeatMonitor(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        loop = asyncio.get_running_loop()

        self.transport, self.protocol = (
            await loop.create_datagram_endpoint(
                MockPeer,
                local_addr=("127.0.0.1", 0)
            )
        )

        self.port = self.transport.get_extra_info("sockname")[1]

    async def asyncTearDown(self):
        self.transport.close()

    async def test_active_peer_responds_to_heartbeat(self):
        peer = {
            "node_id": "test-peer",
            "host": "127.0.0.1",
            "port": self.port,
            "last_seen": 0.0,
            "available": True,
            "missed_heartbeats": 0
        }

        result = await check_peer(peer, timeout=1)

        self.assertTrue(result)
        self.assertTrue(peer["available"])
        self.assertGreater(peer["last_seen"], 0)
        self.assertEqual(peer["missed_heartbeats"], 0)

    async def test_failed_peer_becomes_unavailable(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 0))
        unused_port = sock.getsockname()[1]
        sock.close()

        peer = {
            "node_id": "offline-peer",
            "host": "127.0.0.1",
            "port": unused_port,
            "last_seen": 0.0,
            "available": True,
            "missed_heartbeats": 0
        }

        for attempt in range(3):
            result = await check_peer(peer, timeout=0.05)
            self.assertFalse(result)

            if attempt < 2:
                self.assertTrue(peer["available"])

        self.assertFalse(peer["available"])
        self.assertEqual(peer["missed_heartbeats"], 3)


if __name__ == "__main__":
    unittest.main()