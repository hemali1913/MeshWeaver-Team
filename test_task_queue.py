import time
import pytest
from task_queue import TaskQueueManager, TaskExecutionError


def test_enqueue_and_execute_task():
    """
    Verifies that a task can be enqueued, processed by a worker,
    and marked COMPLETED with the expected return value.
    """
    qm = TaskQueueManager(worker_id="test_worker_1")
    qm.start_workers()

    def add_scaled(a, b, factor=2):
        return (a + b) * factor

    task_id = qm.enqueue_task(add_scaled, args=(3, 4), kwargs={"factor": 5})

    # Wait briefly for worker thread to finish execution
    deadline = time.time() + 2.0
    status = None
    while time.time() < deadline:
        status = qm.get_task_status(task_id)
        if status and status["status"] == "COMPLETED":
            break
        time.sleep(0.05)

    qm.stop_workers()

    assert status is not None
    assert status["status"] == "COMPLETED"
    assert status["result"] == 35
    assert status["error"] is None


def test_failed_task_records_error_status():
    """
    Verifies that if a task raises an exception at runtime,
    its status becomes FAILED and the error message is recorded.
    """
    qm = TaskQueueManager(worker_id="test_worker_2")

    def broken_job():
        raise ValueError("Simulated worker failure")

    task_id = qm.enqueue_task(broken_job)

    with pytest.raises(TaskExecutionError):
        qm.process_next_task(timeout=0.5)

    status = qm.get_task_status(task_id)
    assert status is not None
    assert status["status"] == "FAILED"
    assert "Simulated worker failure" in status["error"]


def test_unknown_task_id_returns_none():
    """
    Ensures querying a non-existent task_id safely returns None.
    """
    qm = TaskQueueManager(worker_id="test_worker_3")
    assert qm.get_task_status("nonexistent") is None