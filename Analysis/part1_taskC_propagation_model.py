#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import os
import pickle
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


INPUT_GRAPH_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part1_taskA" / "graphs"
OUTPUT_DIR = PROJECT_ROOT / "Analysis" / "outputs" / "part1_taskC"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
REPORT_DIR = OUTPUT_DIR / "reports"

GRAPH_ORDER = ["REQUEST_FOR_DELETION", "PROPERTY_PROPOSAL", "BOT_REQUESTS"]
SCENARIO_SEEDS = {
    "REQUEST_FOR_DELETION": 111,
    "PROPERTY_PROPOSAL": 222,
    "BOT_REQUESTS": 333,
}
SIR_PARAMS = {
    "REQUEST_FOR_DELETION": {"beta": 0.28, "gamma": 0.12, "steps": 8},
    "PROPERTY_PROPOSAL": {"beta": 0.26, "gamma": 0.11, "steps": 8},
    "BOT_REQUESTS": {"beta": 0.24, "gamma": 0.13, "steps": 8},
}


def ensure_dirs() -> None:
    for path in [OUTPUT_DIR, TABLE_DIR, FIGURE_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)


def load_graphs() -> dict[str, nx.Graph]:
    graphs: dict[str, nx.Graph] = {}
    for path in sorted(INPUT_GRAPH_DIR.glob("*.pickle")):
        with path.open("rb") as handle:
            graph = pickle.load(handle)
        graphs[graph.graph["dataset"]] = graph
    missing = [name for name in GRAPH_ORDER if name not in graphs]
    if missing:
        raise SystemExit(f"Missing Task A graph pickles for: {missing}. Re-run Task A with --save-graphs.")
    return graphs


def lcc_nodes(graph: nx.Graph) -> set[str]:
    if graph.number_of_nodes() == 0:
        return set()
    component = max(nx.connected_components(graph), key=len)
    return set(component)


def choose_infected_pair(graph: nx.Graph, seed: int) -> tuple[str, str, list[str]]:
    rng = random.Random(seed)
    nodes = sorted(lcc_nodes(graph))
    if len(nodes) < 2:
        raise ValueError("Need at least two nodes in the largest connected component.")
    infected = rng.sample(nodes, 2)
    return infected[0], infected[1], nodes


def shortest_path_distances(graph: nx.Graph, sources: list[str]) -> dict[str, float]:
    dist: dict[str, float] = {node: math.inf for node in graph.nodes()}
    for source in sources:
        lengths = nx.single_source_shortest_path_length(graph, source)
        for node, length in lengths.items():
            if length < dist[node]:
                dist[node] = float(length)
    return dist


def component_membership(graph: nx.Graph) -> dict[str, int]:
    membership: dict[str, int] = {}
    for component_id, component in enumerate(nx.connected_components(graph)):
        for node in component:
            membership[node] = component_id
    return membership


def shared_context_weight(graph: nx.Graph, sources: list[str]) -> dict[str, float]:
    source_set = set(sources)
    scores: dict[str, float] = {}
    for node in graph.nodes():
        total = 0.0
        for source in source_set:
            if graph.has_edge(node, source):
                total += float(graph[node][source].get("weight", 1))
        scores[node] = total
    return scores


def normalise(values: dict[str, float], inverse: bool = False) -> dict[str, float]:
    finite = [value for value in values.values() if math.isfinite(value)]
    if not finite:
        return {node: 0.0 for node in values}
    min_value = min(finite)
    max_value = max(finite)
    if math.isclose(min_value, max_value):
        return {node: 1.0 if math.isfinite(value) else 0.0 for node, value in values.items()}
    scale = max_value - min_value
    normalised: dict[str, float] = {}
    for node, value in values.items():
        if not math.isfinite(value):
            normalised[node] = 0.0 if inverse else 0.0
            continue
        raw = (value - min_value) / scale
        normalised[node] = 1.0 - raw if inverse else raw
    return normalised


