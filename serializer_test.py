import socket
from task_serializer import serialize_task, deserialize_task  

def add(a, b):
    return a + b     


serialized_data = serialize_task(add, args=(5, 10)) 

print("Serialization successful:", isinstance(serialized_data, bytes))
print("Serialized data size:", len(serialized_data), "bytes")

# Create local sockets
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 0))
server.listen(1)

port = server.getsockname()[1]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", port))

connection, address = server.accept()

# Send serialized data
client.sendall(serialized_data)

# Receive serialized data
received_data = connection.recv(4096)

print("Socket transfer successful:", received_data == serialized_data)

# Close sockets
client.close()
connection.close()
server.close()

# Deserialize the received data
restored_func, restored_args, restored_kwargs = deserialize_task(received_data)

# Execute the restored task
result = restored_func(*restored_args, **restored_kwargs)

print("Deserialization successful:", restored_func is not None)
print("Restored task result:", result)
print("Task result correct:", result == 15)

print("\n========== TEST SUMMARY ==========")

if (
    isinstance(serialized_data, bytes)
    and received_data == serialized_data
    and restored_func is not None
    and result == 15
):
    print("PASS: Serialization")
    print("PASS: Socket Transfer")
    print("PASS: Deserialization")
    print("PASS: Task Execution")
    print("ALL TESTS PASSED")
else:
    print("TEST FAILED")