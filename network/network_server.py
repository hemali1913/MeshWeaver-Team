"""
MeshWeaver - Week 1 UDP Networking Server
File: network/network_server.py

Receives UTF-8 JSON datagrams and responds to PING requests with PONG.
Unknown message types and malformed payloads receive a JSON ERROR response.

Run from the repository root:
    python -m network.network_server

Optional configuration:
    MESHWEAVER_SERVER_IP=127.0.0.1
    MESHWEAVER_SERVER_PORT=5000
"""

import asyncio
import json
import os
from typing import Any, Optional, Tuple

SERVER_IP = os.getenv("MESHWEAVER_SERVER_IP", "127.0.0.1")

try:
    SERVER_PORT = int(os.getenv("MESHWEAVER_SERVER_PORT", "5000"))
except ValueError:
    raise ValueError("MESHWEAVER_SERVER_PORT must be an integer.")

if not 1 <= SERVER_PORT <= 65535:
    raise ValueError("MESHWEAVER_SERVER_PORT must be between 1 and 65535.")

SERVER_NAME = "meshweaver-server"
MAX_DATAGRAM_SIZE = 65507


class UDPServer(asyncio.DatagramProtocol):
    """Receive JSON messages and send appropriate UDP responses."""

    def __init__(self) -> None:
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.messages_received = 0
        self.responses_sent = 0
        self.ping_requests = 0
        self.invalid_messages = 0
        self.errors_sent = 0
        

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called by asyncio after the UDP endpoint is created."""
        self.transport = transport  # type: ignore[assignment]
        address = transport.get_extra_info("sockname")
        print("\n" + "=" * 58)
        print("MeshWeaver UDP Server is running")
        print(f"Address : {address[0]}")
        print(f"Port    : {address[1]}")
        print("Waiting for client messages...")
        print("=" * 58 + "\n")

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Decode and process one incoming UDP datagram."""
        self.messages_received += 1
        print(f"\n[{self.messages_received}] Datagram received from {addr}")

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

        print("Received message:", message)
        self._handle_message(message, addr)

    def _handle_message(
        self, message: dict, addr: Tuple[str, int]
    ) -> None:
        """Choose a response based on the incoming message type."""
        message_type = message.get("type")

        if message_type == "PING":
            self.ping_requests += 1
            response = {
                "type": "PONG",
                "node_id": SERVER_NAME,
                "status": "success",
                "message": "Server is active",
            }
            self._send_response(response, addr)
        else:
            self.invalid_messages += 1
            self._send_error(
                f"Unsupported message type: {message_type!r}", addr
            )

    def _send_error(self, error_message: str, addr: Tuple[str, int]) -> None:
        """Send a consistent JSON error response to the client."""
        response = {
            "type": "ERROR",
            "node_id": SERVER_NAME,
            "status": "failed",
            "message": error_message,
        }
        self.errors_sent += 1
        self._send_response(response, addr)

    def _send_response(
        self, response: dict, addr: Tuple[str, int]
    ) -> None:
        """Encode a response as JSON and send it to the client."""
        if self.transport is None:
            print("Cannot send response: UDP transport is not available.")
            return

        try:
            payload = json.dumps(response).encode("utf-8")
            self.transport.sendto(payload, addr)
            self.responses_sent += 1
            print("Sent response:", response)
        except (TypeError, ValueError) as exc:
            print("Response JSON encoding error:", exc)
        except OSError as exc:
            print("UDP sending error:", exc)

    def error_received(self, exc: Exception) -> None:
        """Report asynchronous UDP socket errors."""
        print("UDP socket error:", exc)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """Report that the UDP transport has closed."""
        print("\nUDP server connection closed.")
        if exc is not None:
            print("Connection closed with error:", exc)
        print(f"Messages received : {self.messages_received}")
        print(f"Responses sent    : {self.responses_sent}")
        print(f"PING requests      : {self.ping_requests}")
        print(f"Invalid messages   : {self.invalid_messages}")
        print(f"Error responses    : {self.errors_sent}")


async def start_server(
    host: str = SERVER_IP, port: int = SERVER_PORT
) -> None:
    """Create the UDP endpoint and keep the server alive."""
    loop = asyncio.get_running_loop()
    transport, _protocol = await loop.create_datagram_endpoint(
        UDPServer, local_addr=(host, port)
    )
    try:
        await asyncio.Future()
    finally:
        transport.close()


def main() -> None:
    """Application entry point."""
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nMeshWeaver UDP Server stopped by user.")
    except (OSError, ValueError) as exc:
        print(f"\nCould not start the UDP server: {exc}")
        print(
            f"Check SERVER_IP and UDP port {SERVER_PORT}; "
            "the port may already be in use."
        )


if __name__ == "__main__":
    main()
