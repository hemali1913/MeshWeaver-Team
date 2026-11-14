import cloudpickle
import logging

# Configure basic logging for debugging task serialization flow
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TaskSerializationError(Exception):
    """Custom exception raised when task serialization fails."""
    pass

class TaskDeserializationError(Exception):
    """Custom exception raised when task deserialization or payload extraction fails."""
    pass


def serialize_task(func, args=None, kwargs=None):
    """
    Serializes a Python function along with its positional and keyword arguments 
    into a byte stream using cloudpickle, with robust error handling.
    """
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    
    if not callable(func):
        raise TaskSerializationError(f"Provided object '{func}' is not a callable function.")

    try:
        task_payload = {
            'func': func,
            'args': args,
            'kwargs': kwargs
        }
        serialized_bytes = cloudpickle.dumps(task_payload)
        logging.info(f"Successfully serialized task: {func.__name__} (Payload size: {len(serialized_bytes)} bytes)")
        return serialized_bytes
    
    except Exception as e:
        logging.error(f"Failed to serialize task {func.__name__}: {str(e)}")
        raise TaskSerializationError(f"Serialization failed due to: {str(e)}") from e


def deserialize_task(serialized_data):
    """
    Safely deserializes raw binary bytes back into the original executable function, 
    args, and kwargs with strict payload validation.
    """
    if not isinstance(serialized_data, bytes):
        raise TaskDeserializationError("Invalid payload type. Expected bytes for deserialization.")

    try:
        task_payload = cloudpickle.loads(serialized_data)
        
        # Validate payload structure
        if not isinstance(task_payload, dict) or 'func' not in task_payload:
            raise TaskDeserializationError("Corrupted payload structure: Missing function reference.")
            
        func = task_payload.get('func')
        args = task_payload.get('args', ())
        kwargs = task_payload.get('kwargs', {})
        
        logging.info("Successfully deserialized task payload.")
        return func, args, kwargs

    except Exception as e:
        logging.error(f"Failed to deserialize task payload: {str(e)}")
        raise TaskDeserializationError(f"Deserialization failed due to: {str(e)}") from e


if __name__ == "__main__":
    # Local validation block
    def sample_task(x, y):
        return x ** y

    packet = serialize_task(sample_task, args=(2, 3))
    fn, args, kwargs = deserialize_task(packet)
    print("Execution Result after Error Handling Integration:", fn(*args, **kwargs))