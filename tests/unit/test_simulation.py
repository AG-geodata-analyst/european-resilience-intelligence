from src.simulation.graph import build_dependency_graph, simulate_cascade


def test_electricity_cascades():
    deps = [
        {
            "source_sector": "electricity",
            "dependent_sector": "water",
            "dependency_type": "power",
            "confidence": "documented",
        },
        {
            "source_sector": "water",
            "dependent_sector": "healthcare",
            "dependency_type": "sanitation",
            "confidence": "documented",
        },
    ]
    graph = build_dependency_graph(deps)
    impacted = simulate_cascade(graph, "electricity")
    assert "electricity" in impacted
    assert "water" in impacted
    assert "healthcare" in impacted
    assert len(impacted) == 3


def test_leaf_node_does_not_cascade():
    deps = [
        {
            "source_sector": "electricity",
            "dependent_sector": "water",
            "dependency_type": "power",
            "confidence": "documented",
        },
    ]
    graph = build_dependency_graph(deps)
    impacted = simulate_cascade(graph, "water")
    assert impacted == ["water"]


def test_unknown_sector():
    graph = build_dependency_graph([])
    impacted = simulate_cascade(graph, "unknown")
    assert impacted == ["unknown"]
