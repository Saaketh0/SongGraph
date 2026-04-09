# Music Graph MVP Plan
DESIGN CONTRAINTS: KEEP THIS CODE AS MODULARIZED AND SIMPLE AS POSSIBLE. KEEP THIS IN MIND FOR ALL DESIGN CONTRAINTS.
IGNORE THE "data_cleaning" FOLDER COMPLETELY.
## Project Goal

Build a small MVP that:

- Takes a small song dataset
- Creates artist nodes
- Creates song nodes
- Creates connections between them
- Creates similar song connections
- Optionally creates artist similarity connections
- Displays everything in an interactive 3D graph

This will be built as a **simple property graph**, not a formal knowledge graph.

---

# Phase 1: Define the MVP Scope

## Core MVP Features

The MVP should support:

- Artist -> Song
- Song -> Similar Song
- Optional: Artist -> Artist

## Keep the Graph Small

Target scale:

- 200 to 1000 songs
- 50 to 300 artists
- Each song connected to 3 to 5 similar songs

This keeps the graph readable and prevents browser performance issues.

## Success Condition

The MVP is successful if you can:

- Load the dataset
- Generate nodes and edges
- Export a graph JSON
- Render it in 3D
- Visually explore clusters interactively

---

# Phase 2: Pick the Dataset

## Best Choice

Use a small Spotify style CSV containing columns like:

- artist
- track_name
- genre
- danceability
- energy
- tempo
- valence
- acousticness
- popularity

## Why This Works Well

- Artist-song edges come directly from the dataset
- Song similarity can be computed from numeric features
- No difficult joins required
- No external APIs needed for MVP

---

# Phase 3: Define the Graph Schema

Use a **simple property graph model**.

## Node Types

### Artist Node

Properties:

- id
- type = "artist"
- name

Example:

{
  "id": "artist:drake",
  "type": "artist",
  "name": "Drake"
}

### Song Node

Properties:

- id
- type = "song"
- name
- artist
- genre
- optional audio features
- popularity

Example:

{
  "id": "song:drake:hotline_bling",
  "type": "song",
  "name": "Hotline Bling",
  "artist": "Drake",
  "genre": "pop rap",
  "popularity": 82
}

## Edge Types

### PERFORMS

Artist -> Song

Example:

{
  "source": "artist:drake",
  "target": "song:drake:hotline_bling",
  "type": "PERFORMS"
}

### SIMILAR_TO

Song -> Song

Example:

{
  "source": "song:drake:hotline_bling",
  "target": "song:weeknd:starboy",
  "type": "SIMILAR_TO",
  "score": 0.91
}

### OPTIONAL: ARTIST_SIMILAR

Artist -> Artist

Example:

{
  "source": "artist:drake",
  "target": "artist:the_weeknd",
  "type": "ARTIST_SIMILAR",
  "score": 0.78
}

---

# Phase 4: Build the Data Pipeline

Use **Python**.

## Step 1: Load the CSV

Load dataset with pandas.

## Step 2: Clean the Data

Basic cleanup:

- Remove rows missing artist or track name
- Remove duplicates
- Standardize text fields
- Keep only relevant columns

## Step 3: Create Artist Nodes

Take unique artists and generate one node per artist.

## Step 4: Create Song Nodes

Create one song node per unique (artist, track_name).

## Step 5: Create Artist-Song Edges

For each row:

Artist -> Song edge

Edge type:

PERFORMS

---

# Phase 5: Create Song Similarity Edges

This is the intelligent component of the graph.

## Feature Columns

Select numeric columns such as:

- danceability
- energy
- tempo
- valence
- acousticness
- speechiness
- instrumentalness
- liveness
- popularity

## Normalize Features

Normalize values so one feature does not dominate others.

## Compute Similarity

Use:

- k-nearest neighbors
- cosine similarity

Recommended for MVP:

k-nearest neighbors

## Strategy

For each song:

- Find top k similar songs
- Create edges to those songs

Recommended value:

