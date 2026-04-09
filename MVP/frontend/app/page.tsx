"use client";

import { useMemo } from "react";

import { GraphPanel } from "../components/graph/GraphPanel";
import { SearchBar } from "../components/search/SearchBar";
import { SearchModeTabs } from "../components/search/SearchModeTabs";
import { SearchResults } from "../components/search/SearchResults";
import { SelectedSongPanel } from "../components/sidebar/SelectedSongPanel";
import { useBackendHealth } from "../hooks/useBackendHealth";
import { useGraphActions } from "../hooks/useGraphActions";
import { useSongDetail } from "../hooks/useSongDetail";
import { useGraphSessionState } from "../store/graphSession";

export default function HomePage() {
  const { state, actions } = useGraphSessionState();
  const backendHealth = useBackendHealth();
  const { detail: songDetail, loading: songDetailLoading, error: songDetailError } = useSongDetail(
    state.graph.selectedNodeId,
  );
  const {
    searchLoading,
    graphLoading,
    searchError,
    graphError,
    runSearch,
    seedFromResult,
    runExpand,
  } = useGraphActions({
    mode: state.search.mode,
    query: state.search.query,
    visibleNodes: state.graph.visibleNodes,
    visibleEdges: state.graph.visibleEdges,
    selectedNodeId: state.graph.selectedNodeId,
    actions,
  });

  const selectedNode = useMemo(
    () => state.graph.visibleNodes.find((node) => node.id === state.graph.selectedNodeId) ?? null,
    [state.graph.selectedNodeId, state.graph.visibleNodes],
  );

  return (
    <main>
      <h1>SongGraph MVP</h1>
      <p>Phase 3 homepage shell with wired search, seeding, expand, and song detail fetch.</p>
      <div className="grid-layout">
        <section className="panel">
          <h2>Search</h2>
          <SearchModeTabs mode={state.search.mode} onChange={actions.setSearchMode} />
          <SearchBar
            query={state.search.query}
            loading={searchLoading}
            onQueryChange={actions.setSearchQuery}
            onSearch={runSearch}
          />
          {searchError ? <p className="error">{searchError}</p> : null}
          <SearchResults mode={state.search.mode} results={state.search.results} onSelect={seedFromResult} />
        </section>

        <GraphPanel
          nodes={state.graph.visibleNodes}
          edges={state.graph.visibleEdges}
          selectedNodeId={state.graph.selectedNodeId}
          reachedLimit={state.graph.reachedLimit}
          loading={graphLoading}
          onSelectNode={actions.setSelectedNode}
          onExpand={runExpand}
          onReset={actions.resetGraph}
        />

        <SelectedSongPanel
          selectedNode={selectedNode}
          detail={songDetail}
          loading={songDetailLoading}
          error={songDetailError}
        />
      </div>

      <div className="card">
        <p>
          <strong>Frontend:</strong> Next.js + TypeScript shell
        </p>
        <p>
          <strong>Backend health:</strong> {backendHealth.status} ({backendHealth.detail})
        </p>
        {graphError ? <p className="error">{graphError}</p> : null}
      </div>
    </main>
  );
}
