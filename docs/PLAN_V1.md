# Music Graph Webapp Plan

## 1. Product Summary

This webapp is a search-first music graph explorer built around an interactive graph displayed directly on the homepage.

Users can:
- search by **song title**, **artist**, or **genre**
- view a large interactive graph window on the main page
- click nodes to inspect songs and open a simple song page
- expand outward through each song's 5 precomputed nearest neighbors
- continue exploring until a hard visible node cap is reached

The product is a **local graph exploration app**, not a full 3.3 million node global graph viewer.

---

## 2. Locked Decisions

The following decisions are fixed for this build:

- **Frontend graph library:** Cosmograph React
- **Backend:** FastAPI + Python
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL
- **Source data:** Parquet file
- **Dataset fields:** song ID, song name, artist, genre, and 5 ranked neighbor song IDs
- **Homepage layout:** graph is embedded directly on the main page in a large central window
- **Search modes:** song, artist, genre
- **Search ranking for V1:** exact matches first, prefix matches second
- **Node click behavior:** clicking a node opens a basic song page
- **Artist seed behavior:** load all songs by that artist, capped at 300
- **Genre seed behavior:** load a random sample of songs in that genre
- **Expansion behavior:** indefinite until hard graph cap is reached
- **Commercial scope:** none

---

## 3. Product Goal

Build a webapp that makes exploring song similarity intuitive and visually engaging while keeping the technical design simple, modular, and maintainable.

The app should feel:
- fast
- clean
- easy to understand
- exploratory
- centered around discovery through graph navigation

---

## 4. Core Product Rules

### 4.1 Search Rules
Users can search by:
- song title
- artist
- genre

Search ranking in V1:
1. exact matches
2. prefix matches

No fuzzy matching in V1.

### 4.2 Graph Rules
- each song has exactly 5 precomputed similar neighbors
- graph expansion only uses those stored neighbors
- no edge semantics work is needed
- graph must deduplicate nodes already visible
- graph expansion stops when node cap is reached

### 4.3 Rendering Rules
- do not attempt to render the full dataset
- only load local subgraphs based on search seeds and expansions
- target visual handling up to about 1000 visible nodes

---

## 5. Tech Stack

## Frontend
- Next.js
- TypeScript
- Tailwind CSS
- `@cosmograph/react`

## Backend
- FastAPI
- Python
- SQLAlchemy
- Pydantic

## Database
- PostgreSQL

## Data Source
- Parquet for source ingestion
- PostgreSQL as application runtime database

---

## 6. Main User Flows

## Flow A: Song Search
1. User selects Song mode
2. User enters a song title
3. Backend returns exact and prefix matches
4. User selects a result
5. Homepage graph loads:
   - selected song
   - its 5 similar neighbors
6. User expands, recenters, inspects, or opens a song page

## Flow B: Artist Search
1. User selects Artist mode
2. User enters an artist name
3. Backend returns exact and prefix matches
4. User selects an artist
5. Homepage graph loads all songs by that artist, up to 300
6. User expands outward through similar songs

## Flow C: Genre Search
1. User selects Genre mode
2. User enters a genre
3. Backend returns exact and prefix matches
4. User selects a genre
5. Homepage graph loads a random sample of songs in that genre
6. User expands outward from those seeds

## Flow D: Node Interaction
1. User clicks a node
2. Right sidebar updates with selected song info
3. User can:
   - expand selected node
   - recenter on selected node
   - open song detail page

## Flow E: Song Page
1. User navigates to `/song/[songId]`
2. Song page shows:
   - song title
   - artist
   - genre
   - list of 5 similar songs
3. User can return to the homepage graph and start from that song

---

## 7. Homepage Layout

The homepage is the primary application surface.

## 7.1 Layout Structure

### Top Bar
- app name / logo
- unified search bar
- mode selector: Song / Artist / Genre
- reset graph button

### Main Body
- large central graph window using Cosmograph
- left sidebar for controls and search context
- right sidebar for selected node details and actions

## 7.2 Layout Priorities
- graph should occupy most of the page width and height
- sidebars should be collapsible
- controls should stay lightweight
- the graph should visually feel like the main product feature

---

## 8. Graph Design

## 8.1 Seed Behavior

### Song Seed
Initial graph contents:
- selected song
- 5 outgoing neighbor songs

### Artist Seed
Initial graph contents:
- all songs by the artist
- capped at 300 songs

Important:
- do not auto-expand neighbors for every artist song on first load
- initial artist graph should stay artist-centered

### Genre Seed
Initial graph contents:
- random sample of songs in the selected genre

Recommended default:
- 25 to 75 seed songs depending on visual testing

## 8.2 Expansion Behavior
Expansion must:
- look up neighbors for selected visible nodes
- add only unseen nodes
- add only unseen edges
- stop when node cap is reached

## 8.3 Node Cap
Hard cap:
- **1000 visible nodes**

