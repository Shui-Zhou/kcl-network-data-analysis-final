#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import pickle
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

import esda
import geopandas as gpd
import libpysal
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import pandas as pd
import spaghetti
from pyproj import Transformer


DATA_DIR = PROJECT_ROOT / "Assessment" / "Part2_Data"
INPUT_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part2_taskA"
OUTPUT_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part2_taskB"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"

ACCIDENT_FILES = [DATA_DIR / f"accidents_{year}.csv" for year in range(2009, 2017)]


def ensure_dirs() -> None:
    for path in [OUTPUT_DIR, TABLE_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_selected_square() -> dict[str, Any]:
    return json.loads((INPUT_DIR / "summary.json").read_text())["selected_square"]


def load_road_network() -> nx.MultiDiGraph:
    with (INPUT_DIR / "graphs" / "road_network_multidigraph.pickle").open("rb") as handle:
        return pickle.load(handle)


def normalize_accident_frame(df: pd.DataFrame, year: int) -> pd.DataFrame:
    if year >= 2013:
        df = df.rename(columns={"Grid Ref: Easting": "Easting", "Grid Ref: Northing": "Northing"})
    keep = [col for col in ["Reference Number", "Accident Date", "Time (24hr)", "Road Surface", "Weather Conditions", "Lighting Conditions", "Easting", "Northing"] if col in df.columns]
    frame = df[keep].copy()
    frame["year"] = year
    frame["Easting"] = pd.to_numeric(frame["Easting"], errors="coerce")
    frame["Northing"] = pd.to_numeric(frame["Northing"], errors="coerce")
    frame = frame.dropna(subset=["Easting", "Northing"])
    return frame


def load_square_accidents(square: dict[str, Any]) -> gpd.GeoDataFrame:
    frames = []
    for path in ACCIDENT_FILES:
        year = int(re.search(r"(\d{4})", path.stem).group(1))
        df = pd.read_csv(path, encoding="latin1", low_memory=False)
        frame = normalize_accident_frame(df, year)
        frame = frame[
            (frame["Easting"] >= square["x_min"])
            & (frame["Easting"] < square["x_max"])
            & (frame["Northing"] >= square["y_min"])
            & (frame["Northing"] < square["y_max"])
        ].copy()
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    gdf = gpd.GeoDataFrame(combined, geometry=gpd.points_from_xy(combined["Easting"], combined["Northing"]), crs="EPSG:27700")
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(gdf["Easting"].to_numpy(), gdf["Northing"].to_numpy())
    gdf["lon"] = lon
    gdf["lat"] = lat
    return gdf


def road_edges_gdf(graph: nx.MultiDiGraph) -> gpd.GeoDataFrame:
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).reset_index()
    if edges.crs is None:
        edges = edges.set_crs("EPSG:4326")
    return edges.to_crs("EPSG:27700")


def build_spaghetti_network(edges_gdf: gpd.GeoDataFrame) -> spaghetti.Network:
    line_gdf = edges_gdf[["geometry"]].copy()
    return spaghetti.Network(in_data=line_gdf)


def snap_to_network(ntw: spaghetti.Network, accidents_bng: gpd.GeoDataFrame) -> None:
    pts = accidents_bng[["geometry"]].copy()
    pts["accident_id"] = range(len(pts))
    ntw.snapobservations(pts, "accidents", idvariable="accident_id", attribute=False)


def network_k_summary(ntw: spaghetti.Network) -> dict[str, Any]:
    result = ntw.GlobalAutoK(
        ntw.pointpatterns["accidents"],
        nsteps=12,
        permutations=39,
        threshold=0.5,
        distribution="uniform",
    )
    observed = [float(x) for x in result.observed]
    upper = [float(x) for x in result.upperenvelope]
    lower = [float(x) for x in result.lowerenvelope]
    support = [float(x) for x in result.xaxis]
    exceed_steps = sum(1 for obs, up in zip(observed, upper) if obs > up)
    return {
        "support": support,
        "observed": observed,
        "upper_envelope": upper,
        "lower_envelope": lower,
        "observed_exceeds_upper_steps": int(exceed_steps),
        "max_gap_over_upper": float(max((obs - up) for obs, up in zip(observed, upper))),
    }


