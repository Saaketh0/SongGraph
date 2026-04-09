from __future__ import annotations

import argparse
from pathlib import Path

from graph_pipeline.build_edges import build_performs_edges
from graph_pipeline.build_nodes import add_graph_ids, build_artist_nodes, build_song_nodes
from graph_pipeline.clean_data import clean_song_dataset
from graph_pipeline.export_graph import export_graph_json, validate_graph
from graph_pipeline.load_data import load_song_dataset
from graph_pipeline.similarity import build_similarity_edges


DEFAULT_OUTPUT_PATH = "data/graph.json"
DEFAULT_DATASET_ID = "RecSysTUM/Million_Song_Dataset"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a music graph JSON from a Spotify-style songs dataset."
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optional local CSV path to load instead of a Hugging Face dataset.",
    )
    parser.add_argument(
        "--dataset-id",
        default=DEFAULT_DATASET_ID,
        help="Hugging Face dataset ID to load with datasets.load_dataset(...).",
    )
    parser.add_argument(
        "--dataset-split",
        default="train",
        help="Split name to load from the Hugging Face dataset.",
    )
    parser.add_argument(
        "--load-limit",
        type=int,
        default=5000,
        help="Optional row cap applied while loading a Hugging Face split.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help="Destination path for the exported graph JSON.",
    )
    parser.add_argument(
        "--max-songs",
        type=int,
        default=500,
        help="Optional cap on retained songs after cleaning.",
    )
    parser.add_argument(
        "--similarity-k",
        type=int,
        default=4,
        help="Number of similar song neighbors to connect for each song.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw_df = load_song_dataset(
        input_path=args.input,
        dataset_id=args.dataset_id,
        split=args.dataset_split,
        load_limit=args.load_limit,
    )
    cleaned_df = clean_song_dataset(raw_df, max_songs=args.max_songs)
    songs_df = add_graph_ids(cleaned_df)

    nodes = build_artist_nodes(songs_df) + build_song_nodes(songs_df)
    links = build_performs_edges(songs_df) + build_similarity_edges(
        songs_df,
        k=args.similarity_k,
    )

    graph = validate_graph(
        {
            "nodes": nodes,
            "links": links,
            "meta": {
                "source": args.input or args.dataset_id,
                "song_count": len(songs_df),
                "artist_count": int(songs_df["artist_id"].nunique()),
                "similarity_k": args.similarity_k,
            },
        }
    )

    output_path = Path(args.output)
    export_graph_json(graph, output_path)
    print(
        f"Graph written to {output_path} "
        f"with {len(graph['nodes'])} nodes and {len(graph['links'])} links."
    )


if __name__ == "__main__":
    main()
