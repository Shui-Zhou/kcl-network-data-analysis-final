#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import pickle
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


DATA_DIR = PROJECT_ROOT / "Assessment" / "Part1_Data" / "datasets"
OUTPUT_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part1_taskA"
FIGURE_DIR = OUTPUT_DIR / "figures"
TABLE_DIR = OUTPUT_DIR / "tables"
GRAPH_DIR = OUTPUT_DIR / "graphs"

SELECTED_DATASETS = {
    "large": "REQUEST_FOR_DELETION.csv",
    "medium": "PROPERTY_PROPOSAL.csv",
    "small": "BOT_REQUESTS.csv",
}

REQUIRED_COLUMNS = ["thread_subject", "username", "page_name"]


@dataclass(frozen=True)
class DatasetRun:
    size_label: str
    filename: str

    @property
    def stem(self) -> str:
        return Path(self.filename).stem

    @property
    def path(self) -> Path:
        return DATA_DIR / self.filename


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Part 1 Task A editor co-comment networks.")
    parser.add_argument(
        "--save-graphs",
        action="store_true",
        help="Serialize built networkx graphs to Analysis/outputs/part1_taskA/graphs.",
    )
    return parser.parse_args()


def ensure_output_dirs(save_graphs: bool) -> None:
    for path in [OUTPUT_DIR, FIGURE_DIR, TABLE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    if save_graphs:
        GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=REQUIRED_COLUMNS, dtype=str)
    for column in REQUIRED_COLUMNS:
        df[column] = df[column].str.strip()
    df = df.dropna(subset=REQUIRED_COLUMNS)
    df = df[(df["thread_subject"] != "") & (df["username"] != "") & (df["page_name"] != "")]
    df = df.drop_duplicates(subset=REQUIRED_COLUMNS).reset_index(drop=True)
    return df


def dataset_profile(df: pd.DataFrame, dataset: DatasetRun) -> dict[str, float | int | str]:
    group_sizes = df.groupby(["page_name", "thread_subject"])["username"].nunique()
    return {
        "dataset": dataset.stem,
        "size_label": dataset.size_label,
        "rows": int(len(df)),
        "unique_users": int(df["username"].nunique()),
        "unique_pages": int(df["page_name"].nunique()),
        "unique_threads": int(df["thread_subject"].nunique()),
        "unique_page_thread_groups": int(len(group_sizes)),
        "max_users_in_group": int(group_sizes.max()),
        "median_users_in_group": float(group_sizes.median()),
    }


def build_node_attributes(df: pd.DataFrame) -> dict[str, dict[str, object]]:
    node_attrs: dict[str, dict[str, object]] = {}
    grouped = df.groupby("username", sort=False)
    for username, group in grouped:
        pages = sorted(group["page_name"].unique().tolist())
        threads = sorted(group["thread_subject"].unique().tolist())
        node_attrs[username] = {
            "comment_count": int(len(group)),
            "pages": pages,
            "threads": threads,
            "page_count": int(len(pages)),
            "thread_count": int(len(threads)),
        }
    return node_attrs


def build_edge_attributes(
    df: pd.DataFrame,
) -> tuple[dict[tuple[str, str], int], dict[tuple[str, str], list[tuple[str, str]]]]:
    edge_weights: dict[tuple[str, str], int] = defaultdict(int)
    edge_contexts: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    grouped = df.groupby(["page_name", "thread_subject"], sort=False)["username"]

    for (page_name, thread_subject), users in grouped:
        participants = sorted(users.tolist())
        if len(participants) < 2:
            continue
        context = (page_name, thread_subject)
        for source, target in combinations(participants, 2):
            edge = (source, target)
            edge_weights[edge] += 1
            edge_contexts[edge].append(context)

    return dict(edge_weights), dict(edge_contexts)


def build_graph(df: pd.DataFrame, dataset: DatasetRun) -> tuple[nx.Graph, float]:
    start = time.perf_counter()
    graph = nx.Graph(dataset=dataset.stem, size_label=dataset.size_label)

    node_attrs = build_node_attributes(df)
    graph.add_nodes_from((node, attrs) for node, attrs in node_attrs.items())

    edge_weights, edge_contexts = build_edge_attributes(df)
    graph.add_edges_from(
        (
            source,
            target,
            {
                "weight": weight,
                "shared_context_count": int(weight),
                "shared_contexts": edge_contexts[(source, target)],
            },
        )
        for (source, target), weight in edge_weights.items()
    )
    runtime_seconds = time.perf_counter() - start
    return graph, runtime_seconds


def graph_summary(graph: nx.Graph, profile: dict[str, float | int | str], runtime_seconds: float) -> dict[str, float | int | str]:
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    degrees = [degree for _, degree in graph.degree()]
    components = list(nx.connected_components(graph))
    largest_component_size = max((len(component) for component in components), default=0)
    isolated_nodes = sum(1 for _, degree in graph.degree() if degree == 0)

    weights = [attrs["weight"] for _, _, attrs in graph.edges(data=True)]
    return {
        **profile,
        "nodes": int(node_count),
        "edges": int(edge_count),
        "density": float(nx.density(graph)),
        "average_degree": float(sum(degrees) / node_count) if node_count else 0.0,
        "median_degree": float(pd.Series(degrees).median()) if degrees else 0.0,
        "max_degree": int(max(degrees, default=0)),
        "connected_components": int(len(components)),
        "largest_component_size": int(largest_component_size),
        "largest_component_share": float(largest_component_size / node_count) if node_count else 0.0,
        "isolated_nodes": int(isolated_nodes),
        "mean_edge_weight": float(pd.Series(weights).mean()) if weights else 0.0,
        "max_edge_weight": int(max(weights, default=0)),
        "build_runtime_seconds": float(runtime_seconds),
    }