When reached:
- disable expansion controls
- show clear message that limit has been reached
- encourage recentering, isolating, or resetting

## 8.4 Deduplication
The graph layer must:
- treat each song ID as globally unique within the active session
- never render duplicate nodes
- merge edges against existing nodes

## 8.5 Labels and Visual Clarity
To reduce clutter:
- show labels mainly for selected nodes
- optionally show labels on hover
- keep edge styling subtle
- keep node sizing simple in V1

---

## 9. Search Design

## 9.1 Search Modes
- song
- artist
- genre

## 9.2 Ranking Logic
V1 ranking only:
1. exact match
2. prefix match

Examples:
- exact title equals query
- title begins with query
- exact artist equals query
- artist begins with query
- exact genre equals query
- genre begins with query

## 9.3 Search UI Behavior
- search bar should update suggestions as user types
- results should be grouped by active mode only
- no mixed-type result lists in V1
- keep the search experience predictable and simple

---

## 10. Song Detail Page

## Route
- `/song/[songId]`

## Contents
- song title
- artist
- genre
- list of 5 neighbor songs
- button to open the graph centered on this song
- button to go back to homepage

## Design Rule
Keep this page minimal and informational.
Do not overdesign it in V1.

---

## 11. Database Plan

## 11.1 Core Tables

### `songs`
Fields:
- `song_id` primary key
- `song_name`
- `artist_name`
- `genre`

### `song_neighbors`
Fields:
- `source_song_id`
- `target_song_id`
- `neighbor_rank`

Rules:
- each source song should have exactly 5 rows
- `neighbor_rank` should be 1 through 5

## 11.2 Recommended Indexes
- index on `song_name`
- index on `artist_name`
- index on `genre`
- index on `source_song_id` in `song_neighbors`
- functional lowercase indexes for case-insensitive exact and prefix search if needed

## 11.3 ORM Layer
Use SQLAlchemy with:
- explicit models
- explicit relationships where useful
- clean query service layer
- no business logic inside route handlers

---

## 12. Parquet Ingestion Plan

Phase 1 is assumed complete in Parquet, but application setup still requires loading that data into PostgreSQL.

## 12.1 Ingestion Responsibilities
The ingestion worker/script should:
1. read the Parquet file
2. populate `songs`
3. unpivot the 5 neighbor columns into `song_neighbors`
4. assign `neighbor_rank` based on the original column index
5. validate that every song has exactly 5 neighbors
6. create indexes after data load

## 12.2 Validation Checks
- no missing primary song IDs
- no duplicate song IDs
- every song has exactly 5 neighbor rows
- all neighbor IDs reference valid songs if possible
- artist and genre fields are present

---

## 13. API Plan

## 13.1 Search Endpoints
- `GET /api/search/songs?q=...`
- `GET /api/search/artists?q=...`
- `GET /api/search/genres?q=...`

Behavior:
- exact matches first
- prefix matches second
- limited result count for autocomplete responsiveness

## 13.2 Graph Seed Endpoints
- `GET /api/graph/song/{song_id}`
- `GET /api/graph/artist/{artist_name}`
- `GET /api/graph/genre/{genre_name}`

## 13.3 Expansion Endpoint
- `POST /api/graph/expand`

Input:
- visible node IDs
- selected node IDs
- expansion mode

Output:
- new nodes
- new edges
- node limit status

## 13.4 Song Detail Endpoint
- `GET /api/song/{song_id}`

Returns:
- song info
- 5 neighbor songs
- enough information for song page rendering

---

## 14. Graph Payload Contract

All graph endpoints should return consistent data structures.

