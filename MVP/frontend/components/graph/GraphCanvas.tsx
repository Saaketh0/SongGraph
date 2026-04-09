"use client";

import { useMemo } from "react";
import { Cosmograph } from "@cosmograph/react";

import type { GraphEdge, GraphNode } from "../../types/api";

type GraphCanvasProps = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
};

type CosmographPoint = {
  id: string;
  label: string;
  color: string;
  size: number;
  artist: string;
  genre: string;
};

type CosmographLink = {
  id: string;
  source: string;
  target: string;
  width: number;
  color: string;
};

export function GraphCanvas({ nodes, edges, selectedNodeId, onSelectNode }: GraphCanvasProps) {
  const points = useMemo<CosmographPoint[]>(
    () =>
      nodes.map((node) => ({
        id: node.id,
        label: node.songName,
        color: node.id === selectedNodeId ? "#f08c00" : "#3f83f8",
        size: node.id === selectedNodeId ? 10 : 7,
        artist: node.artist,
        genre: node.genre,
      })),
    [nodes, selectedNodeId],
  );

  const links = useMemo<CosmographLink[]>(
    () =>
      edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        width: edge.rank <= 2 ? 2.2 : 1.4,
        color: "#7c8da8",
      })),
    [edges],
  );

  if (!points.length) {
    return <div className="graph-canvas-empty">No graph seeded yet. Search and select a result.</div>;
  }

  return (
    <div className="graph-canvas-wrap">
      <Cosmograph
        className="graph-canvas"
        points={points}
        links={links}
        pointIdBy="id"
        pointLabelBy="label"
        pointColorBy="color"
        pointSizeBy="size"
        pointSizeRange={[5, 12]}
        pointDefaultColor="#3f83f8"
        pointGreyoutOpacity={0.15}
        linkSourceBy="source"
        linkTargetBy="target"
        linkColorBy="color"
        linkWidthBy="width"
        linkDefaultColor="#6f82a0"
        linkDefaultWidth={1.5}
        renderHoveredPointRing={true}
        hoveredPointRingColor="#ffffff"
        focusedPointRingColor="#ffe6b5"
        fitViewOnInit={true}
        fitViewPadding={0.2}
        fitViewDuration={350}
        backgroundColor="#0f1720"
        onPointClick={(index: number) => {
          const point = points[index];
          if (point) {
            onSelectNode(point.id);
          }
        }}
      />
    </div>
  );
}
