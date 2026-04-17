#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import os
import pickle
import random
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


INPUT_GRAPH_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part1_taskA" / "graphs"
OUTPUT_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part1_taskB"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"

RANDOM_SEEDS = [42, 314, 2718]


@dataclass(frozen=True)
class DistanceMetricResult:
    value: float
    method: str
    sample_size: int | None = None


def ensure_output_dirs() -> None:
    for path in [OUTPUT_DIR, TABLE_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)


def load_graphs() -> list[nx.Graph]:
    graphs: list[nx.Graph] = []
    for path in sorted(INPUT_GRAPH_DIR.glob("*.pickle")):
        with path.open("rb") as handle:
            graphs.append(pickle.load(handle))
    if not graphs:
        raise SystemExit("No graph pickle files found. Re-run Task A with --save-graphs.")
    return graphs


def largest_component_subgraph(graph: nx.Graph) -> nx.Graph:
    if graph.number_of_nodes() == 0:
        return graph.copy()
    largest_component = max(nx.connected_components(graph), key=len)
    return graph.subgraph(largest_component).copy()


def approximate_average_shortest_path_length(graph: nx.Graph, sample_size: int, seed: int) -> DistanceMetricResult:
    rng = random.Random(seed)
    nodes = list(graph.nodes())
    chosen = nodes if len(nodes) <= sample_size else rng.sample(nodes, sample_size)
    path_sum = 0
    path_count = 0
    for source in chosen:
        lengths = nx.single_source_shortest_path_length(graph, source)
        path_sum += sum(lengths.values())
        path_count += len(lengths) - 1
    value = path_sum / path_count if path_count else 0.0
    return DistanceMetricResult(value=value, method="sampled_bfs", sample_size=len(chosen))


def distance_metrics(graph: nx.Graph, seed: int) -> tuple[DistanceMetricResult, DistanceMetricResult]:
    node_count = graph.number_of_nodes()
    if node_count <= 4000:
        avg_path = nx.average_shortest_path_length(graph) if node_count > 1 else 0.0
        diameter = nx.diameter(graph) if node_count > 1 else 0
        return (
            DistanceMetricResult(value=float(avg_path), method="exact"),
            DistanceMetricResult(value=float(diameter), method="exact"),
        )

    avg_path_result = approximate_average_shortest_path_length(graph, sample_size=min(256, node_count), seed=seed)
    approx_diameter = nx.approximation.diameter(graph)
    return (
        avg_path_result,
        DistanceMetricResult(value=float(approx_diameter), method="approximation"),
    )


def betweenness_with_method(graph: nx.Graph, seed: int) -> tuple[dict[str, float], str]:
    node_count = graph.number_of_nodes()
    if node_count <= 1200:
        return nx.betweenness_centrality(graph, normalized=True), "exact"

    sample_size = min(256, max(64, math.ceil(node_count * 0.08)))
    return (
        nx.betweenness_centrality(graph, k=sample_size, normalized=True, seed=seed),
        f"sampled_k_{sample_size}",
    )


def top_centrality_rows(
    dataset: str,
    centrality: dict[str, float],
    metric_name: str,
    top_n: int = 10,
) -> list[dict[str, object]]:
    return [
        {"dataset": dataset, "metric": metric_name, "rank": rank, "username": username, "value": value}
        for rank, (username, value) in enumerate(
            sorted(centrality.items(), key=lambda item: item[1], reverse=True)[:top_n],
            start=1,
        )
    ]


def degree_ccdf(graph: nx.Graph) -> tuple[list[int], list[float]]:
    degrees = sorted(degree for _, degree in graph.degree() if degree > 0)
    if not degrees:
        return [], []
    n = len(degrees)
    x_values = sorted(set(degrees))
    y_values = [sum(1 for degree in degrees if degree >= x) / n for x in x_values]
    return x_values, y_values


def plot_degree_ccdf(dataset: str, graph: nx.Graph, random_graph: nx.Graph) -> None:
    x_real, y_real = degree_ccdf(graph)
    x_rand, y_rand = degree_ccdf(random_graph)
    if not x_real or not x_rand:
        return

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(x_real, y_real, marker="o", linestyle="-", linewidth=1.4, markersize=4, label="Observed")
    ax.plot(x_rand, y_rand, marker="s", linestyle="--", linewidth=1.2, markersize=4, label="Random baseline")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Degree >= k")
    ax.set_ylabel("CCDF")
    ax.set_title(f"{dataset}: degree CCDF vs random baseline")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / f"{dataset}_degree_ccdf_vs_random.png", dpi=220)
    plt.close(fig)


