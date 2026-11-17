import asyncio
import json


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
CLIENT_NAME = "babu-test-client"
TIMEOUT = 5


class UDPTestClient(asyncio.DatagramProtocol):

    def __init__(self):
        self.transport = None
        self.response_received = None

    def connection_made(self, transport):
        self.transport = transport

        message = {
            "type": "PING",
            "node_id": CLIENT_NAME
        }

        data = json.dumps(message).encode("utf-8")

        print("Sending PING to server...")
        print("Message:", message)

        transport.sendto(data)

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode("utf-8"))

            print("\nReceived response from server:")
            print("Message:", message)

            if message.get("type") == "PONG":
                print("\nPASS: PING → PONG")
                self.response_received = True
            else:
                print("\nFAIL: Expected PONG")
                self.response_received = False

        except Exception as error:
            print("\nFAIL: Could not decode server response")
            print("Error:", error)
            self.response_received = False

        self.transport.close()

    def error_received(self, exc):
        print("\nSocket error:", exc)
        self.response_received = False

    def connection_lost(self, exc):
        pass


async def main():

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPTestClient(),
        remote_addr=(SERVER_IP, SERVER_PORT)
    )

    try:
        await asyncio.sleep(TIMEOUT)

        if protocol.response_received is None:
            print("\nFAIL: No response received from server")
            print("The server may be stopped or unreachable.")

    finally:
        if not transport.is_closing():
            transport.close()


if __name__ == "__main__":
    asyncio.run(main())