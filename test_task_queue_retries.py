import pytest
from task_queue import TaskQueueManager, TaskExecutionError


def test_retry_requeues_failed_task_within_limit():
    """
    Verifies that a failed task within max_retries can be re-queued
    and its status resets to QUEUED with error cleared.
    """
    qm = TaskQueueManager(worker_id="retry_worker_1", max_retries=2)

    def failing_task():
        raise RuntimeError("Temporary network glitch")

    task_id = qm.enqueue_task(failing_task)

    with pytest.raises(TaskExecutionError):
        qm.process_next_task(timeout=0.5)

    assert qm.get_task_status(task_id)["status"] == "FAILED"
    assert qm.get_task_status(task_id)["attempts"] == 1

    retried = qm.retry_failed_task(task_id)
    assert retried is True
    assert qm.get_task_status(task_id)["status"] == "QUEUED"
    assert qm.get_task_status(task_id)["error"] is None


def test_retry_blocked_after_exceeding_max_retries():
    """
    Verifies that once attempts exceed max_retries, retry_failed_task
    returns False and refuses to re-queue the task.
    """
    qm = TaskQueueManager(worker_id="retry_worker_2", max_retries=1)

    def always_fails():
        raise ValueError("Persistent failure")

    task_id = qm.enqueue_task(always_fails)

    # Attempt 1
    with pytest.raises(TaskExecutionError):
        qm.process_next_task(timeout=0.5)
    assert qm.retry_failed_task(task_id) is True

    # Attempt 2 (reaches max_retries = 1)
    with pytest.raises(TaskExecutionError):
        qm.process_next_task(timeout=0.5)

    # Next retry should be rejected since attempts (2) > max_retries (1)
    assert qm.retry_failed_task(task_id) is False


def test_list_tasks_by_status():
    """
    Verifies filtering tasks accurately across QUEUED, COMPLETED, and FAILED states.
    """
    qm = TaskQueueManager(worker_id="retry_worker_3", max_retries=1)

    ok_id = qm.enqueue_task(lambda x: x + 1, args=(10,))
    fail_id = qm.enqueue_task(lambda: (_ for _ in ()).throw(RuntimeError("Boom")))
    queued_id = qm.enqueue_task(lambda x: x * 2, args=(3,))

    qm.process_next_task(timeout=0.5)
    with pytest.raises(TaskExecutionError):
        qm.process_next_task(timeout=0.5)

    assert ok_id in qm.list_tasks_by_status("COMPLETED")
    assert fail_id in qm.list_tasks_by_status("FAILED")
    assert queued_id in qm.list_tasks_by_status("QUEUED")