k = 3 to 5

Edge example:

{
  "source": "songA",
  "target": "songB",
  "type": "SIMILAR_TO",
  "score": 0.92
}

Important: Do not connect every song to every other song.

---

# Phase 6: Optional Artist to Artist Connections

Not required for first version.

Possible strategies:

## Option A: Genre Overlap

If artists share the same genre, connect them.

## Option B: Derived from Song Similarity

If many songs from Artist A are similar to songs from Artist B.

For MVP, genre overlap is easiest.

---

# Phase 7: Export the Graph

Export final structure as graph.json.

Example structure:

{
  "nodes": [
    {
      "id": "artist:drake",
      "type": "artist",
      "name": "Drake"
    },
    {
      "id": "song:drake:hotline_bling",
      "type": "song",
      "name": "Hotline Bling",
      "artist": "Drake"
    }
  ],
  "links": [
    {
      "source": "artist:drake",
      "target": "song:drake:hotline_bling",
      "type": "PERFORMS"
    },
    {
      "source": "song:drake:hotline_bling",
      "target": "song:weeknd:starboy",
      "type": "SIMILAR_TO",
      "score": 0.91
    }
  ]
}

---

# Phase 8: Build the Visualization

## Recommended Tools

- React
- react-force-graph-3d

Benefits:

- WebGL based
- Handles medium sized graphs easily
- Built in interaction features

## Visual Styling

Node Colors:

- Artist nodes one color
- Song nodes another color

Node Size:

- Artists larger
- Songs smaller

Edge Styling:

- PERFORMS edges thin
- SIMILAR_TO edges highlighted

Labels:

- Show on hover
- Optionally always show for artists

Avoid showing all labels simultaneously.

---

# Phase 9: Interaction Features

## Must Have

- Rotate
- Zoom
- Hover tooltip
- Click node

## Node Details

When clicking a node:

### Artist

Show:

- artist name
- number of songs

### Song

Show:

- song name
- artist
- genre
- similarity neighbors

---

# Phase 10: Folder Structure

music-graph-mvp/

data/
    songs.csv
    graph.json

scripts/
    build_graph.py

frontend/
    src/
        App.jsx
        components/

    package.json

---

# Phase 11: Suggested Implementation Order

Step 1

Load dataset.

Deliverable:

CSV loads successfully.

Step 2

Create artist and song nodes.

Deliverable:

Node list.

Step 3

Create PERFORMS edges.

Deliverable:

Basic graph structure.

Step 4

Compute song similarity edges.

Deliverable:

Similarity relationships.

Step 5

Export graph.json.

Deliverable:

Graph ready for visualization.

Step 6

Render graph in React.

Deliverable:

3D visualization.

Step 7

Add hover and click interactions.

Deliverable:

Interactive demo.

Step 8 (Optional)

Add artist similarity edges.

Deliverable:

Improved clustering.

---

# Technologies to Avoid in MVP

Do not use yet:

- Azure
- Databricks
- Neo4j
- RDF
- SPARQL
- Complex orchestration
- Large scale ingestion
- Many node types
- Many edge types

These are useful later but unnecessary for MVP validation.

---

# Future Scaling Plan

After MVP success, scale the system.

Possible improvements:

- Larger datasets
- Multiple music data sources
- Better entity resolution
- Richer artist metadata
- Graph database backend
- Azure storage
- Databricks transformations
- Offline similarity pipelines

Scale only after confirming the graph structure is useful.

---

# Final Summary

Build a small Python pipeline that converts a tiny music CSV into:

- artist nodes
- song nodes
- artist -> song edges
- song -> song similarity edges

Export the result as JSON and visualize it in a React 3D force graph.

---

# Quick Checklist

1. Obtain small Spotify style dataset
2. Clean dataset
3. Generate artist nodes
4. Generate song nodes
5. Create artist -> song edges
6. Compute similarity with kNN
7. Create song -> song edges
8. Export graph.json
9. Render using react-force-graph-3d
10. Add interaction features
