 
# MeshWeaver Week 1 - UDP Server Module

## 1. Scope

This module implements the server-side Week 1 networking assignment.

Features:
- Asynchronous UDP server using asyncio.
- Configurable server IP address and port.
- Sender address identification.
- UTF-8 JSON decoding and validation.
- PING/PONG request-response mechanism.
- ERROR responses for malformed and unsupported messages.
- Basic socket error reporting.
- Message and response counters.
- Integration with the team's UDP client.

Task serialization is outside the scope of this module. The team must agree on the task message schema before the server handles serialized tasks.

## 2. Project Structure

```text
MeshWeaver-Team/
├── network/
│   ├── __init__.py
│   ├── network_server.py
│   └── network_client.py
├── tests/
│   ├── test_network_server.py
│   └── test_network_integration.py
└── docs/
    └── week1_server_documentation.md
```

## 3. Server Configuration

Default configuration:
- IP address: 127.0.0.1
- UDP port: 5000

Environment variables:
- MESHWEAVER_SERVER_IP
- MESHWEAVER_SERVER_PORT

Run from the repository root:

```bash
python -m network.network_server
```

For Windows PowerShell, custom configuration can be set using:

```powershell
$env:MESHWEAVER_SERVER_IP = "127.0.0.1"
$env:MESHWEAVER_SERVER_PORT = "5000"
python -m network.network_server
```

For network-wide access, the server may listen on 0.0.0.0. Clients must connect using the server machine's actual network IP.

## 4. Message Contract

### PING Request

```json
{
  "type": "PING",
  "node_id": "hemali-node"
}
```

### PONG Response

```json
{
  "type": "PONG",
  "node_id": "meshweaver-server",
  "status": "success",
  "message": "Server is active"
}
```

### ERROR Response

Malformed JSON, invalid payloads and unsupported message types receive an ERROR response.

```json
{
  "type": "ERROR",
  "node_id": "meshweaver-server",
  "status": "failed",
  "message": "Invalid JSON message"
}
```

## 5. Client-Server Integration

The UDP client and server communicate through localhost using UDP port 5000.

The client:
1. Creates a UDP endpoint.
2. Sends a JSON PING request.
3. Waits for the server response.
4. Validates the response type.
5. Reports successful PONG reception or a timeout.

The server:
1. Receives the UDP datagram.
2. Identifies the sender address.
3. Decodes and validates the JSON message.
4. Processes the PING request.
5. Sends a JSON PONG response.

### Running the integration

Open two separate terminals from the repository root.

Terminal 1 - Start server:

```bash
python -m network.network_server
```

Terminal 2 - Start client:

```bash
python -m network.network_client
```

Expected client result:

```text
Success! PONG received.
```

## 6. Testing

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

Run the integration test separately:

```bash
python -m unittest tests.test_network_integration -v
```

The test suite covers:
- PING/PONG responses.
- Unknown message types.
- Invalid JSON payloads.
- Invalid UTF-8 messages.
- Non-object JSON payloads.
- Message validation edge cases.
- Client-server UDP communication.

The automated integration test starts the server on an available local UDP port, sends a PING request and verifies the PONG response.

## 7. Integration Status

The team's actual UDP client was integrated with the server.

Manual client-server communication was verified successfully.

The automated UDP integration test also passed, confirming:
- PING request received.
- PONG response generated.
- Successful communication between UDP endpoints.

## 8. Limitations and Future Scope

- Task serialization is not yet integrated.
- A common task message schema must be agreed upon by the team.
- Further network-wide testing can be performed using LAN addresses.
- Additional protocol messages can be introduced in later weeks.

## 9. Conclusion

The Week 1 UDP server module implements asynchronous UDP communication, JSON message validation, PING/PONG handling and error responses.

The server has been integrated with the team's UDP client and verified through manual communication and automated integration testing.
