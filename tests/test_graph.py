from src.core.graph import create_orchestrator_graph

def test_graph_creation():
    graph = create_orchestrator_graph()
    assert graph is not None
