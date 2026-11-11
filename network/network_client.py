
import asyncio
import json

# Server configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

# Client configuration
CLIENT_NAME = "hemali-node"


async def start_client():
    print("MeshWeaver UDP Client")
    print("Client Name:", CLIENT_NAME)
    print("Server IP:", SERVER_IP)
    print("Server Port:", SERVER_PORT)
    print("Client setup completed!")


if __name__ == "__main__":
    asyncio.run(start_client())
