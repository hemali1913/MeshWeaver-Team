
# MeshWeaver - Day 6 Testing Report

## Objective
To test UDP client-server communication and verify error handling and timeout behaviour.

## Tests Performed

### 1. PING/PONG Integration Test
- Client sent a PING message.
- Sample UDP server received the message.
- Server returned a PONG response.
- Result: PASS

### 2. Timeout Test
- Server was stopped.
- Client sent a PING message.
- Client displayed a timeout message after 5 seconds.
- Result: PASS

### 3. Invalid Message Test
- Sent an unsupported HELLO message.
- Server returned an ERROR response.
- Result: PASS

## Conclusion
All three tests were successful.
UDP communication, timeout handling and unknown message handling were verified.

Note: The server used for testing was a temporary sample server. The main contribution was focused on the UDP client.