## 14.1 Node Shape
```json
{
  "id": "song_123",
  "label": "Song Title",
  "songName": "Song Title",
  "artist": "Artist Name",
  "genre": "Rock"
}

14.2 Edge Shape

{
  "id": "song_123__song_456",
  "source": "song_123",
  "target": "song_456",
  "rank": 1
}

14.3 Full Graph Response

{
  "nodes": [],
  "edges": [],
  "meta": {
    "seedType": "song",
    "seedValue": "song_123",
    "visibleNodeCount": 6,
    "visibleEdgeCount": 5,
    "reachedLimit": false
  }
}

15. Frontend State Plan
15.1 Search State

search mode

query string

results

loading state

selected result
15.2 Graph State

visible nodes

visible edges

selected node ID

seed type

seed value

limit reached flag

expansion history
15.3 UI State

sidebar open/closed state

loading states

error messages
15.4 Recommended Tools

React Query for server data

Zustand for UI and graph state
16. File Structure
16.1 Frontend
src/
  app/
    page.tsx
    song/[id]/page.tsx
  components/
    search/
      SearchBar.tsx
      SearchModeTabs.tsx
      SearchResults.tsx
    graph/
      GraphCanvas.tsx
      GraphControls.tsx
      GraphLegend.tsx
    sidebar/
      LeftSidebar.tsx
      RightSidebar.tsx
      SelectedSongPanel.tsx
    song/
      SongDetailCard.tsx
      SimilarSongsList.tsx
  lib/
    api.ts
    graph.ts
    search.ts
  store/
    graphStore.ts
    uiStore.ts
  types/
    graph.ts
    song.ts

16.2 Backend
app/
  main.py
  api/
    routes/
      search.py
      graph.py
      songs.py
  core/
    config.py
    database.py
  db/
    models/
      song.py
      song_neighbor.py
    session.py
  schemas/
    graph.py
    search.py
    song.py
  services/
    search_service.py
    graph_service.py
    songs_service.py
    ingestion_service.py
  repositories/
    song_repository.py
    graph_repository.py
    search_repository.py
  scripts/
    load_parquet.py

17. Build Phases
Phase 2: Load Parquet into PostgreSQL
Goal:

Move the prepared Parquet output into PostgreSQL.
Tasks:


read Parquet

populate songs table

populate song_neighbors table

validate rank mapping

add indexes
Deliverable:


PostgreSQL database ready for app use
Phase 3: FastAPI Backend
Goal:

Build the API layer.
Tasks:


create SQLAlchemy models

create repositories

create services

build search endpoints

build graph seed endpoints

build expand endpoint

build song detail endpoint
Deliverable:


tested API with stable payloads
Phase 4: Homepage UI Shell
Goal:

Build the homepage layout around the embedded graph.
Tasks:


create top bar

create graph container

create left and right sidebars

add loading and empty states
Deliverable:


homepage structure complete
Phase 5: Cosmograph Integration
Goal:

Render graph data directly on homepage.
Tasks:


map API graph payloads into Cosmograph

support node selection

support hover

support pan and zoom

support recentering

support expansion controls
Deliverable:


working homepage graph explorer
Phase 6: Song Detail Page
Goal:

Create song detail routing and page rendering.
Tasks:


build /song/[id]

load song detail endpoint

show similar songs

add "open in graph" action
Deliverable:


song page complete
Phase 7: Polish
Goal:

Make the app feel stable and complete.
Tasks:


refine search interaction

refine graph styling

tune artist and genre seeds

improve limit messaging

improve empty states

test common flows
Deliverable:


polished V1
18. Coding Style and Implementation Principles
All code should follow these principles:

18.1 Simplicity

keep code simple

prefer straightforward solutions over clever ones

avoid overengineering
18.2 Modularity

separate concerns clearly

keep routes, services, repositories, and models distinct

keep frontend components focused and reusable
18.3 OOP Principles

use object-oriented design where it improves clarity

keep data models, repositories, and service classes well scoped

avoid huge procedural files that combine too many responsibilities
18.4 Organization

keep file structure organized and predictable

group related files together

avoid dumping unrelated logic into shared utility files
18.5 Maintainability

use clear names

keep functions and classes small

write code so another developer can navigate it easily
19. Documentation Requirements for the Worker
The worker should create .md files whenever possible to document feature design and code-specific information.

19.1 Purpose
These Markdown documents should help future development stay organized and understandable.

19.2 What to Document
Create .md files for:


feature design decisions

API behavior summaries

graph interaction logic

data flow explanations

database design notes

ingestion assumptions

important implementation details for specific modules
19.3 Example Documentation Files
docs/
  feature-search.md
  feature-graph-homepage.md
  feature-song-page.md
  api-contracts.md
  database-schema.md
  ingestion-notes.md
  graph-expansion-rules.md

19.4 Documentation Expectations
Each .md should include:


what the feature or module does

key assumptions

important inputs and outputs

major constraints

any tricky logic worth preserving for future work
These docs should be written when possible during implementation, not postponed until the end.
20. Main Risks
Risk 1: Artist-start graphs are too dense
Fix:


cap artist songs at 300

do not auto-expand neighbors on first render

keep labels restrained
Risk 2: Genre-start graphs feel too random
Fix:


choose a reasonable seed sample size

allow resetting and re-running the genre seed

tune sample count through testing
Risk 3: Infinite expansion gets visually chaotic
Fix:


hard cap at 1000 nodes

provide isolate, reset, and recenter controls

keep graph actions reversible
Risk 4: Search feels limited without fuzzy matching
Fix:


make exact and prefix logic crisp

normalize case consistently

return clean and relevant result sets
Risk 5: Homepage layout becomes cluttered
Fix:


keep graph dominant

make sidebars collapsible

keep controls minimal in V1
21. Final Recommendation
Build V1 as:


Next.js frontend

FastAPI backend

SQLAlchemy ORM

PostgreSQL database

Cosmograph embedded directly on homepage

song, artist, and genre search

exact and prefix matching only

simple song detail pages

hard 1000-node graph cap

clear modular architecture

organized documentation in .md files during implementation
