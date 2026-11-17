import time
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [GossipProtocol] - %(levelname)s - %(message)s')

class GossipNode:
    """
    Manages peer-to-peer cluster node telemetry, heartbeat broadcasting,
    and periodic neighbor health checks at configurable intervals (default 5 seconds).
    """
    def __init__(self, node_id, host="127.0.0.1", port=8000, heartbeat_interval=5):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval
        self.peers = {}  # Format: {peer_id: {'host': host, 'port': port, 'last_seen': timestamp}}
        self.is_running = False
        self._thread = None

    def register_peer(self, peer_id, peer_host, peer_port):
        """Registers or updates a neighboring cluster peer in the telemetry network."""
        self.peers[peer_id] = {
            'host': peer_host,
            'port': peer_port,
            'last_seen': time.time()
        }
        logging.info(f"Node {self.node_id} registered peer -> {peer_id} at {peer_host}:{peer_port}")

    def broadcast_heartbeat(self):
        """Simulates broadcasting a heartbeat message to all active cluster peers."""
        current_time = time.time()
        active_count = len(self.peers)
        logging.info(f"Node {self.node_id} broadcasting heartbeat ping to {active_count} active peers.")
        
        # Simulate updating local timestamps or outgoing ping dispatch
        for peer_id in self.peers:
            logging.debug(f"Dispatched heartbeat ping to peer: {peer_id}")
        return active_count

    def get_cluster_status(self):
        """Returns a snapshot of current node health and active peer registry."""
        return {
            "node_id": self.node_id,
            "status": "ONLINE" if self.is_running else "OFFLINE",
            "active_peers_count": len(self.peers),
            "peers": list(self.peers.keys())
        }

    def start_telemetry(self):
        """Starts the background gossip heartbeat telemetry loop."""
        if self.is_running:
            logging.warning("Gossip telemetry loop is already active.")
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self._thread.start()
        logging.info(f"Started gossip telemetry loop for node {self.node_id}")

    def _gossip_loop(self):
        """Background loop executing 5-second interval checks and heartbeat broadcasts."""
        while self.is_running:
            current_time = time.time()
            
            # Broadcast heartbeat to peers
            self.broadcast_heartbeat()
            
            # Check for inactive or dead peers (no heartbeat received for over 15 seconds)
            for peer_id, data in list(self.peers.items()):
                if current_time - data['last_seen'] > 15:
                    logging.warning(f"Peer {peer_id} appears unresponsive. Pruning from active registry.")
                    del self.peers[peer_id]

            time.sleep(self.heartbeat_interval)

    def stop_telemetry(self):
        """Safely terminates the background telemetry thread."""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2)
        logging.info(f"Stopped gossip telemetry loop for node {self.node_id}")


if __name__ == "__main__":
    # Local validation block for gossip telemetry and heartbeat broadcast
    node = GossipNode(node_id="node_alpha")
    node.register_peer("node_beta", "127.0.0.1", 8001)
    node.start_telemetry()
    
    # Allow the loop to run and broadcast heartbeat
    time.sleep(6)
    
    status = node.get_cluster_status()
    print("Cluster Status Snapshot:", status)
    
    node.stop_telemetry()