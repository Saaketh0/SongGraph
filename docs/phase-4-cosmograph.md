# Phase 4 Cosmograph Integration

## Implemented
- Added Cosmograph dependency to frontend:
  - `@cosmograph/react`
- Added graph canvas component:
  - `frontend/components/graph/GraphCanvas.tsx`
- Updated graph panel to render Cosmograph canvas and keep existing controls:
  - `frontend/components/graph/GraphPanel.tsx`
- Added canvas and graph panel styles:
  - `frontend/app/globals.css`
- Added webpack alias fix for Cosmograph package asset import:
  - `frontend/next.config.ts`

## Constraint: Required Alias
- Cosmograph currently imports internal assets using `@/...` paths from inside the package.
- Because of that, `frontend/next.config.ts` must keep:
  - `config.resolve.alias["@"] = path.resolve(process.cwd(), "node_modules/@cosmograph/cosmograph")`
- Removing or renaming this alias causes production build failure with:
  - `Module not found: Can't resolve '@/cosmograph/style.module.css'`
- Decision: keep this alias for now and revisit only when Cosmograph package behavior changes or we isolate it behind a safer bundling boundary.

## Behavior
- Graph uses API-provided nodes and edges from existing Phase 3 state.
- Node click in Cosmograph selects the node and updates right sidebar details.
- Expand/reset controls continue to call backend-driven graph actions.
- Song detail page and "Open in graph" flow remain intact.

## Build Status
- `npm run build` passes.
- Build shows non-blocking warnings from duckdb wasm dependencies in Cosmograph transitive packages.
