
"""
MeshWeaver - Week 2 UDP Networking Server
Supports PING and JOIN requests for DHT Node Discovery.
"""

import asyncio
import json
import os
import secrets
from typing import Any, Optional, Tuple

SERVER_IP = os.getenv("MESHWEAVER_SERVER_IP", "127.0.0.1")
SERVER_PORT = int(os.getenv("MESHWEAVER_SERVER_PORT", "5000"))
SERVER_NAME = "meshweaver-server"
SERVER_NODE_ID = secrets.token_hex(20)
MAX_DATAGRAM_SIZE = 65507


class UDPServer(asyncio.DatagramProtocol):

    def __init__(self) -> None:
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.messages_received = 0
        self.responses_sent = 0

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]

        address = transport.get_extra_info("sockname")

        print("\n" + "=" * 58)
        print("MeshWeaver UDP Server is running")
        print(f"Node ID : {SERVER_NODE_ID}")
        print(f"Address : {address[0]}")
        print(f"Port    : {address[1]}")
        print("Supported messages: PING, JOIN")
        print("Waiting for client messages...")
        print("=" * 58 + "\n")

    def datagram_received(
        self, data: bytes, addr: Tuple[str, int]
    ) -> None:

        self.messages_received += 1
        print(f"\n[{self.messages_received}] Message received from {addr}")

        if len(data) > MAX_DATAGRAM_SIZE:
            self._send_error("Datagram is too large", addr)
            return

        try:
            message: Any = json.loads(data.decode("utf-8"))

        except UnicodeDecodeError:
            self._send_error("Message must use UTF-8 encoding", addr)
            return

        except json.JSONDecodeError:
            self._send_error("Invalid JSON message", addr)
            return

        if not isinstance(message, dict):
            self._send_error("Message must be a JSON object", addr)
            return

        print("Received:", message)
        self._handle_message(message, addr)

    def _handle_message(
        self, message: dict, addr: Tuple[str, int]
    ) -> None:

        message_type = message.get("type")

        if message_type == "PING":

            response = {
                "type": "PONG",
                "node_id": SERVER_NODE_ID,
                "status": "success",
                "message": "Server is active"
            }

            self._send_response(response, addr)

        elif message_type == "JOIN":

            response = {
                "type": "JOIN_RESPONSE",
                "status": "success",
                "node_info": {
                    "node_id": SERVER_NODE_ID,
                    "host": SERVER_IP,
                    "port": SERVER_PORT
                },
                "message": "Node discovery successful"
            }

            self._send_response(response, addr)

        else:
            self._send_error(
                f"Unsupported message type: {message_type!r}",
                addr
            )

    def _send_error(
        self, error_message: str, addr: Tuple[str, int]
    ) -> None:

        response = {
            "type": "ERROR",
            "node_id": SERVER_NODE_ID,
            "status": "failed",
            "message": error_message
        }

        self._send_response(response, addr)

    def _send_response(
        self, response: dict, addr: Tuple[str, int]
    ) -> None:

        if self.transport is None:
            print("Cannot send response: UDP transport unavailable.")
            return

        try:
            payload = json.dumps(response).encode("utf-8")
            self.transport.sendto(payload, addr)

            self.responses_sent += 1
            print("Sent response:", response)

        except (TypeError, ValueError) as exc:
            print("JSON encoding error:", exc)

        except OSError as exc:
            print("UDP sending error:", exc)

    def error_received(self, exc: Exception) -> None:
        print("UDP socket error:", exc)

    def connection_lost(self, exc: Optional[Exception]) -> None:

        print("\nUDP server connection closed.")

        if exc is not None:
            print("Connection error:", exc)

        print("Messages received:", self.messages_received)
        print("Responses sent:", self.responses_sent)


async def start_server(
    host: str = SERVER_IP,
    port: int = SERVER_PORT
) -> None:

    loop = asyncio.get_running_loop()

    transport, _protocol = await loop.create_datagram_endpoint(
        UDPServer,
        local_addr=(host, port)
    )

    try:
        await asyncio.Future()

    finally:
        transport.close()


def main() -> None:

    try:
        asyncio.run(start_server())

    except KeyboardInterrupt:
        print("\nMeshWeaver UDP Server stopped.")

    except (OSError, ValueError) as exc:
        print("\nCould not start UDP server:", exc)
        print("Check server IP and port:", SERVER_PORT)


if __name__ == "__main__":
    main()