def component_rows(dataset: str, graph: nx.Graph, top_n: int = 10) -> list[dict[str, object]]:
    sizes = sorted((len(component) for component in nx.connected_components(graph)), reverse=True)
    return [
        {"dataset": dataset, "component_rank": rank, "component_size": size}
        for rank, size in enumerate(sizes[:top_n], start=1)
    ]


def summarize_graph(
    graph: nx.Graph,
    seed: int,
    label: str,
    baseline_type: str,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]], nx.Graph]:
    largest_component = largest_component_subgraph(graph)
    average_path_result, diameter_result = distance_metrics(largest_component, seed=seed)
    average_clustering = nx.average_clustering(graph)
    transitivity = nx.transitivity(graph)
    degree_centrality = nx.degree_centrality(graph)
    betweenness_centrality, betweenness_method = betweenness_with_method(graph, seed=seed)

    top_rows = []
    top_rows.extend(top_centrality_rows(label, degree_centrality, "degree_centrality"))
    top_rows.extend(top_centrality_rows(label, betweenness_centrality, "betweenness_centrality"))

    random_graph = nx.gnm_random_graph(graph.number_of_nodes(), graph.number_of_edges(), seed=seed)
    random_lcc = largest_component_subgraph(random_graph)
    random_average_path_result, random_diameter_result = distance_metrics(random_lcc, seed=seed)

    summary = {
        "dataset": label,
        "baseline_type": baseline_type,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": nx.density(graph),
        "average_clustering": average_clustering,
        "transitivity": transitivity,
        "connected_components": nx.number_connected_components(graph),
        "largest_component_size": largest_component.number_of_nodes(),
        "largest_component_share": largest_component.number_of_nodes() / graph.number_of_nodes(),
        "average_path_length_lcc": average_path_result.value,
        "average_path_length_method": average_path_result.method,
        "diameter_lcc": diameter_result.value,
        "diameter_method": diameter_result.method,
        "mean_degree_centrality": sum(degree_centrality.values()) / len(degree_centrality),
        "max_degree_centrality": max(degree_centrality.values(), default=0.0),
        "mean_betweenness_centrality": sum(betweenness_centrality.values()) / len(betweenness_centrality),
        "max_betweenness_centrality": max(betweenness_centrality.values(), default=0.0),
        "betweenness_method": betweenness_method,
        "random_seed": seed,
        "random_density": nx.density(random_graph),
        "random_average_clustering": nx.average_clustering(random_graph),
        "random_transitivity": nx.transitivity(random_graph),
        "random_connected_components": nx.number_connected_components(random_graph),
        "random_largest_component_size": random_lcc.number_of_nodes(),
        "random_average_path_length_lcc": random_average_path_result.value,
        "random_average_path_length_method": random_average_path_result.method,
        "random_diameter_lcc": random_diameter_result.value,
        "random_diameter_method": random_diameter_result.method,
        "clustering_ratio_vs_random": average_clustering / nx.average_clustering(random_graph)
        if nx.average_clustering(random_graph) > 0
        else float("nan"),
        "path_ratio_vs_random": average_path_result.value / random_average_path_result.value
        if random_average_path_result.value > 0
        else float("nan"),
        "small_world_sigma": (
            (average_clustering / nx.average_clustering(random_graph))
            / (average_path_result.value / random_average_path_result.value)
        )
        if nx.average_clustering(random_graph) > 0 and random_average_path_result.value > 0
        else float("nan"),
    }
    return summary, top_rows, component_rows(label, graph), random_graph


