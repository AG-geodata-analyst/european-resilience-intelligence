import networkx as nx


def build_dependency_graph(dependencies: list[dict]) -> nx.DiGraph:
    """Builds a directed graph where edges point from source -> dependent."""
    G = nx.DiGraph()
    for dep in dependencies:
        G.add_edge(
            dep["source_sector"], dep["dependent_sector"], dep_type=dep["dependency_type"], confidence=dep["confidence"]
        )
    return G


def simulate_cascade(graph: nx.DiGraph, failed_sector: str) -> list[str]:
    """Given a starting failure, returns a list of all impacted sectors."""
    if failed_sector not in graph:
        return [failed_sector]

    # networkx.descendants finds all nodes reachable from the failed sector
    impacted = list(nx.descendants(graph, failed_sector))
    return [failed_sector] + impacted
