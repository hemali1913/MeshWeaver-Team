import time
import pytest
from gossip_protocol import GossipNode

def test_peer_registration():
    """
    Test that registering peers correctly populates the peer registry 
    with proper host, port, and tracking timestamps.
    """
    node = GossipNode(node_id="test_node_1", heartbeat_interval=1)
    node.register_peer("peer_alpha", "127.0.0.1", 9001)
    
    status = node.get_cluster_status()
    assert status["active_peers_count"] == 1
    assert "peer_alpha" in status["peers"]
    assert node.peers["peer_alpha"]["host"] == "127.0.0.1"
    assert node.peers["peer_alpha"]["port"] == 9001

def test_heartbeat_broadcast():
    """
    Test that broadcasting heartbeats accurately returns 
    the count of currently active cluster peers.
    """
    node = GossipNode(node_id="test_node_2", heartbeat_interval=1)
    node.register_peer("peer_beta", "127.0.0.1", 9002)
    node.register_peer("peer_gamma", "127.0.0.1", 9003)
    
    active_count = node.broadcast_heartbeat()
    assert active_count == 2

def test_telemetry_loop_lifecycle():
    """
    Test starting and safely terminating the background 
    gossip thread without hanging or errors.
    """
    node = GossipNode(node_id="test_node_3", heartbeat_interval=1)
    assert node.is_running is False
    
    node.start_telemetry()
    assert node.is_running is True
    
    time.sleep(1.2)
    node.stop_telemetry()
    assert node.is_running is False