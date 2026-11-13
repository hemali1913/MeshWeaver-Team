
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
            data = json.dumps(message).encode("utf-8")
            self.transport.sendto(data, addr)

            print("Message sent successfully:", message)

        except (TypeError, ValueError) as exc:
            print("Message encoding error:", exc)

        except OSError as exc:
            print("UDP sending error:", exc)

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode("utf-8"))

            if not isinstance(message, dict):
                raise ValueError("Response must be a JSON object")

            print("Response received:", message)

            if self.response_future and not self.response_future.done():
                self.response_future.set_result(message)

        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            print("Invalid response received:", exc)

            if self.response_future and not self.response_future.done():
                self.response_future.set_exception(exc)

    def error_received(self, exc):
        print("UDP Error:", exc)

        if self.response_future and not self.response_future.done():
            self.response_future.set_exception(exc)

    def connection_lost(self, exc):
        if exc:
            print("Connection lost:", exc)


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
                print("Unexpected response:", response)

        except asyncio.TimeoutError:
            print("Timeout! Server did not respond.")

        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print("Communication error:", exc)

    finally:
        transport.close()


if __name__ == "__main__":
    try:
        asyncio.run(start_client())

    except KeyboardInterrupt:
        print("Client stopped by user.")

    except OSError as exc:
        print("Client startup error:", exc)
