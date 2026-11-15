import pytest
import cloudpickle
from task_serializer import (
    serialize_task, 
    deserialize_task, 
    TaskSerializationError, 
    TaskDeserializationError
)

def test_serialize_non_callable_raises_error():
    """
    Ensures that trying to serialize a non-callable object 
    correctly raises the custom TaskSerializationError.
    """
    with pytest.raises(TaskSerializationError):
        serialize_task("this_is_a_string_not_a_function", args=(10, 20))

def test_deserialize_invalid_type_raises_error():
    """
    Ensures that passing non-bytes data into deserialize_task 
    raises the custom TaskDeserializationError.
    """
    with pytest.raises(TaskDeserializationError):
        deserialize_task("invalid_raw_string_data")

def test_deserialize_corrupted_payload_structure():
    """
    Ensures that a serialized payload missing the expected 'func' 
    dictionary structure safely triggers TaskDeserializationError.
    """
    # Create a valid pickle of a dict that lacks the required 'func' key
    corrupted_payload = cloudpickle.dumps({"invalid_key": 42})
    
    with pytest.raises(TaskDeserializationError):
        deserialize_task(corrupted_payload)