def aggregate_baselines(records: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    group_cols = ["dataset"]
    numeric_cols = [
        "random_density",
        "random_average_clustering",
        "random_transitivity",
        "random_connected_components",
        "random_largest_component_size",
        "random_average_path_length_lcc",
        "random_diameter_lcc",
        "clustering_ratio_vs_random",
        "path_ratio_vs_random",
        "small_world_sigma",
    ]
    aggregated = df[group_cols + numeric_cols].groupby(group_cols, as_index=False).mean()
    aggregated = aggregated.rename(
        columns={
            "random_density": "random_density_mean",
            "random_average_clustering": "random_average_clustering_mean",
            "random_transitivity": "random_transitivity_mean",
            "random_connected_components": "random_connected_components_mean",
            "random_largest_component_size": "random_largest_component_size_mean",
            "random_average_path_length_lcc": "random_average_path_length_lcc_mean",
            "random_diameter_lcc": "random_diameter_lcc_mean",
            "clustering_ratio_vs_random": "clustering_ratio_vs_random_mean",
            "path_ratio_vs_random": "path_ratio_vs_random_mean",
            "small_world_sigma": "small_world_sigma_mean",
        }
    )
    return aggregated


def write_markdown(real_df: pd.DataFrame, baseline_df: pd.DataFrame) -> None:
    target = OUTPUT_DIR / "part1_taskB_summary.md"
    rounded_real = real_df.copy()
    rounded_baseline = baseline_df.copy()
    for frame in [rounded_real, rounded_baseline]:
        for column in frame.columns:
            if pd.api.types.is_float_dtype(frame[column]):
                frame[column] = frame[column].map(lambda value: f"{value:.4f}")
    with target.open("w", encoding="utf-8") as handle:
        handle.write("# Part 1 Task B Summary\n\n")
        handle.write("## Observed Graph Metrics\n\n")
        handle.write(rounded_real.to_markdown(index=False))
        handle.write("\n\n## Random Baseline Means\n\n")
        handle.write(rounded_baseline.to_markdown(index=False))
        handle.write("\n")


def main() -> None:
    ensure_output_dirs()
    graphs = load_graphs()

    metric_records: list[dict[str, object]] = []
    top_rows: list[dict[str, object]] = []
    component_size_rows: list[dict[str, object]] = []
    first_random_graphs: dict[str, nx.Graph] = {}

    for graph in graphs:
        dataset = graph.graph["dataset"]
        for index, seed in enumerate(RANDOM_SEEDS, start=1):
            summary, summary_top_rows, summary_components, random_graph = summarize_graph(
                graph=graph,
                seed=seed,
                label=dataset,
                baseline_type=f"gnm_random_graph_seed_{seed}",
            )
            summary["baseline_run"] = index
            metric_records.append(summary)
            if index == 1:
                top_rows.extend(summary_top_rows)
                component_size_rows.extend(summary_components)
                first_random_graphs[dataset] = random_graph
            print(
                f"[{dataset}] seed={seed} clustering={summary['average_clustering']:.4f} "
                f"path={summary['average_path_length_lcc']:.4f} sigma={summary['small_world_sigma']:.4f}"
            )

    metrics_df = pd.DataFrame(metric_records)
    observed_cols = [
        "dataset",
        "nodes",
        "edges",
        "density",
        "average_clustering",
        "transitivity",
        "connected_components",
        "largest_component_size",
        "largest_component_share",
        "average_path_length_lcc",
        "average_path_length_method",
        "diameter_lcc",
        "diameter_method",
        "mean_degree_centrality",
        "max_degree_centrality",
        "mean_betweenness_centrality",
        "max_betweenness_centrality",
        "betweenness_method",
    ]
    observed_df = metrics_df[observed_cols].drop_duplicates(subset=["dataset"]).sort_values("dataset")
    baseline_df = aggregate_baselines(metric_records).sort_values("dataset")
    merged_df = observed_df.merge(baseline_df, on="dataset", how="left")

    observed_df.to_csv(TABLE_DIR / "observed_metrics.csv", index=False)
    baseline_df.to_csv(TABLE_DIR / "random_baseline_means.csv", index=False)
    merged_df.to_csv(TABLE_DIR / "taskB_comparison_summary.csv", index=False)
    pd.DataFrame(top_rows).to_csv(TABLE_DIR / "top_centrality_nodes.csv", index=False)
    pd.DataFrame(component_size_rows).to_csv(TABLE_DIR / "component_sizes_top10.csv", index=False)
    metrics_df.to_csv(TABLE_DIR / "raw_metric_runs.csv", index=False)

    by_dataset = {graph.graph["dataset"]: graph for graph in graphs}
    for dataset, graph in by_dataset.items():
        plot_degree_ccdf(dataset, graph, first_random_graphs[dataset])

    metadata = {
        "random_seeds": RANDOM_SEEDS,
        "graph_input_dir": str(INPUT_GRAPH_DIR.relative_to(PROJECT_ROOT)),
        "outputs": {
            "observed_metrics": str((TABLE_DIR / "observed_metrics.csv").relative_to(PROJECT_ROOT)),
            "random_baseline_means": str((TABLE_DIR / "random_baseline_means.csv").relative_to(PROJECT_ROOT)),
            "taskB_comparison_summary": str((TABLE_DIR / "taskB_comparison_summary.csv").relative_to(PROJECT_ROOT)),
            "top_centrality_nodes": str((TABLE_DIR / "top_centrality_nodes.csv").relative_to(PROJECT_ROOT)),
            "component_sizes_top10": str((TABLE_DIR / "component_sizes_top10.csv").relative_to(PROJECT_ROOT)),
        },
    }
    (OUTPUT_DIR / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_markdown(observed_df, baseline_df)


if __name__ == "__main__":
    main()