def plot_network_k(k_summary: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(k_summary["support"], k_summary["observed"], marker="o", linewidth=1.5, label="Observed K")
    ax.plot(k_summary["support"], k_summary["upper_envelope"], linestyle="--", linewidth=1.2, label="Upper envelope")
    ax.plot(k_summary["support"], k_summary["lower_envelope"], linestyle="--", linewidth=1.2, label="Lower envelope")
    ax.set_title("Network-constrained K-function")
    ax.set_xlabel("Network distance")
    ax.set_ylabel("K")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "network_k_function.png", dpi=220)
    plt.close(fig)


def assign_accidents_to_edges(accidents_wgs84: gpd.GeoDataFrame, graph: nx.MultiDiGraph, edges_bng: gpd.GeoDataFrame) -> pd.DataFrame:
    edge_records = []
    for _, row in accidents_wgs84.iterrows():
        u, v, key = ox.distance.nearest_edges(graph, row["lon"], row["lat"], return_dist=False)
        edge_records.append((u, v, key))

    mapped = accidents_wgs84.copy()
    mapped[["u", "v", "key"]] = pd.DataFrame(edge_records, index=mapped.index)

    edge_table = edges_bng[["u", "v", "key", "length", "geometry"]].copy()
    counts = mapped.groupby(["u", "v", "key"]).size().reset_index(name="accident_count")
    edge_counts = edge_table.merge(counts, on=["u", "v", "key"], how="left").fillna({"accident_count": 0})
    edge_counts["accident_count"] = edge_counts["accident_count"].astype(int)
    return edge_counts


def moran_summary(edge_counts: pd.DataFrame) -> dict[str, Any]:
    weights = libpysal.weights.fuzzy_contiguity(edge_counts[["geometry"]], buffering=True, silence_warnings=True)
    weights.transform = "R"
    values = edge_counts["accident_count"].to_numpy()
    moran = esda.Moran(values, weights, permutations=499)
    return {
        "moran_i": float(moran.I),
        "expected_i": float(moran.EI),
        "z_score": float(moran.z_norm),
        "p_value": float(moran.p_norm),
        "permutation_p_value": float(moran.p_sim),
    }


def plot_accident_map(edges_bng: gpd.GeoDataFrame, accidents_bng: gpd.GeoDataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    edges_bng.plot(ax=ax, linewidth=0.7, color="#33415c", alpha=0.75)
    accidents_bng.plot(ax=ax, markersize=8, color="#d62828", alpha=0.35)
    ax.set_title("Accidents snapped within selected 1 km^2 Leeds network")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "accidents_on_network.png", dpi=220)
    plt.close(fig)


