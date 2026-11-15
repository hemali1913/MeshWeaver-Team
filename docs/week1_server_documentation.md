# MeshWeaver Week 1 – UDP Server Module

## Scope
This module implements the server-side Week 1 networking assignment:
- asyncio UDP endpoint
- sender address visibility
- UTF-8 JSON decoding and object validation
- PING → PONG
- ERROR responses for malformed/unsupported messages
- basic socket error reporting and message counters

Task serialization is intentionally outside this module. The team must agree
on the task message schema before the server handles serialized tasks.

## Run
From the repository root:

```bash
python -m network.network_server
```

Defaults: `127.0.0.1:5000`. Configure with environment variables:

```bash
MESHWEAVER_SERVER_IP=0.0.0.0 MESHWEAVER_SERVER_PORT=5000 python -m network.network_server
```

Use `0.0.0.0` only to listen on all interfaces; clients must connect to the
server machine's actual LAN IP. Allow UDP port 5000 through the firewall.

## Message contract
Request:

```json
{"type": "PING"}
```

Successful response:

```json
{
  "type": "PONG",
  "node_id": "meshweaver-server",
  "status": "success",
  "message": "Server is active"
}
```

Unknown message types and invalid payloads return an object with
`type: "ERROR"`, `status: "failed"`, and a human-readable `message`.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests exercise the protocol handler using a fake UDP transport. A final
end-to-end integration check should also be run with the team's actual
`network_client.py` before merging.

## Integration note
The PONG and ERROR fields preserve the uploaded starter code's response
contract. Client-side matching should use `type` (`PONG` / `ERROR`).
