"use client";

import { useMemo, useReducer } from "react";
import type {
  ArtistSearchResult,
  GenreSearchResult,
  GraphEdge,
  GraphNode,
  GraphResponse,
  SearchMode,
  SongSearchResult,
} from "../types/api";

export type SearchResultItem = SongSearchResult | ArtistSearchResult | GenreSearchResult;

type SearchState = {
  mode: SearchMode;
  query: string;
  results: SearchResultItem[];
};

type GraphState = {
  visibleNodes: GraphNode[];
  visibleEdges: GraphEdge[];
  selectedNodeId: string | null;
  reachedLimit: boolean;
};

type GraphSessionState = {
  search: SearchState;
  graph: GraphState;
};

type GraphSessionAction =
  | { type: "search/setMode"; payload: SearchMode }
  | { type: "search/setQuery"; payload: string }
  | { type: "search/setResults"; payload: SearchResultItem[] }
  | { type: "graph/setSeed"; payload: GraphResponse }
  | { type: "graph/mergeDelta"; payload: GraphResponse }
  | { type: "graph/setSelectedNode"; payload: string | null }
  | { type: "graph/reset" };

const initialState: GraphSessionState = {
  search: {
    mode: "song",
    query: "",
    results: [],
  },
  graph: {
    visibleNodes: [],
    visibleEdges: [],
    selectedNodeId: null,
    reachedLimit: false,
  },
};

function mergeNodes(existing: GraphNode[], incoming: GraphNode[]): GraphNode[] {
  const byId = new Map<string, GraphNode>();
  for (const node of existing) {
    byId.set(node.id, node);
  }
  for (const node of incoming) {
    byId.set(node.id, node);
  }
  return Array.from(byId.values());
}

function mergeEdges(existing: GraphEdge[], incoming: GraphEdge[]): GraphEdge[] {
  const byId = new Map<string, GraphEdge>();
  for (const edge of existing) {
    byId.set(edge.id, edge);
  }
  for (const edge of incoming) {
    byId.set(edge.id, edge);
  }
  return Array.from(byId.values());
}

function reducer(state: GraphSessionState, action: GraphSessionAction): GraphSessionState {
  switch (action.type) {
    case "search/setMode":
      return {
        ...state,
        search: {
          ...state.search,
          mode: action.payload,
          results: [],
        },
      };
    case "search/setQuery":
      return {
        ...state,
        search: {
          ...state.search,
          query: action.payload,
        },
      };
    case "search/setResults":
      return {
        ...state,
        search: {
          ...state.search,
          results: action.payload,
        },
      };
    case "graph/setSeed":
      return {
        ...state,
        graph: {
          visibleNodes: action.payload.nodes,
          visibleEdges: action.payload.edges,
          selectedNodeId: action.payload.nodes[0]?.id ?? null,
          reachedLimit: action.payload.meta.reachedLimit,
        },
      };
    case "graph/mergeDelta":
      return {
        ...state,
        graph: {
          ...state.graph,
          visibleNodes: mergeNodes(state.graph.visibleNodes, action.payload.nodes),
          visibleEdges: mergeEdges(state.graph.visibleEdges, action.payload.edges),
          reachedLimit: action.payload.meta.reachedLimit,
        },
      };
    case "graph/setSelectedNode":
      return {
        ...state,
        graph: {
          ...state.graph,
          selectedNodeId: action.payload,
        },
      };
    case "graph/reset":
      return {
        ...state,
        graph: {
          ...initialState.graph,
        },
      };
    default:
      return state;
  }
}

export function useGraphSessionState() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const actions = useMemo(
    () => ({
      setSearchMode(mode: SearchMode) {
        dispatch({ type: "search/setMode", payload: mode });
      },
      setSearchQuery(query: string) {
        dispatch({ type: "search/setQuery", payload: query });
      },
      setSearchResults(results: SearchResultItem[]) {
        dispatch({ type: "search/setResults", payload: results });
      },
      setGraphSeed(payload: GraphResponse) {
        dispatch({ type: "graph/setSeed", payload });
      },
      mergeGraphDelta(payload: GraphResponse) {
        dispatch({ type: "graph/mergeDelta", payload });
      },
      setSelectedNode(nodeId: string | null) {
        dispatch({ type: "graph/setSelectedNode", payload: nodeId });
      },
      resetGraph() {
        dispatch({ type: "graph/reset" });
      },
    }),
    [dispatch],
  );

  return useMemo(() => ({ state, actions }), [state, actions]);
}
