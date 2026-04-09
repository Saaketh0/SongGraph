from __future__ import annotations

import json
from pathlib import Path


def validate_graph(graph: dict) -> dict:
    nodes = graph.get("nodes", [])
    links = graph.get("links", [])

    node_ids = [node["id"] for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Graph contains duplicate node IDs.")

    node_id_set = set(node_ids)
    seen_links: set[tuple[str, str, str]] = set()

    for link in links:
        edge_key = (link["source"], link["target"], link["type"])
        if edge_key in seen_links:
            raise ValueError(f"Graph contains duplicate edge: {edge_key}")
        if link["source"] not in node_id_set or link["target"] not in node_id_set:
            raise ValueError(f"Graph edge points to a missing node: {edge_key}")
        if link["type"] == "SIMILAR_TO" and link["source"] == link["target"]:
            raise ValueError(f"Graph contains a self-referential similarity edge: {edge_key}")
        seen_links.add(edge_key)

    return graph


def export_graph_json(graph: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
