#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import pickle
import re
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "Analysis" / "outputs" / "part2_taskA"
FIGURE_DIR = OUTPUT_ROOT / "figures"
TABLE_DIR = OUTPUT_ROOT / "tables"
GRAPH_DIR = OUTPUT_ROOT / "graphs"
TEXT_DIR = OUTPUT_ROOT / "reports"
MPL_CACHE_DIR = OUTPUT_ROOT / ".mplconfig"
XDG_CACHE_DIR = OUTPUT_ROOT / ".cache"

os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))

for path in (MPL_CACHE_DIR, XDG_CACHE_DIR):
    path.mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")

import networkx as nx
import osmnx as ox
import pandas as pd
from pyproj import Transformer
import matplotlib.pyplot as plt


DATA_DIR = PROJECT_ROOT / "Assessment" / "Part2_Data"
ACCIDENT_FILES = [DATA_DIR / f"accidents_{year}.csv" for year in range(2009, 2017)]
CRS_BNG = 27700
CRS_WGS84 = 4326
AREA_M2 = 1_000_000.0
GRID_SIZE_M = 1000

YEAR_COLUMN_MAP = {
    "2009": ("Easting", "Northing"),
    "2010": ("Easting", "Northing"),
    "2011": ("Easting", "Northing"),
    "2012": ("Easting", "Northing"),
    "2013": ("Grid Ref: Easting", "Grid Ref: Northing"),
    "2014": ("Grid Ref: Easting", "Grid Ref: Northing"),
    "2015": ("Grid Ref: Easting", "Grid Ref: Northing"),
    "2016": ("Grid Ref: Easting", "Grid Ref: Northing"),
}


@dataclass(frozen=True)
class AccidentSummary:
    year: int
    rows: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Part 2 Task A spatial network pipeline.")
    parser.add_argument(
        "--download-timeout",
        type=int,
        default=120,
        help="Timeout in seconds for the road network download step.",
    )
    return parser.parse_args()


