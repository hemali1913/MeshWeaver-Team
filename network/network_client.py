
import asyncio
import json

# Server configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

# Client configuration
CLIENT_NAME = "hemali-node"


class UDPClient(asyncio.DatagramProtocol):

    def connection_made(self, transport):
        self.transport = transport
        print("UDP Client is ready.")

    def error_received(self, exc):
        print("Error:", exc)


async def start_client():

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        UDPClient,
        local_addr=("127.0.0.1", 0)
    )

    try:
        message = {
            "type": "PING",
            "node_id": CLIENT_NAME
        }

        data = json.dumps(message).encode()

        transport.sendto(data, (SERVER_IP, SERVER_PORT))

        print("PING message sent successfully!")
        print("Message:", message)

    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(start_client())
