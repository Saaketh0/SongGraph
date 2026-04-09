"use client";

import dynamic from "next/dynamic";
import type { GraphEdge, GraphNode } from "../../types/api";

const GraphCanvas = dynamic(
  () => import("./GraphCanvas").then((module) => module.GraphCanvas),
  {
    ssr: false,
    loading: () => <div className="graph-canvas-empty">Loading graph canvas...</div>,
  },
);

type GraphPanelProps = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId: string | null;
  reachedLimit: boolean;
  loading: boolean;
  onSelectNode: (nodeId: string) => void;
  onExpand: () => void;
  onReset: () => void;
};

export function GraphPanel({
  nodes,
  edges,
  selectedNodeId,
  reachedLimit,
  loading,
  onSelectNode,
  onExpand,
  onReset,
}: GraphPanelProps) {
  return (
    <section className="panel graph-panel">
      <div className="panel-head">
        <h2>Graph</h2>
        <div className="actions">
          <button type="button" className="button" onClick={onExpand} disabled={loading || reachedLimit || !selectedNodeId}>
            Expand
          </button>
          <button type="button" className="button" onClick={onReset} disabled={loading}>
            Reset
          </button>
        </div>
      </div>
      <p className="muted">
        Nodes: {nodes.length} · Edges: {edges.length} · Limit reached: {reachedLimit ? "yes" : "no"}
      </p>
      {reachedLimit ? <p className="warning">Graph node cap reached. Reset or narrow your seed.</p> : null}
      <GraphCanvas nodes={nodes} edges={edges} selectedNodeId={selectedNodeId} onSelectNode={onSelectNode} />
      <div className="node-list">
        {nodes.slice(0, 24).map((node) => {
          const selected = node.id === selectedNodeId;
          return (
            <button
              type="button"
              key={node.id}
              className={`node-chip ${selected ? "node-chip-active" : ""}`}
              onClick={() => onSelectNode(node.id)}
            >
              {node.songName}
            </button>
          );
        })}
      </div>
    </section>
  );
}
