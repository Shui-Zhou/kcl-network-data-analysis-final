#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import os
import pickle
from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import pandas as pd
from pyproj import Transformer


INPUT_TASK_A = PROJECT_ROOT / "Analysis" / "outputs" / "part2_taskA" / "summary.json"
OUTPUT_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part2_taskC"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
GRAPH_DIR = OUTPUT_DIR / "graphs"

CITY_GRAPH_PICKLE = GRAPH_DIR / "leeds_city_drive_multidigraph.pickle"
CITY_SIMPLE_PICKLE = GRAPH_DIR / "leeds_city_drive_simple_graph.pickle"
TARGET_MARATHON_M = 42_195.0
TARGET_TOLERANCE = 0.05
SEED_COLORS = ["#d62828", "#1d3557", "#2a9d8f", "#f4a261"]


@dataclass(frozen=True)
class SeedNode:
    rank: int
    node_id: int
    label: str
    x: float
    y: float
    street_count: int
    distance_to_hotspot_m: float
    quadrant: str


def ensure_dirs() -> None:
    for path in [OUTPUT_DIR, TABLE_DIR, FIGURE_DIR, GRAPH_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_hotspot_center_bng() -> tuple[float, float]:
    summary = json.loads(INPUT_TASK_A.read_text())
    square = summary["selected_square"]
    return float(square["center_x"]), float(square["center_y"])


def save_pickle(obj: object, path: Path) -> None:
    with path.open("wb") as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_or_download_city_graph() -> nx.MultiDiGraph:
    if CITY_GRAPH_PICKLE.exists():
        with CITY_GRAPH_PICKLE.open("rb") as handle:
            return pickle.load(handle)

    ox.settings.use_cache = True
    ox.settings.log_console = False
    graph = ox.graph_from_place("Leeds, West Yorkshire, England, United Kingdom", network_type="drive", simplify=True, retain_all=False)
    save_pickle(graph, CITY_GRAPH_PICKLE)
    return graph


def simplify_to_undirected_minlength(graph: nx.MultiDiGraph) -> nx.Graph:
    if CITY_SIMPLE_PICKLE.exists():
        with CITY_SIMPLE_PICKLE.open("rb") as handle:
            return pickle.load(handle)

    undirected = ox.convert.to_undirected(graph)
    simple = nx.Graph()
    simple.graph.update(graph.graph)
    for node, attrs in undirected.nodes(data=True):
        simple.add_node(node, **attrs)
    for u, v, attrs in undirected.edges(data=True):
        length = float(attrs.get("length", 1.0))
        geometry = attrs.get("geometry")
        if simple.has_edge(u, v):
            if length < float(simple[u][v]["length"]):
                simple[u][v].update(length=length, geometry=geometry)
        else:
            simple.add_edge(u, v, length=length, geometry=geometry)
    save_pickle(simple, CITY_SIMPLE_PICKLE)
    return simple


def project_hotspot(center_x: float, center_y: float) -> tuple[float, float]:
    return center_x, center_y


def quadrant_label(x: float, y: float, centroid_x: float, centroid_y: float) -> str:
    if x <= centroid_x and y >= centroid_y:
        return "north_west"
    if x > centroid_x and y >= centroid_y:
        return "north_east"
    if x <= centroid_x and y < centroid_y:
        return "south_west"
    return "south_east"


def select_seed_nodes(graph: nx.Graph, hotspot_x: float, hotspot_y: float) -> list[SeedNode]:
    nodes = pd.DataFrame(
        [
            {
                "node_id": node,
                "x": attrs["x"],
                "y": attrs["y"],
                "street_count": int(attrs.get("street_count") or graph.degree(node)),
                "degree": graph.degree(node),
            }
            for node, attrs in graph.nodes(data=True)
        ]
    )
    centroid_x = float(nodes["x"].mean())
    centroid_y = float(nodes["y"].mean())
    nodes["distance_to_hotspot_m"] = ((nodes["x"] - hotspot_x) ** 2 + (nodes["y"] - hotspot_y) ** 2) ** 0.5
    nodes["distance_to_center_m"] = ((nodes["x"] - centroid_x) ** 2 + (nodes["y"] - centroid_y) ** 2) ** 0.5
    nodes["quadrant"] = nodes.apply(lambda row: quadrant_label(row["x"], row["y"], centroid_x, centroid_y), axis=1)

    candidates = nodes[(nodes["street_count"] >= 3) & (nodes["distance_to_hotspot_m"] >= 2500)].copy()
    if candidates.empty:
        candidates = nodes[nodes["street_count"] >= 3].copy()

    candidates["score"] = (
        candidates["distance_to_hotspot_m"].rank(pct=True) * 0.55
        + candidates["street_count"].rank(pct=True) * 0.30
        + candidates["distance_to_center_m"].rank(pct=True) * 0.15
    )

    chosen_rows = []
    seen_nodes: set[int] = set()
    quadrant_order = ["north_west", "north_east", "south_west", "south_east"]
    for quadrant in quadrant_order:
        subset = candidates[candidates["quadrant"] == quadrant].sort_values(["score", "distance_to_hotspot_m"], ascending=[False, False])
        if subset.empty:
            subset = candidates.sort_values(["score", "distance_to_hotspot_m"], ascending=[False, False])
        selected = subset[~subset["node_id"].isin(seen_nodes)].iloc[0]
        seen_nodes.add(int(selected["node_id"]))
        chosen_rows.append(selected)

    seeds: list[SeedNode] = []
    for rank, row in enumerate(chosen_rows, start=1):
        seeds.append(
            SeedNode(
                rank=rank,
                node_id=int(row["node_id"]),
                label=f"Seed_{rank}",
                x=float(row["x"]),
                y=float(row["y"]),
                street_count=int(row["street_count"]),
                distance_to_hotspot_m=float(row["distance_to_hotspot_m"]),
                quadrant=str(row["quadrant"]),
            )
        )
    return seeds


def shortest_lengths_from_seeds(graph: nx.Graph, seeds: list[SeedNode]) -> dict[int, dict[int, float]]:
    return {seed.node_id: nx.single_source_dijkstra_path_length(graph, seed.node_id, weight="length") for seed in seeds}


def build_node_assignments(
    graph: nx.Graph,
    seeds: list[SeedNode],
    seed_lengths: dict[int, dict[int, float]],
) -> pd.DataFrame:
    rows = []
    for node, attrs in graph.nodes(data=True):
        planar_owner = min(seeds, key=lambda seed: math.dist((attrs["x"], attrs["y"]), (seed.x, seed.y)))
        network_owner = min(seeds, key=lambda seed: seed_lengths[seed.node_id].get(node, float("inf")))
        rows.append(
            {
                "node_id": node,
                "x": attrs["x"],
                "y": attrs["y"],
                "planar_owner": planar_owner.label,
                "node_network_owner": network_owner.label,
                "street_count": int(attrs.get("street_count") or graph.degree(node)),
            }
        )
    return pd.DataFrame(rows)


def build_edge_assignments(
    graph: nx.Graph,
    seeds: list[SeedNode],
    seed_lengths: dict[int, dict[int, float]],
    node_assignments: pd.DataFrame,
) -> pd.DataFrame:
    node_owner_map = dict(zip(node_assignments["node_id"], node_assignments["node_network_owner"]))
    rows = []
    for u, v, attrs in graph.edges(data=True):
        length = float(attrs.get("length", 0.0))
        midpoint_scores = {
            seed.label: min(seed_lengths[seed.node_id].get(u, float("inf")), seed_lengths[seed.node_id].get(v, float("inf"))) + length / 2.0
            for seed in seeds
        }
        edge_point_owner = min(midpoint_scores, key=midpoint_scores.get)
        same_node_owner = node_owner_map[u] == node_owner_map[v]
        rows.append(
            {
                "u": u,
                "v": v,
                "length_m": length,
                "node_owner_u": node_owner_map[u],
                "node_owner_v": node_owner_map[v],
                "node_network_owner": node_owner_map[u] if same_node_owner else "boundary",
                "edge_point_owner": edge_point_owner,
                "is_boundary_edge": not same_node_owner,
            }
        )
    return pd.DataFrame(rows)


def cell_subgraph(graph: nx.Graph, seed_label: str, edge_assignments: pd.DataFrame, seeds: list[SeedNode]) -> nx.Graph:
    seed_id = next(seed.node_id for seed in seeds if seed.label == seed_label)
    selected_edges = edge_assignments[edge_assignments["edge_point_owner"] == seed_label][["u", "v"]]
    subgraph = nx.Graph()
    for _, row in selected_edges.iterrows():
        u = int(row["u"])
        v = int(row["v"])
        if graph.has_edge(u, v):
            subgraph.add_edge(u, v, **graph[u][v])
    if seed_id not in subgraph:
        return nx.Graph()
    component = nx.node_connected_component(subgraph, seed_id)
    return subgraph.subgraph(component).copy()


def relaxed_cell_subgraph(
    graph: nx.Graph,
    seed_label: str,
    edge_assignments: pd.DataFrame,
    seeds: list[SeedNode],
    expansion_rounds: int = 1,
) -> nx.Graph:
    base = cell_subgraph(graph, seed_label, edge_assignments, seeds)
    seed_id = next(seed.node_id for seed in seeds if seed.label == seed_label)
    if base.number_of_nodes() == 0 or seed_id not in base:
        return base

    expanded_nodes = set(base.nodes())
    frontier = set(base.nodes())
    for _ in range(expansion_rounds):
        new_nodes = set()
        for node in frontier:
            new_nodes.update(graph.neighbors(node))
        new_nodes -= expanded_nodes
        expanded_nodes.update(new_nodes)
        frontier = new_nodes
        if not frontier:
            break

    subgraph = graph.subgraph(expanded_nodes).copy()
    component = nx.node_connected_component(subgraph, seed_id)
    return subgraph.subgraph(component).copy()


def select_loop_targets(subgraph: nx.Graph, seed_id: int) -> list[tuple[int, float]]:
    distances = nx.single_source_dijkstra_path_length(subgraph, seed_id, weight="length")
    candidates = [(node, dist) for node, dist in distances.items() if node != seed_id and dist >= 1500]
    candidates.sort(key=lambda item: item[1], reverse=True)
    if len(candidates) > 80:
        stride = max(1, len(candidates) // 80)
        candidates = candidates[::stride][:80]
    return candidates


def assemble_route_from_loops(subgraph: nx.Graph, seed_id: int, targets: list[int]) -> tuple[list[int], float]:
    route_nodes = [seed_id]
    total_length = 0.0
    current = seed_id
    for target in targets:
        outward = nx.shortest_path(subgraph, current, target, weight="length")
        outward_len = nx.path_weight(subgraph, outward, "length")
        route_nodes.extend(outward[1:])
        total_length += outward_len

        back = nx.shortest_path(subgraph, target, seed_id, weight="length")
        back_len = nx.path_weight(subgraph, back, "length")
        route_nodes.extend(back[1:])
        total_length += back_len
        current = seed_id
    return route_nodes, total_length


def find_marathon_route(subgraph: nx.Graph, seed: SeedNode) -> dict[str, object]:
    if subgraph.number_of_nodes() < 20 or subgraph.number_of_edges() < 20:
        return {"seed_label": seed.label, "status": "fail", "reason": "cell_too_small"}

    targets = select_loop_targets(subgraph, seed.node_id)
    if not targets:
        return {"seed_label": seed.label, "status": "fail", "reason": "no_viable_targets"}

    candidate_loops = [(node, 2 * dist) for node, dist in targets]
    if len(candidate_loops) > 26:
        candidate_loops = candidate_loops[:18] + candidate_loops[len(candidate_loops) // 2 : len(candidate_loops) // 2 + 8]

    best_combo: tuple[int, ...] | None = None
    best_total = None
    best_gap = float("inf")

    for loop_count in range(1, 5):
        for combo in combinations_with_replacement(range(len(candidate_loops)), loop_count):
            counts = Counter(combo)
            if any(count > 2 for count in counts.values()):
                continue
            total = sum(candidate_loops[index][1] for index in combo)
            gap = abs(total - TARGET_MARATHON_M)
            if gap < best_gap or (
                math.isclose(gap, best_gap) and best_total is not None and abs(total - TARGET_MARATHON_M) < abs(best_total - TARGET_MARATHON_M)
            ):
                best_gap = gap
                best_total = total
                best_combo = combo
            if gap <= TARGET_MARATHON_M * TARGET_TOLERANCE:
                break
        if best_gap <= TARGET_MARATHON_M * TARGET_TOLERANCE:
            break

    selected_targets = [candidate_loops[index][0] for index in best_combo] if best_combo is not None else []

    route_nodes, route_length = assemble_route_from_loops(subgraph, seed.node_id, selected_targets)
    status = "success" if abs(route_length - TARGET_MARATHON_M) <= TARGET_MARATHON_M * TARGET_TOLERANCE else "approximate"
    return {
        "seed_label": seed.label,
        "seed_node_id": seed.node_id,
        "status": status,
        "route_length_m": route_length,
        "target_gap_m": route_length - TARGET_MARATHON_M,
        "loop_count": len(selected_targets),
        "route_nodes": route_nodes,
        "target_nodes": selected_targets,
        "cell_nodes": subgraph.number_of_nodes(),
        "cell_edges": subgraph.number_of_edges(),
    }


def build_route_edges(route_nodes: list[int]) -> set[tuple[int, int]]:
    return {tuple(sorted((route_nodes[i], route_nodes[i + 1]))) for i in range(len(route_nodes) - 1)}


def plot_voronoi_map(
    graph: nx.Graph,
    seeds: list[SeedNode],
    edge_assignments: pd.DataFrame,
    route_results: list[dict[str, object]],
    output_name: str = "leeds_voronoi_marathon_map.png",
    title: str = "Leeds city network Voronoi cells and marathon routes",
) -> None:
    pos = {node: (attrs["x"], attrs["y"]) for node, attrs in graph.nodes(data=True)}
    edge_color_map = {}
    for seed, color in zip(seeds, SEED_COLORS):
        edge_color_map[seed.label] = color
    edge_color_map["boundary"] = "#bdbdbd"

    route_edge_sets = {}
    for route in route_results:
        if route.get("route_nodes"):
            route_edge_sets[route["seed_label"]] = build_route_edges(route["route_nodes"])

    fig, ax = plt.subplots(figsize=(10, 10))
    for _, edge in edge_assignments.iterrows():
        u = int(edge["u"])
        v = int(edge["v"])
        owner = edge["edge_point_owner"]
        color = edge_color_map.get(owner, "#cccccc")
        linewidth = 0.35
        edge_key = tuple(sorted((u, v)))
        for route in route_results:
            if route.get("seed_label") in route_edge_sets and edge_key in route_edge_sets[route["seed_label"]]:
                color = edge_color_map[route["seed_label"]]
                linewidth = 1.8
                break
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        ax.plot([x0, x1], [y0, y1], color=color, linewidth=linewidth, alpha=0.75 if linewidth > 1 else 0.25)

    for seed, color in zip(seeds, SEED_COLORS):
        ax.scatter(seed.x, seed.y, s=80, color=color, edgecolor="white", linewidth=0.9, zorder=5)
        ax.text(seed.x, seed.y, seed.label, fontsize=9, ha="left", va="bottom", color=color)

    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / output_name, dpi=220)
    plt.close(fig)


def write_summary(
    seeds_df: pd.DataFrame,
    node_assignments: pd.DataFrame,
    edge_assignments: pd.DataFrame,
    route_df: pd.DataFrame,
    refined_route_df: pd.DataFrame | None = None,
) -> None:
    planar_counts = node_assignments["planar_owner"].value_counts().rename_axis("owner").reset_index(name="node_count")
    network_counts = node_assignments["node_network_owner"].value_counts().rename_axis("owner").reset_index(name="node_count")
    edge_counts = edge_assignments["edge_point_owner"].value_counts().rename_axis("owner").reset_index(name="edge_count")

    planar_counts.to_csv(TABLE_DIR / "planar_voronoi_node_counts.csv", index=False)
    network_counts.to_csv(TABLE_DIR / "node_network_voronoi_counts.csv", index=False)
    edge_counts.to_csv(TABLE_DIR / "edge_point_voronoi_counts.csv", index=False)

    lines = [
        "# Part 2 Task C Summary",
        "",
        "## Seed Points",
        "",
        seeds_df.to_markdown(index=False),
        "",
        "## Voronoi Strategy Counts",
        "",
        "### Planar nearest-seed node counts",
        "",
        planar_counts.to_markdown(index=False),
        "",
        "### Node-network nearest-seed node counts",
        "",
        network_counts.to_markdown(index=False),
        "",
        "### Edge-point (midpoint network-distance approximation) edge counts",
        "",
        edge_counts.to_markdown(index=False),
        "",
        "## Marathon Route Attempts",
        "",
        route_df.drop(columns=["route_nodes", "target_nodes"], errors="ignore").to_markdown(index=False),
        "",
    ]
    if refined_route_df is not None:
        lines.extend(
            [
                "## Step 5 Rerun: Slight Boundary Relaxation",
                "",
                "Chosen option: allow routes to cross cell boundaries slightly by expanding each edge-point "
                "cell to include one graph-neighbourhood hop beyond its original nodes, then repeat the route search.",
                "",
                refined_route_df.drop(columns=["route_nodes", "target_nodes"], errors="ignore").to_markdown(index=False),
                "",
            ]
        )

    lines.extend(
        [
        "## Output artifacts",
        "",
        "- `figures/leeds_voronoi_marathon_map.png`",
        "- `figures/leeds_voronoi_marathon_refined_map.png`",
        "- `tables/seed_nodes.csv`",
        "- `tables/marathon_routes.csv`",
        "- `tables/marathon_routes_refined.csv`",
    ]
    )
    (OUTPUT_DIR / "part2_taskC_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    hotspot_x, hotspot_y = load_hotspot_center_bng()
    city_graph = load_or_download_city_graph()
    projected_graph = ox.project_graph(city_graph, to_crs="EPSG:27700")
    simple_graph = simplify_to_undirected_minlength(projected_graph)

    seeds = select_seed_nodes(simple_graph, hotspot_x, hotspot_y)
    seed_lengths = shortest_lengths_from_seeds(simple_graph, seeds)
    node_assignments = build_node_assignments(simple_graph, seeds, seed_lengths)
    edge_assignments = build_edge_assignments(simple_graph, seeds, seed_lengths, node_assignments)

    route_results = []
    for seed in seeds:
        subgraph = cell_subgraph(simple_graph, seed.label, edge_assignments, seeds)
        route = find_marathon_route(subgraph, seed)
        route_results.append(route)

    refined_route_results = []
    for seed in seeds:
        relaxed_subgraph = relaxed_cell_subgraph(simple_graph, seed.label, edge_assignments, seeds, expansion_rounds=1)
        route = find_marathon_route(relaxed_subgraph, seed)
        route["rerun_option"] = "allow_slight_boundary_crossing"
        refined_route_results.append(route)

    seeds_df = pd.DataFrame([seed.__dict__ for seed in seeds])
    route_df = pd.DataFrame(route_results)
    refined_route_df = pd.DataFrame(refined_route_results)
    seeds_df.to_csv(TABLE_DIR / "seed_nodes.csv", index=False)
    node_assignments.to_csv(TABLE_DIR / "node_assignments.csv", index=False)
    edge_assignments.to_csv(TABLE_DIR / "edge_assignments.csv", index=False)
    route_df.to_csv(TABLE_DIR / "marathon_routes.csv", index=False)
    refined_route_df.to_csv(TABLE_DIR / "marathon_routes_refined.csv", index=False)

    summary = {
        "seeds": seeds_df.to_dict(orient="records"),
        "routes": route_df.drop(columns=["route_nodes", "target_nodes"], errors="ignore").to_dict(orient="records"),
        "refined_routes": refined_route_df.drop(columns=["route_nodes", "target_nodes"], errors="ignore").to_dict(orient="records"),
        "city_graph_nodes": int(simple_graph.number_of_nodes()),
        "city_graph_edges": int(simple_graph.number_of_edges()),
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    plot_voronoi_map(simple_graph, seeds, edge_assignments, route_results)
    plot_voronoi_map(
        simple_graph,
        seeds,
        edge_assignments,
        refined_route_results,
        output_name="leeds_voronoi_marathon_refined_map.png",
        title="Leeds city network Voronoi cells and marathon routes (rerun)",
    )
    write_summary(seeds_df, node_assignments, edge_assignments, route_df, refined_route_df=refined_route_df)

    for route in route_results:
        print(
            f"[{route['seed_label']}] status={route['status']} "
            f"length={route.get('route_length_m', float('nan')):.1f}m "
            f"gap={route.get('target_gap_m', float('nan')):.1f}m"
        )
    for route in refined_route_results:
        print(
            f"[rerun {route['seed_label']}] status={route['status']} "
            f"length={route.get('route_length_m', float('nan')):.1f}m "
            f"gap={route.get('target_gap_m', float('nan')):.1f}m"
        )


if __name__ == "__main__":
    main()
