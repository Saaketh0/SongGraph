from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text


os.environ.setdefault("READ_FROM_STAGE", "true")

try:
    from fastapi.testclient import TestClient
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "fastapi.testclient could not be imported. Install backend dependencies first."
    ) from exc

from app.core.database import engine
from app.main import app


@dataclass(slots=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


SMOKE_SONGS = [
    {"song_id": "smoke_s1", "song_name": "zz_smoke_alpha", "artist_name": "smoke_artist_a", "genre": "smoke_genre_rock"},
    {"song_id": "smoke_s2", "song_name": "zz_smoke_alpine", "artist_name": "smoke_artist_a", "genre": "smoke_genre_rock"},
    {"song_id": "smoke_s3", "song_name": "zz_smoke_beta", "artist_name": "smoke_artist_b", "genre": "smoke_genre_pop"},
    {"song_id": "smoke_s4", "song_name": "zz_smoke_gamma", "artist_name": "smoke_artist_c", "genre": "smoke_genre_jazz"},
    {"song_id": "smoke_s5", "song_name": "zz_smoke_delta", "artist_name": "smoke_artist_d", "genre": "smoke_genre_rock"},
    {"song_id": "smoke_s6", "song_name": "zz_smoke_echo", "artist_name": "smoke_artist_e", "genre": "smoke_genre_rock"},
]

SMOKE_NEIGHBORS = [
    {"source_song_id": "smoke_s1", "target_song_id": "smoke_s2", "neighbor_rank": 1},
    {"source_song_id": "smoke_s1", "target_song_id": "smoke_s3", "neighbor_rank": 2},
    {"source_song_id": "smoke_s1", "target_song_id": "smoke_s4", "neighbor_rank": 3},
    {"source_song_id": "smoke_s1", "target_song_id": "smoke_s5", "neighbor_rank": 4},
    {"source_song_id": "smoke_s1", "target_song_id": "smoke_s6", "neighbor_rank": 5},
]


def seed_smoke_fixture() -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "DELETE FROM song_neighbors_stage "
                "WHERE source_song_id LIKE 'smoke_%' OR target_song_id LIKE 'smoke_%'"
            )
        )
        conn.execute(text("DELETE FROM songs_stage WHERE song_id LIKE 'smoke_%'"))

        conn.execute(
            text(
                "INSERT INTO songs_stage (song_id, song_name, artist_name, genre) "
                "VALUES (:song_id, :song_name, :artist_name, :genre)"
            ),
            SMOKE_SONGS,
        )
        conn.execute(
            text(
                "INSERT INTO song_neighbors_stage (source_song_id, target_song_id, neighbor_rank) "
                "VALUES (:source_song_id, :target_song_id, :neighbor_rank)"
            ),
            SMOKE_NEIGHBORS,
        )


def _check_status(name: str, status_code: int, expected: int) -> CheckResult:
    passed = status_code == expected
    detail = f"expected={expected}, actual={status_code}"
    return CheckResult(name=name, passed=passed, detail=detail)


def _as_json(response) -> dict[str, Any]:
    try:
        return response.json()
    except Exception:
        return {}


def run_smoke_checks() -> list[CheckResult]:
    client = TestClient(app)
    checks: list[CheckResult] = []

    songs_resp = client.get("/api/search/songs", params={"q": "zz_smoke_al"})
    checks.append(_check_status("search_songs_status", songs_resp.status_code, 200))
    songs_payload = _as_json(songs_resp)
    checks.append(
        CheckResult(
            name="search_songs_result_presence",
            passed=bool(songs_payload.get("results")),
            detail=f"result_count={len(songs_payload.get('results', []))}",
        )
    )

    artists_resp = client.get("/api/search/artists", params={"q": "smoke_artist"})
    checks.append(_check_status("search_artists_status", artists_resp.status_code, 200))

    genres_resp = client.get("/api/search/genres", params={"q": "smoke_genre_r"})
    checks.append(_check_status("search_genres_status", genres_resp.status_code, 200))

    seed_resp = client.get("/api/graph/song/smoke_s1")
    checks.append(_check_status("graph_seed_song_status", seed_resp.status_code, 200))
    seed_payload = _as_json(seed_resp)
    checks.append(
        CheckResult(
            name="graph_seed_song_counts",
            passed=len(seed_payload.get("nodes", [])) >= 6 and len(seed_payload.get("edges", [])) >= 5,
            detail=(
                f"nodes={len(seed_payload.get('nodes', []))}, "
                f"edges={len(seed_payload.get('edges', []))}"
            ),
        )
    )

    expand_resp = client.post(
        "/api/graph/expand",
        json={
            "visibleNodeIds": ["smoke_s1"],
            "visibleEdgeIds": [],
            "selectedNodeIds": ["smoke_s1"],
            "expansionMode": "selected",
        },
    )
    checks.append(_check_status("graph_expand_status", expand_resp.status_code, 200))
    expand_payload = _as_json(expand_resp)
    checks.append(
        CheckResult(
            name="graph_expand_counts",
            passed=len(expand_payload.get("nodes", [])) >= 5 and len(expand_payload.get("edges", [])) >= 5,
            detail=(
                f"new_nodes={len(expand_payload.get('nodes', []))}, "
                f"new_edges={len(expand_payload.get('edges', []))}"
            ),
        )
    )

    song_resp = client.get("/api/song/smoke_s1")
    checks.append(_check_status("song_detail_status", song_resp.status_code, 200))
    song_payload = _as_json(song_resp)
    checks.append(
        CheckResult(
            name="song_detail_similar_count",
            passed=len(song_payload.get("similarSongs", [])) == 5,
            detail=f"similar_count={len(song_payload.get('similarSongs', []))}",
        )
    )

    not_found_resp = client.get("/api/song/does-not-exist")
    checks.append(_check_status("song_detail_404_status", not_found_resp.status_code, 404))
    return checks


def main() -> None:
    seed_smoke_fixture()
    checks = run_smoke_checks()
    failures = [check for check in checks if not check.passed]

    summary = {
        "passed": len(failures) == 0,
        "total_checks": len(checks),
        "failed_checks": [{"name": c.name, "detail": c.detail} for c in failures],
        "checks": [{"name": c.name, "passed": c.passed, "detail": c.detail} for c in checks],
    }
    print(json.dumps(summary))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()

