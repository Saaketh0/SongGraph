from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories.graph_repository import GraphRepository
from app.schemas.graph import ExpandGraphRequest, GraphEdge, GraphMeta, GraphNode, GraphResponse


@dataclass(slots=True)
class _SongRow:
    song_id: str
    song_name: str
    artist_name: str
    genre: str


def _node_from_song(song: _SongRow) -> GraphNode:
    return GraphNode(
        id=song.song_id,
        label=song.song_name,
        songName=song.song_name,
        artist=song.artist_name,
        genre=song.genre,
    )


def _edge_id(source: str, target: str) -> str:
    return f"{source}__{target}"


class GraphService:
    def __init__(self, db: Session) -> None:
        self.settings = get_settings()
        self.repository = GraphRepository(db=db, read_from_stage=self.settings.read_from_stage)

    def seed_from_song(self, song_id: str) -> GraphResponse:
        seed_song = self.repository.get_song_by_id(song_id)
        if seed_song is None:
            raise ValueError(f"Song not found: {song_id}")

        nodes_by_id: dict[str, GraphNode] = {seed_song.song_id: _node_from_song(seed_song)}
        edges: list[GraphEdge] = []

        neighbor_edges = self.repository.get_neighbor_edges_for_sources([seed_song.song_id])
        neighbor_ids = [target_id for _, target_id, _ in neighbor_edges]
        for song in self.repository.get_songs_by_ids(neighbor_ids):
            nodes_by_id[song.song_id] = _node_from_song(song)

        for source_id, target_id, rank in neighbor_edges:
            if source_id in nodes_by_id and target_id in nodes_by_id:
                edges.append(GraphEdge(id=_edge_id(source_id, target_id), source=source_id, target=target_id, rank=rank))

        return GraphResponse(
            nodes=list(nodes_by_id.values()),
            edges=edges,
            meta=GraphMeta(
                seedType="song",
                seedValue=song_id,
                visibleNodeCount=len(nodes_by_id),
                visibleEdgeCount=len(edges),
                reachedLimit=len(nodes_by_id) >= self.settings.graph_node_cap,
            ),
        )

    def seed_from_artist(self, artist_name: str) -> GraphResponse:
        songs = self.repository.get_songs_by_artist(
            artist_name=artist_name,
            limit=min(self.settings.artist_seed_cap, self.settings.graph_node_cap),
        )
        nodes = [_node_from_song(song) for song in songs]
        return GraphResponse(
            nodes=nodes,
            edges=[],
            meta=GraphMeta(
                seedType="artist",
                seedValue=artist_name,
                visibleNodeCount=len(nodes),
                visibleEdgeCount=0,
                reachedLimit=len(nodes) >= self.settings.graph_node_cap,
            ),
        )

    def seed_from_genre(self, genre_name: str) -> GraphResponse:
        songs = self.repository.get_songs_by_genre_sample(
            genre_name=genre_name,
            limit=min(self.settings.genre_seed_sample_size, self.settings.graph_node_cap),
        )
        nodes = [_node_from_song(song) for song in songs]
        return GraphResponse(
            nodes=nodes,
            edges=[],
            meta=GraphMeta(
                seedType="genre",
                seedValue=genre_name,
                visibleNodeCount=len(nodes),
                visibleEdgeCount=0,
                reachedLimit=len(nodes) >= self.settings.graph_node_cap,
            ),
        )

    def expand_graph(self, request: ExpandGraphRequest) -> GraphResponse:
        cap = self.settings.graph_node_cap
        existing_node_ids: set[str] = set(request.visibleNodeIds)
        existing_edge_ids: set[str] = set(request.visibleEdgeIds)
        selected_ids = [node_id for node_id in request.selectedNodeIds if node_id in existing_node_ids]

        reached_limit = len(existing_node_ids) >= cap
        if reached_limit or not selected_ids:
            return GraphResponse(
                nodes=[],
                edges=[],
                meta=GraphMeta(
                    seedType=None,
                    seedValue=None,
                    visibleNodeCount=len(existing_node_ids),
                    visibleEdgeCount=len(existing_edge_ids),
                    reachedLimit=reached_limit,
                ),
            )

        neighbor_edges = self.repository.get_neighbor_edges_for_sources(selected_ids)
        candidate_target_ids: list[str] = []
        for _, target_id, _ in neighbor_edges:
            if target_id not in existing_node_ids:
                candidate_target_ids.append(target_id)
        candidate_target_ids = list(dict.fromkeys(candidate_target_ids))

        remaining_slots = max(0, cap - len(existing_node_ids))
        allowed_target_ids = candidate_target_ids[:remaining_slots]
        loaded_songs = self.repository.get_songs_by_ids(allowed_target_ids)
        loaded_song_ids = {song.song_id for song in loaded_songs}

        new_nodes = [_node_from_song(song) for song in loaded_songs]
        final_visible_nodes = len(existing_node_ids) + len(new_nodes)
        reached_limit = final_visible_nodes >= cap

        new_edges: list[GraphEdge] = []
        for source_id, target_id, rank in neighbor_edges:
            if source_id not in existing_node_ids:
                continue
            if target_id in existing_node_ids or target_id in loaded_song_ids:
                edge_id = _edge_id(source_id, target_id)
                if edge_id in existing_edge_ids:
                    continue
                existing_edge_ids.add(edge_id)
                new_edges.append(GraphEdge(id=edge_id, source=source_id, target=target_id, rank=rank))

        return GraphResponse(
            nodes=new_nodes,
            edges=new_edges,
            meta=GraphMeta(
                seedType=None,
                seedValue=None,
                visibleNodeCount=final_visible_nodes,
                visibleEdgeCount=len(existing_edge_ids),
                reachedLimit=reached_limit,
            ),
        )