def intersection_distance_summary(
    accidents_bng: gpd.GeoDataFrame,
    graph: nx.MultiDiGraph,
    edges_bng: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    edge_lookup = edges_bng.set_index(["u", "v", "key"])
    rows = []
    for idx, row in accidents_bng.iterrows():
        u, v, key = ox.distance.nearest_edges(graph, row["lon"], row["lat"], return_dist=False)
        edge_row = edge_lookup.loc[(u, v, key)]
        if isinstance(edge_row, pd.DataFrame):
            edge_row = edge_row.iloc[0]

        edge_geom = edge_row["geometry"]
        length = float(edge_geom.length)
        projected_distance = float(edge_geom.project(row.geometry))
        distance_to_u = projected_distance
        distance_to_v = max(length - projected_distance, 0.0)
        nearest_node_distance = min(distance_to_u, distance_to_v)
        fraction = nearest_node_distance / length if length > 0 else 0.0
        rows.append(
            {
                "accident_row": idx,
                "u": u,
                "v": v,
                "key": key,
                "edge_length_m": length,
                "distance_to_u_m": distance_to_u,
                "distance_to_v_m": distance_to_v,
                "nearest_intersection_distance_m": nearest_node_distance,
                "edge_fraction_to_nearest_intersection": fraction,
            }
        )
    df = pd.DataFrame(rows)
    summary = {
        "mean_distance_m": float(df["nearest_intersection_distance_m"].mean()),
        "median_distance_m": float(df["nearest_intersection_distance_m"].median()),
        "p90_distance_m": float(df["nearest_intersection_distance_m"].quantile(0.9)),
        "mean_edge_fraction": float(df["edge_fraction_to_nearest_intersection"].mean()),
        "median_edge_fraction": float(df["edge_fraction_to_nearest_intersection"].median()),
    }
    return df, summary


def plot_intersection_distance_hist(distance_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(distance_df["edge_fraction_to_nearest_intersection"], bins=20, color="#457b9d", alpha=0.85)
    ax.set_title("Accident position along edge relative to nearest intersection")
    ax.set_xlabel("Fraction of edge length to nearest intersection")
    ax.set_ylabel("Accident count")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "distance_to_intersection_hist.png", dpi=220)
    plt.close(fig)


def write_markdown(
    accident_summary: dict[str, Any],
    k_summary: dict[str, Any],
    moran: dict[str, Any],
    intersection_summary: dict[str, Any],
) -> None:
    lines = [
        "# Part 2 Task B Summary",
        "",
        "## Accident subset",
        "",
        pd.DataFrame([accident_summary]).to_markdown(index=False),
        "",
        "## Network K-function",
        "",
        pd.DataFrame([{
            "observed_exceeds_upper_steps": k_summary["observed_exceeds_upper_steps"],
            "max_gap_over_upper": k_summary["max_gap_over_upper"],
        }]).to_markdown(index=False),
        "",
        "## Moran's I",
        "",
        pd.DataFrame([moran]).to_markdown(index=False),
        "",
        "## Distance from intersections",
        "",
        pd.DataFrame([intersection_summary]).to_markdown(index=False),
        "",
        "## Output artifacts",
        "",
        "- `figures/accidents_on_network.png`",
        "- `figures/network_k_function.png`",
        "- `figures/distance_to_intersection_hist.png`",
    ]
    (OUTPUT_DIR / "part2_taskB_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    square = load_selected_square()
    graph = load_road_network()
    accidents_bng = load_square_accidents(square)
    edges_bng = road_edges_gdf(graph)

    ntw = build_spaghetti_network(edges_bng)
    snap_to_network(ntw, accidents_bng)
    k_summary = network_k_summary(ntw)
    plot_network_k(k_summary)

    edge_counts = assign_accidents_to_edges(accidents_bng, graph, edges_bng)
    moran = moran_summary(edge_counts)

    distance_df, intersection_summary = intersection_distance_summary(accidents_bng, graph, edges_bng)
    plot_intersection_distance_hist(distance_df)
    plot_accident_map(edges_bng, accidents_bng)

    accident_summary = {
        "accidents_in_square": int(len(accidents_bng)),
        "years_covered": "2009-2016",
        "unique_edges_with_accidents": int((edge_counts["accident_count"] > 0).sum()),
        "max_accidents_on_single_edge": int(edge_counts["accident_count"].max()),
        "mean_accidents_per_edge": float(edge_counts["accident_count"].mean()),
    }

    edge_counts.drop(columns=["geometry"]).to_csv(TABLE_DIR / "edge_accident_counts.csv", index=False)
    distance_df.to_csv(TABLE_DIR / "distance_to_intersection.csv", index=False)
    pd.DataFrame({"support": k_summary["support"], "observed": k_summary["observed"], "upper_envelope": k_summary["upper_envelope"], "lower_envelope": k_summary["lower_envelope"]}).to_csv(
        TABLE_DIR / "network_k_function.csv",
        index=False,
    )
    pd.DataFrame([moran]).to_csv(TABLE_DIR / "moran_summary.csv", index=False)
    pd.DataFrame([intersection_summary]).to_csv(TABLE_DIR / "intersection_distance_summary.csv", index=False)
    pd.DataFrame([accident_summary]).to_csv(TABLE_DIR / "accident_subset_summary.csv", index=False)

    summary = {
        "accident_summary": accident_summary,
        "network_k_summary": {
            "observed_exceeds_upper_steps": k_summary["observed_exceeds_upper_steps"],
            "max_gap_over_upper": k_summary["max_gap_over_upper"],
        },
        "moran_summary": moran,
        "intersection_distance_summary": intersection_summary,
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(accident_summary, k_summary, moran, intersection_summary)

    print(
        f"Accidents in square={accident_summary['accidents_in_square']}, "
        f"edges_with_accidents={accident_summary['unique_edges_with_accidents']}, "
        f"Moran_I={moran['moran_i']:.4f}, K_exceed_steps={k_summary['observed_exceeds_upper_steps']}"
    )


if __name__ == "__main__":
    main()
