# Phase 5 README

This phase focuses on stabilization, quality, and performance hardening on top of the Phase 4 Cosmograph integration.

## Phase 5 Goal
- Make the app production-ready for local/demo use by improving reliability, test coverage, graph UX behavior, and operational guardrails without changing core product scope.

## Scope
- Keep existing architecture:
  - Next.js frontend
  - FastAPI backend
  - PostgreSQL runtime
  - Cosmograph graph rendering
- Do not add new major infrastructure (no cloud deployment system, no graph database migration).

## Deliverables
1. Robust graph interaction behavior under edge cases.
2. Consistent loading/error/empty states across homepage and song page.
3. Backend query and expansion performance guardrails.
4. Automated test coverage for core user flows.
5. Operational docs for debugging and common failure recovery.

## Workstreams

### 1) Frontend Interaction Hardening
- Add explicit UX states for:
  - empty search results
  - no seed graph returned
  - expansion blocked by node cap
  - backend unavailable
- Add lightweight retry actions in error surfaces for:
  - search
  - graph seed
  - graph expand
  - song detail
- Ensure selected node state remains valid after graph reset and reseed.

Acceptance criteria:
- No uncaught runtime errors during normal graph usage.
- All error states are user-visible with actionable messaging.

### 2) Graph Behavior and Session Controls
- Add deterministic guardrails around expansion:
  - disable expand when `selectedNodeId` is null
  - disable expand when `reachedLimit=true`
- Add session controls:
  - clear selected node on reset
  - optional "recenter on selected" action if not already available
- Verify dedupe remains stable when repeatedly expanding same node.

Acceptance criteria:
- Repeated expand actions never duplicate visible nodes/edges.
- Limit state is reflected immediately in controls.

### 3) Backend Performance and Query Quality
- Add/verify DB indexes used by search/expand paths:
  - lower(song_name), lower(artist_name), lower(genre)
  - song neighbor source index
- Add request-level limits:
  - cap search result size from config
  - cap expansion edge fanout per call if needed
- Add timed logging around:
  - search query duration
  - seed graph query duration
  - expand query duration

Acceptance criteria:
- Search and expand endpoints remain responsive on current staged dataset.
- Query plans use intended indexes for search-heavy endpoints.

### 4) Testing and CI-Script Maturity
- Extend backend tests beyond smoke:
  - repository unit tests for exact/prefix ranking
  - graph expansion service tests for dedupe and cap logic
  - songs service tests for missing-neighbor and 404 behavior
- Add frontend checks:
  - `npm run build`
  - lint/type checks in scripted workflow
- Consolidate into one developer test command in repo root.

Acceptance criteria:
- Single script executes backend smoke + backend unit tests + frontend build checks.
- Failures are explicit and actionable.

### 5) Docs and Operations
- Update docs with:
  - troubleshooting playbook for common local failures
  - known Cosmograph alias constraint from Phase 4
  - expected warnings vs blocking failures in frontend build
- Add short runbook for data reload cycle:
  - migrate
  - validate
  - load-stage
  - smoke

Acceptance criteria:
- A new contributor can recover a broken local setup using docs only.

## Suggested Implementation Order
1. Backend index/query guardrails.
2. Frontend error/empty/loading-state standardization.
3. Expansion/session control hardening.
4. Test suite expansion + unified test script.
5. Docs completion and cleanup.

## Out of Scope
- Auth and user accounts.
- Multi-tenant data model.
- Large-scale distributed ingestion.
- Full production deployment platform.

## Definition of Done
- Core flows (song search seed, artist seed, genre seed, expand, song page) work reliably.
- Smoke tests and build checks pass from a single command.
- Docs are aligned with actual runtime behavior and known constraints.
