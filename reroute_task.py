import logging
import random
from task_serializer import serialize_task, TaskSerializationError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TaskRouter] - %(levelname)s - %(message)s')

class TaskRoutingError(Exception):
    """Raised when a task cannot be routed or rerouted to any available peer."""
    pass


class TaskRouter:
    """
    Handles task dispatch, peer selection, and failover rerouting
    when a target node fails or becomes unreachable.
    """
    def __init__(self, local_node_id):
        self.local_node_id = local_node_id
        self.reroute_history = []

    def select_fallback_peer(self, active_peers, failed_peer_id=None):
        """
        Selects a healthy peer from active_peers excluding any node that just failed.
        Returns the selected peer_id or None if no candidate is available.
        """
        candidates = [
            peer_id for peer_id in active_peers.keys()
            if peer_id != failed_peer_id and peer_id != self.local_node_id
        ]

        if not candidates:
            logging.warning(f"[{self.local_node_id}] No fallback peers available for rerouting.")
            return None

        chosen_peer = random.choice(candidates)
        logging.info(f"[{self.local_node_id}] Selected fallback peer -> {chosen_peer}")
        return chosen_peer

    def reroute_task(self, func, args=None, kwargs=None, active_peers=None, failed_peer_id=None):
        """
        Serializes a task and prepares a rerouted payload for a fallback peer.
        """
        if active_peers is None:
            active_peers = {}

        target_peer = self.select_fallback_peer(active_peers, failed_peer_id=failed_peer_id)
        if not target_peer:
            raise TaskRoutingError(f"Failed to reroute task '{getattr(func, '__name__', str(func))}': no healthy peers.")

        try:
            payload = serialize_task(func, args=args, kwargs=kwargs)
        except TaskSerializationError as exc:
            logging.error(f"[{self.local_node_id}] Task serialization failed during reroute: {exc}")
            raise TaskRoutingError("Unable to serialize task payload for rerouting.") from exc

        record = {
            "task_name": getattr(func, "__name__", str(func)),
            "failed_peer": failed_peer_id,
            "target_peer": target_peer,
            "payload_size": len(payload),
        }
        self.reroute_history.append(record)
        logging.info(
            f"[{self.local_node_id}] Rerouted '{record['task_name']}' "
            f"from '{failed_peer_id}' to '{target_peer}' ({record['payload_size']} bytes)"
        )
        return target_peer, payload


if __name__ == "__main__":
    def compute_square(n):
        return n * n

    sample_peers = {
        "node_beta": {"host": "127.0.0.1", "port": 8001},
        "node_gamma": {"host": "127.0.0.1", "port": 8002},
    }

    router = TaskRouter(local_node_id="node_alpha")
    peer, raw_bytes = router.reroute_task(
        compute_square,
        args=(6,),
        active_peers=sample_peers,
        failed_peer_id="node_beta",
    )
    print(f"Rerouted to: {peer} | Payload bytes: {len(raw_bytes)}")