def score_candidates(
    graph: nx.Graph,
    infected: list[str],
    scenario_name: str,
    degree_centrality: dict[str, float],
) -> pd.DataFrame:
    dist = shortest_path_distances(graph, infected)
    shared_weight = shared_context_weight(graph, infected)
    dist_score = normalise(dist, inverse=True)
    shared_score = normalise(shared_weight, inverse=False)
    degree_score = normalise(degree_centrality, inverse=False)
    membership = component_membership(graph)
    infected_components = {membership[node] for node in infected if node in membership}

    infected_set = set(infected)
    rows = []
    for node in graph.nodes():
        if node in infected_set:
            continue  # exclude known infected editors from the checking list
        same_component = int(membership.get(node) in infected_components)
        rows.append(
            {
                "scenario": scenario_name,
                "username": node,
                "distance_to_infected": dist[node] if math.isfinite(dist[node]) else None,
                "shared_context_weight": shared_weight[node],
                "degree_centrality": degree_centrality[node],
                "distance_score": dist_score[node],
                "shared_score": shared_score[node],
                "degree_score": degree_score[node],
                "combined_score": 0.5 * dist_score[node] + 0.3 * shared_score[node] + 0.2 * degree_score[node],
                "same_component": same_component,
            }
        )
    frame = pd.DataFrame(rows)
    frame = frame.sort_values(
        by=["combined_score", "distance_to_infected", "shared_context_weight", "degree_centrality"],
        ascending=[False, True, False, False],
        na_position="last",
    ).reset_index(drop=True)
    frame["rank"] = frame.index + 1
    return frame


def summarize_scenario(graph: nx.Graph, infected: list[str], seed: int) -> dict[str, object]:
    dist = shortest_path_distances(graph, infected)
    same_component_nodes = [node for node, value in dist.items() if math.isfinite(value)]
    reachable = len(same_component_nodes)
    dist_values = [value for value in dist.values() if math.isfinite(value)]
    degree_centrality = nx.degree_centrality(graph)
    infected_degrees = [graph.degree(node) for node in infected]
    infected_neighbors = set()
    for node in infected:
        infected_neighbors.update(graph.neighbors(node))
    within_two_hops = set()
    for source in infected:
        within_two_hops.update(nx.single_source_shortest_path_length(graph, source, cutoff=2).keys())
    within_three_hops = set()
    for source in infected:
        within_three_hops.update(nx.single_source_shortest_path_length(graph, source, cutoff=3).keys())
    same_component_share = reachable / graph.number_of_nodes() if graph.number_of_nodes() else 0.0
    return {
        "seed": seed,
        "infected_1": infected[0] if len(infected) > 0 else None,
        "infected_2": infected[1] if len(infected) > 1 else None,
        "infected_1_degree": infected_degrees[0] if len(infected_degrees) > 0 else None,
        "infected_2_degree": infected_degrees[1] if len(infected_degrees) > 1 else None,
        "infected_1_degree_centrality": degree_centrality[infected[0]] if len(infected) > 0 else None,
        "infected_2_degree_centrality": degree_centrality[infected[1]] if len(infected) > 1 else None,
        "same_component_share": same_component_share,
        "reachable_nodes": reachable,
        "average_finite_distance": float(sum(dist_values) / len(dist_values)) if dist_values else None,
        "max_finite_distance": float(max(dist_values)) if dist_values else None,
        "neighbors_1hop": len(infected_neighbors),
        "within_two_hops": len(within_two_hops),
        "within_three_hops": len(within_three_hops),
        "non_propagation_plausibility": assess_plausibility(graph, same_component_share, dist_values),
    }


def assess_plausibility(graph: nx.Graph, same_component_share: float, dist_values: list[float]) -> str:
    clustering = nx.average_clustering(graph)
    diameter_proxy = max(dist_values) if dist_values else math.inf
    if same_component_share < 0.5:
        return "high"
    if same_component_share > 0.95 and clustering > 0.3 and diameter_proxy <= 6:
        return "low"
    if same_component_share > 0.9 and clustering > 0.2 and diameter_proxy <= 8:
        return "moderate"
    return "moderate"


