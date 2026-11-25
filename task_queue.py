import queue
import threading
import time
import uuid
import logging
from task_serializer import serialize_task, deserialize_task, TaskSerializationError, TaskDeserializationError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TaskQueue] - %(levelname)s - %(message)s')


class TaskExecutionError(Exception):
    """Raised when a deserialized task fails during execution."""
    pass


class TaskQueueManager:
    """
    Thread-safe task queue that accepts callables, serializes them into payloads,
    tracks task lifecycle states, supports retries, and executes tasks via workers.
    """
    def __init__(self, worker_id="worker_1", max_retries=2):
        self.worker_id = worker_id
        self.max_retries = max_retries
        self._queue = queue.Queue()
        self._lock = threading.Lock()
        self.tasks = {}  # task_id -> metadata & status/result
        self._is_running = False
        self._worker_thread = None

    def enqueue_task(self, func, args=None, kwargs=None):
        """Serializes and enqueues a task, returning a unique task_id."""
        task_id = str(uuid.uuid4())[:8]
        try:
            payload = serialize_task(func, args=args, kwargs=kwargs)
        except TaskSerializationError as exc:
            logging.error(f"[{self.worker_id}] Failed to enqueue task {task_id}: {exc}")
            raise

        with self._lock:
            self.tasks[task_id] = {
                "status": "QUEUED",
                "payload": payload,
                "result": None,
                "error": None,
                "attempts": 0,
                "created_at": time.time(),
            }

        self._queue.put(task_id)
        logging.info(f"[{self.worker_id}] Enqueued task {task_id} ({len(payload)} bytes)")
        return task_id

    def process_next_task(self, timeout=0.5):
        """Pops one task from the queue, deserializes it, and runs it."""
        try:
            task_id = self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

        with self._lock:
            record = self.tasks.get(task_id)
            if not record:
                self._queue.task_done()
                return None
            record["status"] = "RUNNING"
            record["attempts"] += 1

        try:
            fn, args, kwargs = deserialize_task(record["payload"])
            result = fn(*args, **kwargs)
            with self._lock:
                record["status"] = "COMPLETED"
                record["result"] = result
                record["error"] = None
            logging.info(f"[{self.worker_id}] Task {task_id} completed successfully.")
            return result
        except TaskDeserializationError as exc:
            with self._lock:
                record["status"] = "FAILED"
                record["error"] = str(exc)
            logging.error(f"[{self.worker_id}] Task {task_id} deserialization error: {exc}")
            raise TaskExecutionError(f"Task {task_id} failed during deserialization") from exc
        except Exception as exc:
            with self._lock:
                record["status"] = "FAILED"
                record["error"] = str(exc)
            logging.error(f"[{self.worker_id}] Task {task_id} runtime error: {exc}")
            raise TaskExecutionError(f"Task {task_id} raised an exception: {exc}") from exc
        finally:
            self._queue.task_done()

    def retry_failed_task(self, task_id):
        """
        Re-queues a FAILED task if its attempt count is below max_retries.
        Returns True if re-queued, False otherwise.
        """
        with self._lock:
            record = self.tasks.get(task_id)
            if not record or record["status"] != "FAILED":
                logging.warning(f"[{self.worker_id}] Task {task_id} is not eligible for retry.")
                return False
            if record["attempts"] > self.max_retries:
                logging.warning(
                    f"[{self.worker_id}] Task {task_id} exceeded max_retries ({self.max_retries})."
                )
                return False

            record["status"] = "QUEUED"
            record["error"] = None

        self._queue.put(task_id)
        logging.info(f"[{self.worker_id}] Re-queued failed task {task_id} for retry.")
        return True

    def list_tasks_by_status(self, status):
        """Returns a list of task_ids matching the requested status."""
        with self._lock:
            return [
                tid for tid, meta in self.tasks.items()
                if meta["status"] == status
            ]

    def start_workers(self):
        """Starts background worker loop to continuously drain queued tasks."""
        if self._is_running:
            logging.warning(f"[{self.worker_id}] Worker loop already running.")
            return
        self._is_running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        logging.info(f"[{self.worker_id}] Background worker started.")

    def _worker_loop(self):
        while self._is_running:
            try:
                self.process_next_task(timeout=0.3)
            except TaskExecutionError:
                continue

    def stop_workers(self):
        """Stops the background worker thread cleanly."""
        self._is_running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=2)
        logging.info(f"[{self.worker_id}] Background worker stopped.")

    def get_task_status(self, task_id):
        """Returns a safe status snapshot for a given task_id."""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return None
            return {
                "task_id": task_id,
                "status": task["status"],
                "result": task["result"],
                "error": task["error"],
                "attempts": task["attempts"],
            }


if __name__ == "__main__":
    def compute_with_retry_demo(val, should_fail_first=True):
        if should_fail_first:
            raise RuntimeError("Simulated transient failure")
        return val * 10

    qm = TaskQueueManager(worker_id="node_alpha_worker", max_retries=2)

    # 1. Enqueue a task that fails on first run, then retry with a healthy payload
    tid_fail = qm.enqueue_task(compute_with_retry_demo, args=(4,), kwargs={"should_fail_first": True})
    try:
        qm.process_next_task(timeout=0.5)
    except TaskExecutionError:
        pass

    print("After attempt 1:", qm.get_task_status(tid_fail))
    if qm.retry_failed_task(tid_fail):
        # Replace payload with non-failing call for demonstration of successful retry recovery
        with qm._lock:
            qm.tasks[tid_fail]["payload"] = serialize_task(
                compute_with_retry_demo, args=(4,), kwargs={"should_fail_first": False}
            )
        res = qm.process_next_task(timeout=0.5)
        print("After retry result:", res, "| Status:", qm.get_task_status(tid_fail))