def save_graph(graph: nx.Graph, dataset: DatasetRun) -> None:
    target = GRAPH_DIR / f"{dataset.stem}.pickle"
    with target.open("wb") as handle:
        pickle.dump(graph, handle, protocol=pickle.HIGHEST_PROTOCOL)


def plot_degree_distribution(graph: nx.Graph, dataset: DatasetRun) -> None:
    degree_counts = Counter(dict(graph.degree()).values())
    items = sorted((degree, count) for degree, count in degree_counts.items() if degree > 0)
    if not items:
        return

    x_values = [degree for degree, _ in items]
    y_values = [count for _, count in items]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x_values, y_values, s=32, color="#1f4e79", alpha=0.85)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Degree")
    ax.set_ylabel("Number of nodes")
    ax.set_title(f"{dataset.stem}: degree distribution")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.4)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / f"{dataset.stem}_degree_distribution.png", dpi=220)
    plt.close(fig)


def plot_small_network(graph: nx.Graph, dataset: DatasetRun) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    layout = nx.spring_layout(graph, seed=42, k=0.22, iterations=150, weight="weight")
    degrees = dict(graph.degree())
    node_sizes = [18 + degrees[node] * 10 for node in graph.nodes()]
    edge_widths = [0.15 + attrs["weight"] * 0.12 for _, _, attrs in graph.edges(data=True)]

    nx.draw_networkx_edges(graph, pos=layout, ax=ax, alpha=0.18, width=edge_widths, edge_color="#6b7280")
    nx.draw_networkx_nodes(
        graph,
        pos=layout,
        ax=ax,
        node_size=node_sizes,
        node_color=list(degrees.values()),
        cmap="viridis",
        alpha=0.9,
        linewidths=0.0,
    )
    ax.set_title(f"{dataset.stem}: full editor co-comment network")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / f"{dataset.stem}_network.png", dpi=240)
    plt.close(fig)


def write_markdown_summary(summary_df: pd.DataFrame) -> None:
    target = OUTPUT_DIR / "part1_taskA_summary.md"
    rounded = summary_df.copy()
    for column in [
        "density",
        "average_degree",
        "median_degree",
        "largest_component_share",
        "mean_edge_weight",
        "build_runtime_seconds",
        "median_users_in_group",
    ]:
        rounded[column] = rounded[column].map(lambda value: f"{value:.4f}")

    with target.open("w", encoding="utf-8") as handle:
        handle.write("# Part 1 Task A Summary\n\n")
        handle.write("## Graph Summary\n\n")
        handle.write(rounded.to_markdown(index=False))
        handle.write("\n\n")
        handle.write("## Output Files\n\n")
        handle.write("- `tables/dataset_profiles.csv`\n")
        handle.write("- `tables/graph_summary.csv`\n")
        handle.write("- `figures/*_degree_distribution.png`\n")
        handle.write("- `figures/BOT_REQUESTS_network.png`\n")


def main() -> None:
    args = parse_args()
    ensure_output_dirs(save_graphs=args.save_graphs)

    profiles: list[dict[str, float | int | str]] = []
    summaries: list[dict[str, float | int | str]] = []

    for size_label, filename in SELECTED_DATASETS.items():
        dataset = DatasetRun(size_label=size_label, filename=filename)
        dataframe = load_dataset(dataset.path)
        profile = dataset_profile(dataframe, dataset)
        graph, runtime_seconds = build_graph(dataframe, dataset)
        summary = graph_summary(graph, profile, runtime_seconds)

        profiles.append(profile)
        summaries.append(summary)

        plot_degree_distribution(graph, dataset)
        if dataset.size_label == "small":
            plot_small_network(graph, dataset)
        if args.save_graphs:
            save_graph(graph, dataset)

        print(
            f"[{dataset.size_label}] {dataset.stem}: "
            f"nodes={summary['nodes']}, edges={summary['edges']}, "
            f"density={summary['density']:.6f}, avg_degree={summary['average_degree']:.2f}, "
            f"components={summary['connected_components']}, runtime={summary['build_runtime_seconds']:.2f}s"
        )

    profiles_df = pd.DataFrame(profiles).sort_values("size_label")
    summary_df = pd.DataFrame(summaries).sort_values("size_label")

    profiles_df.to_csv(TABLE_DIR / "dataset_profiles.csv", index=False)
    summary_df.to_csv(TABLE_DIR / "graph_summary.csv", index=False)

    metadata = {
        "selected_datasets": SELECTED_DATASETS,
        "generated_files": {
            "profiles_csv": str((TABLE_DIR / "dataset_profiles.csv").relative_to(PROJECT_ROOT)),
            "summary_csv": str((TABLE_DIR / "graph_summary.csv").relative_to(PROJECT_ROOT)),
            "figure_dir": str(FIGURE_DIR.relative_to(PROJECT_ROOT)),
        },
    }
    (OUTPUT_DIR / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_markdown_summary(summary_df)


if __name__ == "__main__":
    main()
