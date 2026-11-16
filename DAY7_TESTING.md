# Day 7 – UDP Networking Testing Report

## Project: MeshWeaver
**Week:** 1 – Networking Setup  
**Team Member:** Hemali Kachhad  
**Module:** UDP Client-Server Communication

## 1. Testing Objectives
- Verify UDP server startup.
- Test client-server PING/PONG communication.
- Verify client timeout handling.
- Test invalid JSON message handling.
- Test unsupported message type handling.

## 2. Test Results

| No. | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| 1 | Python syntax check | No syntax errors | No errors found | PASS |
| 2 | UDP server startup | Server starts successfully | Server started on port 5000 | PASS |
| 3 | PING/PONG communication | Server responds with PONG | PONG received successfully | PASS |
| 4 | Server unavailable | Client handles timeout | Timeout handled successfully | PASS |
| 5 | Invalid JSON message | Server returns ERROR | Invalid JSON error received | PASS |
| 6 | Unsupported message type | Server returns ERROR | Unsupported message error received | PASS |

## 3. Conclusion

All six UDP networking tests were completed successfully. The server correctly handles valid PING messages, invalid JSON messages, unsupported message types, and client timeout scenarios.

**Day 7 testing completed successfully.**