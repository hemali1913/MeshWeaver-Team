import logging
import time
from gossip_protocol import GossipNode
from reroute_task import TaskRouter, TaskRoutingError
from task_queue import TaskQueueManager
from task_serializer import deserialize_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ClusterFailover] - %(levelname)s - %(message)s')


class ClusterFailoverOrchestrator:
    """
    Connects GossipNode peer telemetry, TaskRouter failover selection,
    and TaskQueueManager execution to reroute tasks away from failed peers.
    """
    def __init__(self, node_id, host="127.0.0.1", port=8000, heartbeat_interval=5, peer_timeout=15.0):
        self.node_id = node_id
        self.peer_timeout = peer_timeout
        self.gossip = GossipNode(node_id=node_id, host=host, port=port, heartbeat_interval=heartbeat_interval)
        self.router = TaskRouter(local_node_id=node_id)
        self.peer_queues = {
            node_id: TaskQueueManager(worker_id=f"{node_id}_queue")
        }

    def register_worker_node(self, peer_id, host, port):
        """Registers a peer in gossip telemetry and initializes its local task queue."""
        self.gossip.register_peer(peer_id, host, port)
        if peer_id not in self.peer_queues:
            self.peer_queues[peer_id] = TaskQueueManager(worker_id=f"{peer_id}_queue")
        logging.info(f"[{self.node_id}] Registered worker node '{peer_id}' ({host}:{port})")

    def mark_peer_stale(self, peer_id, age_seconds=20.0):
        """
        Helper to simulate a peer missing heartbeats for age_seconds
        so stale peer detection and failover can be tested deterministically.
        """
        if peer_id in self.gossip.peers:
            self.gossip.peers[peer_id]["last_seen"] = time.time() - age_seconds
            logging.warning(f"[{self.node_id}] Marked peer '{peer_id}' stale by {age_seconds}s")

    def detect_stale_peers(self):
        """Returns peer_ids whose last_seen timestamp exceeds peer_timeout."""
        now = time.time()
        stale = [
            peer_id for peer_id, meta in self.gossip.peers.items()
            if (now - meta["last_seen"]) > self.peer_timeout
        ]
        if stale:
            logging.warning(f"[{self.node_id}] Detected stale peers: {stale}")
        return stale

    def failover_and_enqueue(self, func, args=None, kwargs=None, failed_peer_id=None):
        """
        Selects a healthy peer (excluding failed_peer_id and stale peers),
        serializes the task via TaskRouter, unpacks it, and enqueues it on the target queue.
        """
        stale_peers = set(self.detect_stale_peers())
        healthy_peers = {
            peer_id: meta for peer_id, meta in self.gossip.peers.items()
            if peer_id not in stale_peers and peer_id != failed_peer_id
        }

        # Include local node as fallback if registered in peer_queues
        if self.node_id != failed_peer_id:
            healthy_peers[self.node_id] = {"host": self.gossip.host, "port": self.gossip.port}

        target_peer, payload = self.router.reroute_task(
            func,
            args=args,
            kwargs=kwargs,
            active_peers=healthy_peers,
            failed_peer_id=failed_peer_id,
        )

        if target_peer not in self.peer_queues:
            self.peer_queues[target_peer] = TaskQueueManager(worker_id=f"{target_peer}_queue")

        fn, unpacked_args, unpacked_kwargs = deserialize_task(payload)
        task_id = self.peer_queues[target_peer].enqueue_task(fn, args=unpacked_args, kwargs=unpacked_kwargs)
        logging.info(f"[{self.node_id}] Enqueued rerouted task '{task_id}' onto '{target_peer}'")
        return target_peer, task_id


if __name__ == "__main__":
    def compute_power(base, exp):
        return base ** exp

    orchestrator = ClusterFailoverOrchestrator(node_id="node_alpha", peer_timeout=10.0)
    orchestrator.register_worker_node("node_beta", "127.0.0.1", 8001)
    orchestrator.register_worker_node("node_gamma", "127.0.0.1", 8002)

    # Simulate node_beta going stale
    orchestrator.mark_peer_stale("node_beta", age_seconds=15.0)

    try:
        chosen_peer, tid = orchestrator.failover_and_enqueue(
            compute_power, args=(3, 4), failed_peer_id="node_beta"
        )
        result = orchestrator.peer_queues[chosen_peer].process_next_task(timeout=0.5)
        print(f"Failover succeeded -> Peer: {chosen_peer}, Task ID: {tid}, Result: {result}")
    except TaskRoutingError as err:
        print("Failover failed:", err)