
import asyncio
import json

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
CLIENT_NAME = "hemali-node"
TIMEOUT = 5


class UDPClient(asyncio.DatagramProtocol):

    def __init__(self):
        self.transport = None
        self.response_future = None

    def connection_made(self, transport):
        self.transport = transport
        print("UDP Client is ready.")

    def send_message(self, message, addr):
        try:
            data = json.dumps(message).encode()
            self.transport.sendto(data, addr)

            print("Message sent successfully:", message)

        except (TypeError, ValueError) as exc:
            print("Message encoding error:", exc)

        except OSError as exc:
            print("UDP sending error:", exc)

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode())

            print("Response received:", message)

            if self.response_future and not self.response_future.done():
                self.response_future.set_result(message)

        except (json.JSONDecodeError, UnicodeDecodeError):
            print("Invalid response received.")

    def error_received(self, exc):
        print("UDP Error:", exc)


async def start_client():

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        UDPClient,
        local_addr=("127.0.0.1", 0)
    )

    try:
        protocol.response_future = loop.create_future()

        message = {
            "type": "PING",
            "node_id": CLIENT_NAME
        }

        print("Sending PING message...")

        protocol.send_message(
            message,
            (SERVER_IP, SERVER_PORT)
        )

        try:
            response = await asyncio.wait_for(
                protocol.response_future,
                timeout=TIMEOUT
            )

            if response.get("type") == "PONG":
                print("Success! PONG received.")
            else:
                print("Unexpected response.")

        except asyncio.TimeoutError:
            print("Timeout! Server did not respond.")

    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(start_client())
