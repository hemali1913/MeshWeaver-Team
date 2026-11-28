"""
MeshWeaver - Week 3 Heartbeat Monitor
Checks peer availability using UDP PING/PONG messages.
"""

import asyncio
import json
import time


async def check_peer(peer, timeout=3):
    """
    Check whether a peer is active using a UDP heartbeat.

    Returns True if a valid PONG is received.
    Returns False if the peer does not respond.
    """

    loop = asyncio.get_running_loop()
    response_future = loop.create_future()

    class HeartbeatProtocol(asyncio.DatagramProtocol):

        def __init__(self):
            self.transport = None

        def connection_made(self, transport):
            self.transport = transport

        def datagram_received(self, data, addr):
            try:
                message = json.loads(data.decode("utf-8"))

                if (
                    isinstance(message, dict)
                    and message.get("type") == "PONG"
                    and not response_future.done()
                ):
                    response_future.set_result(message)

            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        def error_received(self, exc):
            if not response_future.done():
                response_future.set_exception(exc)

    transport = None

    try:
        transport, protocol = await loop.create_datagram_endpoint(
            HeartbeatProtocol,
            local_addr=("0.0.0.0", 0)
        )

        message = {
            "type": "PING",
            "node_id": "meshweaver-heartbeat"
        }

        transport.sendto(
            json.dumps(message).encode("utf-8"),
            (peer["host"], peer["port"])
        )

        response = await asyncio.wait_for(
            response_future,
            timeout=timeout
        )

        if response.get("status") == "success":
            peer["available"] = True
            peer["last_seen"] = time.time()
            peer["missed_heartbeats"] = 0
            return True

        return False

    except (asyncio.TimeoutError, OSError, ValueError):
        missed = peer.get("missed_heartbeats", 0) + 1
        peer["missed_heartbeats"] = missed

        if missed >= 3:
            peer["available"] = False

        return False

    finally:
        if transport is not None:
            transport.close()