def ensure_dirs() -> None:
    for path in [OUTPUT_ROOT, FIGURE_DIR, TABLE_DIR, GRAPH_DIR, TEXT_DIR, MPL_CACHE_DIR, XDG_CACHE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def normalize_accident_frame(df: pd.DataFrame, year: int) -> pd.DataFrame:
    if year >= 2013:
        df = df.rename(
            columns={
                "Grid Ref: Easting": "Easting",
                "Grid Ref: Northing": "Northing",
            }
        )

    keep = ["Easting", "Northing"]
    if not set(keep).issubset(df.columns):
        raise KeyError(f"Missing coordinate columns for {year}: {sorted(df.columns)}")

    frame = df[keep].copy()
    frame["year"] = year
    frame["Easting"] = pd.to_numeric(frame["Easting"], errors="coerce")
    frame["Northing"] = pd.to_numeric(frame["Northing"], errors="coerce")
    frame = frame.dropna(subset=["Easting", "Northing"])
    frame = frame[(frame["Easting"] > 0) & (frame["Northing"] > 0)]
    return frame


def load_accidents() -> tuple[pd.DataFrame, list[AccidentSummary]]:
    summaries: list[AccidentSummary] = []
    frames: list[pd.DataFrame] = []

    for path in ACCIDENT_FILES:
        year = int(re.search(r"(\d{4})", path.stem).group(1))
        df = pd.read_csv(path, encoding="latin1", low_memory=False)
        normalized = normalize_accident_frame(df, year)
        summaries.append(
            AccidentSummary(
                year=year,
                rows=int(len(normalized)),
                x_min=float(normalized["Easting"].min()),
                x_max=float(normalized["Easting"].max()),
                y_min=float(normalized["Northing"].min()),
                y_max=float(normalized["Northing"].max()),
            )
        )
        frames.append(normalized)

    all_accidents = pd.concat(frames, ignore_index=True)
    transformer = Transformer.from_crs(CRS_BNG, CRS_WGS84, always_xy=True)
    lon, lat = transformer.transform(all_accidents["Easting"].to_numpy(), all_accidents["Northing"].to_numpy())
    all_accidents["lon"] = lon
    all_accidents["lat"] = lat
    return all_accidents, summaries


def build_candidate_grid(accidents: pd.DataFrame) -> pd.DataFrame:
    grid = accidents.copy()
    grid["cell_x"] = (grid["Easting"] // GRID_SIZE_M * GRID_SIZE_M).astype(int)
    grid["cell_y"] = (grid["Northing"] // GRID_SIZE_M * GRID_SIZE_M).astype(int)
    counts = grid.groupby(["cell_x", "cell_y"], as_index=False).size().rename(columns={"size": "accident_count"})
    counts["center_x"] = counts["cell_x"] + GRID_SIZE_M / 2
    counts["center_y"] = counts["cell_y"] + GRID_SIZE_M / 2
    centroid_x = float(accidents["Easting"].mean())
    centroid_y = float(accidents["Northing"].mean())
    counts["distance_to_centroid_m"] = ((counts["center_x"] - centroid_x) ** 2 + (counts["center_y"] - centroid_y) ** 2) ** 0.5
    counts = counts.sort_values(
        by=["accident_count", "distance_to_centroid_m", "cell_y", "cell_x"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)
    return counts


def choose_candidate_square(grid_counts: pd.DataFrame) -> dict[str, Any]:
    selected = grid_counts.iloc[0].to_dict()
    cell = {
        "cell_x": int(selected["cell_x"]),
        "cell_y": int(selected["cell_y"]),
        "x_min": int(selected["cell_x"]),
        "x_max": int(selected["cell_x"]) + GRID_SIZE_M,
        "y_min": int(selected["cell_y"]),
        "y_max": int(selected["cell_y"]) + GRID_SIZE_M,
        "center_x": float(selected["center_x"]),
        "center_y": float(selected["center_y"]),
        "accident_count": int(selected["accident_count"]),
        "distance_to_centroid_m": float(selected["distance_to_centroid_m"]),
    }
    return cell


def square_to_bbox(square: dict[str, Any]) -> tuple[float, float, float, float]:
    transformer = Transformer.from_crs(CRS_BNG, CRS_WGS84, always_xy=True)
    corners = [
        transformer.transform(square["x_min"], square["y_min"]),
        transformer.transform(square["x_min"], square["y_max"]),
        transformer.transform(square["x_max"], square["y_min"]),
        transformer.transform(square["x_max"], square["y_max"]),
    ]
    lons = [lon for lon, _ in corners]
    lats = [lat for _, lat in corners]
    west, east = min(lons), max(lons)
    south, north = min(lats), max(lats)
    return west, south, east, north


def save_pickle(obj: Any, path: Path) -> None:
    with path.open("wb") as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def simplify_to_weighted_simple_graph(graph: nx.MultiDiGraph) -> nx.Graph:
    undirected = ox.convert.to_undirected(graph)
    simple = nx.Graph()
    simple.graph.update(graph.graph)
    for node, attrs in undirected.nodes(data=True):
        simple.add_node(node, **attrs)
    for u, v, attrs in undirected.edges(data=True):
        length = float(attrs.get("length", 1.0))
        if simple.has_edge(u, v):
            simple[u][v]["length"] = min(float(simple[u][v]["length"]), length)
        else:
            simple.add_edge(u, v, length=length)
    return simple


class DownloadTimeoutError(RuntimeError):
    pass


def _timeout_handler(signum: int, frame: Any) -> None:  # pragma: no cover - signal plumbing
    raise DownloadTimeoutError("Timed out while downloading the road network from OSMnx.")


def largest_connected_component(graph: nx.Graph) -> nx.Graph:
    if graph.number_of_nodes() == 0:
        return graph.copy()
    component = max(nx.connected_components(graph), key=len)
    return graph.subgraph(component).copy()


def compute_spatial_diameter(graph: nx.Graph) -> float:
    if graph.number_of_nodes() < 2:
        return 0.0
    lengths = dict(nx.all_pairs_dijkstra_path_length(graph, weight="length"))
    eccentricity = nx.eccentricity(graph, sp=lengths)
    return float(max(eccentricity.values()))


def plot_candidate_grid(grid_counts: pd.DataFrame, selected_square: dict[str, Any], accidents: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 8))
    pivot = grid_counts.pivot(index="cell_y", columns="cell_x", values="accident_count").sort_index(ascending=True)
    im = ax.imshow(
        pivot.to_numpy(),
        origin="lower",
        cmap="magma",
        extent=[
            float(pivot.columns.min()),
            float(pivot.columns.max() + GRID_SIZE_M),
            float(pivot.index.min()),
            float(pivot.index.max() + GRID_SIZE_M),
        ],
        aspect="equal",
    )
    fig.colorbar(im, ax=ax, label="Accident count")
    ax.scatter(accidents["Easting"].mean(), accidents["Northing"].mean(), s=80, c="cyan", marker="x", label="Accident centroid")
    ax.add_patch(
        plt.Rectangle(
            (selected_square["x_min"], selected_square["y_min"]),
            GRID_SIZE_M,
            GRID_SIZE_M,
            fill=False,
            edgecolor="lime",
            linewidth=2.5,
            label="Selected 1 km^2",
        )
    )
    ax.set_title("Leeds accident density by 1 km grid cell")
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    output = FIGURE_DIR / "accident_density_grid.png"
    fig.savefig(output, dpi=220)
    plt.close(fig)
    return output


def plot_road_network(graph: nx.MultiDiGraph, accidents: pd.DataFrame, square: dict[str, Any]) -> Path:
    fig, ax = plt.subplots(figsize=(10, 10))
    ox.plot_graph(
        graph,
        ax=ax,
        show=False,
        close=False,
        node_size=0,
        edge_color="#2b2d42",
        edge_linewidth=0.8,
        bgcolor="white",
    )
    ax.scatter(accidents["lon"], accidents["lat"], s=2, c="#ef233c", alpha=0.25, linewidths=0)
    transformer = Transformer.from_crs(CRS_BNG, CRS_WGS84, always_xy=True)
    corners = [
        transformer.transform(square["x_min"], square["y_min"]),
        transformer.transform(square["x_min"], square["y_max"]),
        transformer.transform(square["x_max"], square["y_min"]),
        transformer.transform(square["x_max"], square["y_max"]),
    ]
    west, south = min(lon for lon, _ in corners), min(lat for _, lat in corners)
    east, north = max(lon for lon, _ in corners), max(lat for _, lat in corners)
    ax.add_patch(
        plt.Rectangle(
            (west, south),
            east - west,
            north - south,
            fill=False,
            edgecolor="#06d6a0",
            linewidth=2.0,
            label="Selected 1 km^2",
        )
    )
    ax.legend(loc="upper right")
    ax.set_title("Road network and accidents in selected Leeds area")
    fig.tight_layout()
    output = FIGURE_DIR / "road_network_selected_area.png"
    fig.savefig(output, dpi=220)
    plt.close(fig)
    return output


def road_network_stats(graph: nx.MultiDiGraph) -> dict[str, Any]:
    stats = ox.stats.basic_stats(graph, area=AREA_M2)
    simple = simplify_to_weighted_simple_graph(graph)
    lcc = largest_connected_component(simple)
    spatial_diameter = compute_spatial_diameter(lcc)
    planar, _ = nx.check_planarity(simple)
    stats.update(
        {
            "spatial_diameter_m": spatial_diameter,
            "planar": bool(planar),
            "nodes_total": int(graph.number_of_nodes()),
            "edges_total": int(graph.number_of_edges()),
            "largest_component_nodes": int(lcc.number_of_nodes()),
            "largest_component_edges": int(lcc.number_of_edges()),
        }
    )
    return stats


def write_outputs(
    accidents: pd.DataFrame,
    accident_summaries: list[AccidentSummary],
    grid_counts: pd.DataFrame,
    selected_square: dict[str, Any],
    road_graph: nx.MultiDiGraph | None,
    road_stats: dict[str, Any] | None,
    figures: dict[str, Path],
    error: str | None = None,
) -> None:
    grid_counts.to_csv(TABLE_DIR / "candidate_grid_counts.csv", index=False)
    accident_summaries_df = pd.DataFrame([summary.__dict__ for summary in accident_summaries])
    accident_summaries_df.to_csv(TABLE_DIR / "accident_year_summaries.csv", index=False)

    selected = {
        "selected_square": selected_square,
        "accident_year_total_rows": int(len(accidents)),
        "accident_years": [summary.year for summary in accident_summaries],
        "figures": {key: str(value.relative_to(OUTPUT_ROOT)) for key, value in figures.items()},
    }

    if road_stats is not None and road_graph is not None:
        save_pickle(simplify_to_weighted_simple_graph(road_graph), GRAPH_DIR / "road_network_simple_graph.pickle")
        road_stats_clean = {}
        for key, value in road_stats.items():
            if isinstance(value, (pd.Series, pd.Index)):
                road_stats_clean[key] = value.to_dict()
            elif isinstance(value, (float, int, bool, str)) or value is None:
                road_stats_clean[key] = value
            else:
                road_stats_clean[key] = str(value)
        selected["road_network_stats"] = road_stats_clean
    else:
        selected["road_network_stats"] = None

    if error:
        selected["blocker"] = error

    (OUTPUT_ROOT / "summary.json").write_text(json.dumps(selected, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# Part 2 Task A Summary",
        "",
        "## Accident data",
        "",
        accident_summaries_df.to_markdown(index=False),
        "",
        "## Selected 1 km^2 square",
        "",
        f"- Cell origin: `{selected_square['cell_x']}, {selected_square['cell_y']}`",
        f"- Accident count in cell: `{selected_square['accident_count']}`",
        f"- Distance to accident centroid: `{selected_square['distance_to_centroid_m']:.1f} m`",
        f"- BNG bbox: `{selected_square['x_min']}, {selected_square['y_min']}` to `{selected_square['x_max']}, {selected_square['y_max']}`",
        "",
        "## Output artifacts",
        "",
    ]
    for name, path in figures.items():
        md_lines.append(f"- {name}: `{path.relative_to(OUTPUT_ROOT)}`")

    if road_stats is not None:
        md_lines.extend(
            [
                "",
                "## Road network stats",
                "",
                pd.DataFrame([road_stats]).to_markdown(index=False),
            ]
        )
    if error:
        md_lines.extend(["", "## Blocker", "", error])

    (TEXT_DIR / "summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    ensure_dirs()

    accidents, accident_summaries = load_accidents()
    grid_counts = build_candidate_grid(accidents)
    selected_square = choose_candidate_square(grid_counts)

    grid_figure = plot_candidate_grid(grid_counts, selected_square, accidents)

    road_graph: nx.MultiDiGraph | None = None
    road_stats: dict[str, Any] | None = None
    road_figure: Path | None = None
    error: str | None = None

    try:
        west, south, east, north = square_to_bbox(selected_square)
        ox.settings.use_cache = True
        ox.settings.log_console = False
        if hasattr(ox.settings, "requests_timeout"):
            ox.settings.requests_timeout = args.download_timeout
        previous_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(args.download_timeout)
        try:
            road_graph = ox.graph_from_bbox(
                bbox=(west, south, east, north),
                network_type="drive",
                simplify=True,
                retain_all=False,
                truncate_by_edge=True,
            )
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)
        road_figure = plot_road_network(road_graph, accidents, selected_square)
        road_stats = road_network_stats(road_graph)
        road_graph.graph["selected_square_bng"] = selected_square
        road_graph.graph["selected_square_bbox_wgs84"] = {
            "west": west,
            "south": south,
            "east": east,
            "north": north,
        }
        road_graph.graph["accident_count_in_square"] = selected_square["accident_count"]
        save_pickle(road_graph, GRAPH_DIR / "road_network_multidigraph.pickle")
    except DownloadTimeoutError as exc:  # pragma: no cover - environment-specific fallback
        error = (
            "Road network download timed out in the current environment. "
            f"Underlying error: {type(exc).__name__}: {exc}"
        )
    except Exception as exc:  # pragma: no cover - network-dependent fallback
        error = (
            "Road network download or analysis failed in the current environment. "
            f"Underlying error: {type(exc).__name__}: {exc}"
        )

    figures = {"accident_grid": grid_figure}
    if road_figure is not None:
        figures["road_network"] = road_figure

    write_outputs(
        accidents=accidents,
        accident_summaries=accident_summaries,
        grid_counts=grid_counts,
        selected_square=selected_square,
        road_graph=road_graph,
        road_stats=road_stats,
        figures=figures,
        error=error,
    )

    print(f"Loaded {len(accidents)} accident rows across 2009-2016.")
    print(
        "Selected square: "
        f"origin=({selected_square['cell_x']}, {selected_square['cell_y']}), "
        f"accidents={selected_square['accident_count']}"
    )
    if road_stats is not None:
        print(
            "Road network: "
            f"nodes={road_stats['n']}, edges={road_stats['m']}, "
            f"circuity={road_stats.get('circuity_avg', float('nan')):.4f}, "
            f"planar={road_stats['planar']}, spatial_diameter_m={road_stats['spatial_diameter_m']:.2f}"
        )
    else:
        print(error)


if __name__ == "__main__":
    main()
