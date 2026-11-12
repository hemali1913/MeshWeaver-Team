import cloudpickle

def serialize_task(func, args=None, kwargs=None):
    
    # Packs python func and it's arguments into byte format using cloudpickle
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    
    # Pack functions and arguments in a dictionary
    task_payload = {
        'func': func,
        'args': args,
        'kwargs': kwargs
    }
    
    # cloudpickle.dumps() converts into binary bytes
    return cloudpickle.dumps(task_payload)

def deserialize_task(serialized_data):
    
    # Unpacks the byte data obtained from network into original python func, args, and kwargs 
    task_payload = cloudpickle.loads(serialized_data)
    return task_payload['func'], task_payload['args'], task_payload['kwargs']


if __name__ == "__main__":
    # Testing serialize and deserialize functions
    def sample_func(a, b):
        return a * b

    # 1. Serialize
    packet = serialize_task(sample_func, args=(6, 7))
    print("Serialized Byte Data Length:", len(packet))

    # 2. Deserialize
    fn, args, kwargs = deserialize_task(packet)

    # 3. Execution check
    result = fn(*args, **kwargs)
    print("Deserialized Function Execution Result:", result)