def sir_simulation(graph: nx.Graph, infected: list[str], beta: float, gamma: float, steps: int, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    states = {node: "S" for node in graph.nodes()}
    for node in infected:
        states[node] = "I"
    timeline = []
    for step in range(steps + 1):
        counts = {"S": 0, "I": 0, "R": 0}
        for state in states.values():
            counts[state] += 1
        timeline.append({"step": step, **counts})
        if step == steps:
            break
        new_states = states.copy()
        for node, state in states.items():
            if state != "I":
                continue
            for neighbor in graph.neighbors(node):
                if states[neighbor] == "S":
                    weight = float(graph[node][neighbor].get("weight", 1))
                    p_infect = min(0.95, beta * (1.0 + math.log1p(weight)))
                    if rng.random() < p_infect:
                        new_states[neighbor] = "I"
            if rng.random() < gamma:
                new_states[node] = "R"
        states = new_states
    return pd.DataFrame(timeline)


def plot_sir(timelines: dict[str, pd.DataFrame]) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, (dataset, timeline) in zip(axes, timelines.items()):
        ax.plot(timeline["step"], timeline["S"], label="S", color="#1f77b4")
        ax.plot(timeline["step"], timeline["I"], label="I", color="#d62728")
        ax.plot(timeline["step"], timeline["R"], label="R", color="#2ca02c")
        ax.set_title(dataset)
        ax.set_xlabel("Step")
        ax.grid(True, alpha=0.2)
    axes[0].set_ylabel("Nodes")
    axes[-1].legend(loc="upper right")
    fig.suptitle("Illustrative SIR propagation from two infected editors")
    fig.tight_layout()
    output = FIGURE_DIR / "sir_timeline.png"
    fig.savefig(output, dpi=220)
    plt.close(fig)
    return output


def plot_risk_overlay(graph: nx.Graph, infected: list[str], ranking: pd.DataFrame, dataset: str) -> Path:
    top_nodes = ranking.head(40)["username"].tolist()
    viz_nodes = set(infected) | set(top_nodes)
    viz_graph = graph.subgraph(viz_nodes).copy()
    layout = nx.spring_layout(viz_graph, seed=42, k=0.45, iterations=60, weight="weight")
    fig, ax = plt.subplots(figsize=(9, 7))
    degrees = dict(viz_graph.degree())
    top_nodes = set(top_nodes)
    node_colors = []
    node_sizes = []
    for node in viz_graph.nodes():
        if node in infected:
            node_colors.append("#d62728")
            node_sizes.append(100)
        elif node in top_nodes:
            node_colors.append("#ff7f0e")
            node_sizes.append(55)
        else:
            node_colors.append("#1f4e79")
            node_sizes.append(12 + degrees[node] * 0.4)
    nx.draw_networkx_edges(viz_graph, pos=layout, ax=ax, alpha=0.12, width=0.5, edge_color="#8d99ae")
    nx.draw_networkx_nodes(viz_graph, pos=layout, ax=ax, node_color=node_colors, node_size=node_sizes, linewidths=0)
    ax.set_title(f"{dataset}: infected seeds and top-risk editors")
    ax.set_axis_off()
    fig.tight_layout()
    output = FIGURE_DIR / f"{dataset.lower()}_risk_overlay.png"
    fig.savefig(output, dpi=220)
    plt.close(fig)
    return output


def narrative_row(dataset: str, summary_two: dict[str, object], graph: nx.Graph) -> dict[str, object]:
    clustering = nx.average_clustering(graph)
    transitivity = nx.transitivity(graph)
    if summary_two["non_propagation_plausibility"] == "high":
        assessment = "Non-propagation is fairly plausible because the infected pair does not cover most of the graph."
    elif clustering > 0.5 and summary_two["same_component_share"] > 0.9:
        assessment = "Non-propagation is weakly plausible; the graph is dense, clustered, and the infected pair sits in the main component."
    else:
        assessment = "Non-propagation is moderately plausible, but the main component is large enough that spread remains realistic."
    return {
        "dataset": dataset,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "average_clustering": clustering,
        "transitivity": transitivity,
        "infected_1": summary_two["infected_1"],
        "infected_2": summary_two["infected_2"],
        "same_component_share": summary_two["same_component_share"],
        "average_finite_distance": summary_two["average_finite_distance"],
        "max_finite_distance": summary_two["max_finite_distance"],
        "plausibility": summary_two["non_propagation_plausibility"],
        "interpretation": assessment,
    }


def write_markdown(summary_df: pd.DataFrame, ranking_df: pd.DataFrame, sir_df: pd.DataFrame, figure_paths: dict[str, str]) -> None:
    lines = [
        "# Part 1 Task C Summary",
        "",
        "## Scenario Summary",
        "",
        summary_df.to_markdown(index=False),
        "",
        "## Top Priority Rankings",
        "",
        ranking_df.head(30).to_markdown(index=False),
        "",
        "## SIR Illustration",
        "",
        sir_df.to_markdown(index=False),
        "",
        "## Figures",
        "",
    ]
    for key, path in figure_paths.items():
        lines.append(f"- {key}: `{path}`")
    (REPORT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    graphs = load_graphs()

    scenario_rows = []
    ranking_frames = []
    sir_timelines = {}
    figure_paths: dict[str, str] = {}

    for dataset in GRAPH_ORDER:
        graph = graphs[dataset]
        seed = SCENARIO_SEEDS[dataset]
        infected_1, infected_2, _ = choose_infected_pair(graph, seed)
        infected = [infected_1, infected_2]

        degree_centrality = nx.degree_centrality(graph)
        one_seed_ranking = score_candidates(graph, [infected_1], f"{dataset}_one_seed", degree_centrality)
        two_seed_ranking = score_candidates(graph, infected, f"{dataset}_two_seed", degree_centrality)

        summary_one = summarize_scenario(graph, [infected_1], seed)
        summary_two = summarize_scenario(graph, infected, seed)
        scenario_rows.append(narrative_row(dataset, summary_two, graph))

        one_seed_ranking = one_seed_ranking.copy()
        two_seed_ranking = two_seed_ranking.copy()
        one_seed_ranking["dataset"] = dataset
        one_seed_ranking["scenario"] = f"{dataset}_one_seed"
        two_seed_ranking["dataset"] = dataset
        two_seed_ranking["scenario"] = f"{dataset}_two_seed"
        column_order = [
            "dataset",
            "scenario",
            "rank",
            "username",
            "combined_score",
            "distance_to_infected",
            "shared_context_weight",
            "degree_centrality",
            "distance_score",
            "shared_score",
            "degree_score",
            "same_component",
        ]
        one_seed_ranking = one_seed_ranking[column_order]
        two_seed_ranking = two_seed_ranking[column_order]
        ranking_frames.append(one_seed_ranking.head(15))
        ranking_frames.append(two_seed_ranking.head(15))

        params = SIR_PARAMS[dataset]
        timeline = sir_simulation(
            graph=graph,
            infected=infected,
            beta=params["beta"],
            gamma=params["gamma"],
            steps=params["steps"],
            seed=seed,
        )
        sir_timelines[dataset] = timeline

        figure_paths[f"{dataset}_risk_overlay"] = str(
            plot_risk_overlay(graph, infected, two_seed_ranking, dataset).relative_to(OUTPUT_DIR)
        )

        # Keep a concise per-dataset audit trail in the JSON output.
        scenario_rows[-1].update(
            {
                "infected_1_degree": summary_two["infected_1_degree"],
                "infected_2_degree": summary_two["infected_2_degree"],
                "infected_1_degree_centrality": summary_two["infected_1_degree_centrality"],
                "infected_2_degree_centrality": summary_two["infected_2_degree_centrality"],
                "one_seed_plausibility": summary_one["non_propagation_plausibility"],
            }
        )

    sir_plot = plot_sir(sir_timelines)
    figure_paths["sir_timeline"] = str(sir_plot.relative_to(OUTPUT_DIR))

    summary_df = pd.DataFrame(scenario_rows)
    rankings_df = pd.concat(ranking_frames, ignore_index=True)
    sir_summary_df = pd.concat(
        [
            timeline.assign(dataset=dataset)
            for dataset, timeline in sir_timelines.items()
        ],
        ignore_index=True,
    )

    summary_df.to_csv(TABLE_DIR / "scenario_summary.csv", index=False)
    rankings_df.to_csv(TABLE_DIR / "priority_rankings.csv", index=False)
    sir_summary_df.to_csv(TABLE_DIR / "sir_timelines.csv", index=False)

    metadata = {
        "graph_order": GRAPH_ORDER,
        "scenario_seeds": SCENARIO_SEEDS,
        "sir_params": SIR_PARAMS,
        "outputs": {
            "scenario_summary": str((TABLE_DIR / "scenario_summary.csv").relative_to(OUTPUT_DIR)),
            "priority_rankings": str((TABLE_DIR / "priority_rankings.csv").relative_to(OUTPUT_DIR)),
            "sir_timelines": str((TABLE_DIR / "sir_timelines.csv").relative_to(OUTPUT_DIR)),
            "summary_md": str((REPORT_DIR / "summary.md").relative_to(OUTPUT_DIR)),
        },
        "figures": figure_paths,
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary_df, rankings_df, sir_summary_df, figure_paths)

    summary_rows = summary_df.to_dict("records")
    for row in summary_rows:
        print(
            f"[{row['dataset']}] seeds={row['infected_1']} / {row['infected_2']} "
            f"same_component_share={row['same_component_share']:.3f} plausibility={row['plausibility']}"
        )


if __name__ == "__main__":
    main()
