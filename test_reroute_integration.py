import pytest
from gossip_protocol import GossipNode
from reroute_task import TaskRouter, TaskRoutingError
from task_serializer import deserialize_task


def test_reroute_excludes_failed_peer_and_executes_task():
    """
    Verifies that when a peer fails, TaskRouter selects another active peer
    from the gossip registry and produces a valid serialized task payload.
    """
    node = GossipNode(node_id="node_alpha", heartbeat_interval=1)
    node.register_peer("node_beta", "127.0.0.1", 8001)
    node.register_peer("node_gamma", "127.0.0.1", 8002)

    router = TaskRouter(local_node_id="node_alpha")

    def add_numbers(a, b):
        return a + b

    target_peer, payload = router.reroute_task(
        add_numbers,
        args=(15, 27),
        active_peers=node.peers,
        failed_peer_id="node_beta",
    )

    assert target_peer == "node_gamma"
    assert len(router.reroute_history) == 1

    fn, args, kwargs = deserialize_task(payload)
    assert fn(*args, **kwargs) == 42


def test_reroute_raises_error_when_no_healthy_peers():
    """
    Ensures TaskRoutingError is raised when only the failed peer or local
    node exists in the active peer list.
    """
    router = TaskRouter(local_node_id="node_alpha")
    peers = {"node_beta": {"host": "127.0.0.1", "port": 8001}}

    def sample_job(x):
        return x * 2

    with pytest.raises(TaskRoutingError):
        router.reroute_task(
            sample_job,
            args=(5,),
            active_peers=peers,
            failed_peer_id="node_beta",
        )