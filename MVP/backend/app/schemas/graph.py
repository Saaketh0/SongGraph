from __future__ import annotations

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    label: str
    songName: str
    artist: str
    genre: str


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    rank: int


class GraphMeta(BaseModel):
    seedType: str | None = None
    seedValue: str | None = None
    visibleNodeCount: int = 0
    visibleEdgeCount: int = 0
    reachedLimit: bool = False


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    meta: GraphMeta


class ExpandGraphRequest(BaseModel):
    visibleNodeIds: list[str] = Field(default_factory=list)
    visibleEdgeIds: list[str] = Field(default_factory=list)
    selectedNodeIds: list[str] = Field(default_factory=list)
    expansionMode: str = "selected"

