import pytest
from task_serializer import serialize_task, deserialize_task

def test_serialization_deserialization():
    """
    Test case to verify if a function with arguments can be 
    successfully serialized, deserialized, and executed correctly.
    """
    # A sample test function
    def multiply(x, y):
        return x * y

    # 1. Test Serialization
    serialized = serialize_task(multiply, args=(4, 5))
    assert isinstance(serialized, bytes), "Serialized output should be bytes"

    # 2. Test Deserialization
    fn, args, kwargs = deserialize_task(serialized)
    
    # 3. Test Execution
    result = fn(*args, **kwargs)
    assert result == 20, f"Expected 20, but got {result}"

def test_with_default_arguments():
    """
    Test case to verify handling when args or kwargs are None/empty.
    """
    def say_hello():
        return "Hello, MeshWeaver!"

    serialized = serialize_task(say_hello)
    fn, args, kwargs = deserialize_task(serialized)
    
    assert fn(*args, **kwargs) == "Hello, MeshWeaver!"