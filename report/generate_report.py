#!/usr/bin/env python3
"""
Generate the Network Data Analysis coursework report as PDF.

Student: Shui Zhou (K25120780)
Module: 7CUSMNDA Network Data Analysis
KCL Urban Informatics MSc 2025-26

Usage:
    python3 report/generate_report.py

Output:
    report/K25120780_7CUSMNDA_Coursework.pdf
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

from fpdf import FPDF
from PIL import Image as PILImage

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = PROJECT_ROOT / "Analysis" / "outputs"
REPORT_DIR = PROJECT_ROOT / "report"

# Page geometry
PAGE_W = 210  # A4 width mm
MARGIN = 18
CONTENT_W = PAGE_W - 2 * MARGIN
COL_W = CONTENT_W / 2 - 2  # for 2-up figures

# Colours
HEADING1_COLOR = (20, 50, 100)   # dark navy
HEADING2_COLOR = (30, 60, 110)
HEADING3_COLOR = (40, 40, 40)
BODY_COLOR = (30, 30, 30)
CAPTION_COLOR = (80, 80, 80)
RULE_COLOR = (180, 200, 220)     # light blue rule


def _img_height_mm(path: Path, width_mm: float) -> float:
    """Return the rendered height in mm for an image placed at *width_mm*."""
    img = PILImage.open(path)
    w_px, h_px = img.size
    return width_mm * (h_px / w_px)


class ReportPDF(FPDF):
    """Custom PDF with header/footer for the coursework report."""

    # ── Serif body font: Times; Sans headings: Helvetica ────

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, "7CUSMNDA Network Data Analysis Coursework  |  Shui Zhou (K25120780)", align="C")
        self.ln(7)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, f"Page {self.page_no() - 1}", align="C")

    # ── helpers ──────────────────────────────────────────────

    def section_title(self, title: str, level: int = 1):
        sizes = {1: 14, 2: 12, 3: 10.5}
        colors = {1: HEADING1_COLOR, 2: HEADING2_COLOR, 3: HEADING3_COLOR}
        self.set_font("Helvetica", "B", sizes.get(level, 10.5))
        self.set_text_color(*colors.get(level, HEADING3_COLOR))
        if level == 1:
            self.ln(5)
        elif level == 2:
            self.ln(3)
        else:
            self.ln(2)
        self.multi_cell(CONTENT_W, 6.5, title)
        if level == 1:
            # thin rule under main headings
            y = self.get_y()
            self.set_draw_color(*RULE_COLOR)
            self.set_line_width(0.4)
            self.line(self.l_margin, y, self.l_margin + CONTENT_W, y)
            self.ln(2.5)
        else:
            self.ln(1.5)

    def body(self, text: str):
        self.set_font("Times", "", 10.5)
        self.set_text_color(*BODY_COLOR)
        self.multi_cell(CONTENT_W, 4.8, text)
        self.ln(1.2)

    def body_italic(self, text: str):
        self.set_font("Times", "I", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(CONTENT_W, 4.8, text)
        self.ln(1)

    def table_row(self, cells: list[str], widths: list[float], bold: bool = False):
        self.set_font("Helvetica", "B" if bold else "", 8.5)
        self.set_text_color(0, 0, 0)
        for cell_text, w in zip(cells, widths):
            self.cell(w, 5.8, cell_text, border=1, align="C")
        self.ln()

    def add_figure(self, path: str | Path, caption: str, width: float = CONTENT_W * 0.85):
        p = Path(path)
        if not p.exists():
            self.body(f"[Figure not found: {p.name}]")
            return
        h = _img_height_mm(p, width)
        self.check_space(h + 15)
        x = self.l_margin + (CONTENT_W - width) / 2
        self.image(str(p), x=x, w=width)
        self.ln(1)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*CAPTION_COLOR)
        self.multi_cell(CONTENT_W, 4, caption)
        self.ln(2)

    def add_figures_2up(self, path1: str | Path, path2: str | Path, caption: str, width: float | None = None):
        gap = 6  # mm gap between images
        if width is None:
            width = (CONTENT_W - gap) / 2
        p1, p2 = Path(path1), Path(path2)
        # compute max height from actual image aspect ratios
        max_h = 0.0
        for p in [p1, p2]:
            if p.exists():
                max_h = max(max_h, _img_height_mm(p, width))
        self.check_space(max_h + 15)
        y_start = self.get_y()
        if p1.exists():
            self.image(str(p1), x=self.l_margin, y=y_start, w=width)
        if p2.exists():
            self.image(str(p2), x=self.l_margin + width + gap, y=y_start, w=width)
        self.set_y(y_start + max_h + 2)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*CAPTION_COLOR)
        self.multi_cell(CONTENT_W, 4, caption)
        self.ln(2)

    def add_figures_3up(self, paths: list[str | Path], caption: str):
        gap = 3
        w = (CONTENT_W - 2 * gap) / 3
        max_h = 0.0
        for p in paths:
            pp = Path(p)
            if pp.exists():
                max_h = max(max_h, _img_height_mm(pp, w))
        self.check_space(max_h + 15)
        y_start = self.get_y()
        for i, p in enumerate(paths):
            pp = Path(p)
            if pp.exists():
                self.image(str(pp), x=self.l_margin + i * (w + gap), y=y_start, w=w)
        self.set_y(y_start + max_h + 2)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*CAPTION_COLOR)
        self.multi_cell(CONTENT_W, 4, caption)
        self.ln(2)

    def check_space(self, needed_mm: float):
        """Add page break if less than needed_mm remains."""
        if self.get_y() + needed_mm > 280:
            self.add_page()


def fig(relative: str) -> Path:
    return FIGURE_DIR / relative


def read_csv_rows(relative: str) -> list[dict[str, str]]:
    path = FIGURE_DIR / relative
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_single_row_csv(relative: str) -> dict[str, str]:
    rows = read_csv_rows(relative)
    if not rows:
        raise ValueError(f"No rows found in {relative}")
    return rows[0]


def fmt_km(distance_m: float) -> str:
    return f"{distance_m / 1000:.2f} km"


def fmt_gap_km(gap_m: float) -> str:
    return f"{gap_m / 1000:+.2f} km"


def build_report() -> Path:
    intersection_stats = read_single_row_csv("part2_taskB/tables/intersection_distance_summary.csv")
    marathon_routes = {row["seed_label"]: row for row in read_csv_rows("part2_taskC/tables/marathon_routes.csv")}
    marathon_routes_refined = {row["seed_label"]: row for row in read_csv_rows("part2_taskC/tables/marathon_routes_refined.csv")}

    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(MARGIN)
    pdf.set_right_margin(MARGIN)

    # ══════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*HEADING1_COLOR)
    pdf.cell(CONTENT_W, 12, "Network Data Analysis", align="C")
    pdf.ln(14)
    pdf.set_font("Times", "I", 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(CONTENT_W, 10, "Coursework Report", align="C")
    pdf.ln(25)
    pdf.set_font("Times", "", 12)
    pdf.set_text_color(*BODY_COLOR)
    for line in [
        "Module: 7CUSMNDA Network Data Analysis",
        "Student: Shui Zhou",
        "Student ID: K25120780",
        "Programme: MSc Urban Informatics",
        "Institution: King's College London",
        "Date: April 2026",
        "Code Repository:",
        "https://github.com/Shui-Zhou/kcl-network-data-analysis-final",
    ]:
        pdf.multi_cell(CONTENT_W, 8, line, align="C")
        pdf.ln(1.5)

    # ══════════════════════════════════════════════════════════
    # PART 1: WIKIDATA EDITOR NETWORKS
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("Part 1: Wikidata Editor Co-Comment Networks")

    pdf.body(
        "Wikidata, the structured knowledge base maintained by the Wikimedia Foundation, relies on "
        "community-driven editorial processes including property proposals, deletion reviews, and bot "
        "task requests. Each process generates discussion threads where editors participate through "
        "comments. In this part, I construct and analyse co-comment networks from three Wikidata "
        "discussion datasets, representing different scales and community dynamics. I characterise "
        "these networks using small-world and scale-free metrics, and simulate trolling propagation "
        "to assess community vulnerability to disruptive behaviour."
    )

    # ── Task A ───────────────────────────────────────────────
    pdf.section_title("Task A: Network Construction", 2)

    pdf.section_title("Dataset Selection and Edge Definition", 3)
    pdf.body(
        "Three Wikidata discussion datasets were selected to represent different scales and community "
        "types, each containing three columns: thread_subject, username, and page_name."
    )
    pdf.body(
        "REQUEST_FOR_DELETION (large, 648,637 records): Discussions about proposed deletions of "
        "Wikidata items. This is the largest dataset by far, involving 9,935 unique editors across "
        "316,267 unique threads on 3,303 pages. Deletion debates tend to attract a broad cross-section "
        "of the community, including both domain experts and administrative power-users."
    )
    pdf.body(
        "PROPERTY_PROPOSAL (medium, 52,160 records): Discussions proposing new properties for the "
        "Wikidata knowledge graph. This dataset involves 3,058 editors across 10,005 threads on 8,649 "
        "pages. Property proposals follow a structured voting process, where many community members "
        "express support or opposition, creating dense interaction patterns."
    )
    pdf.body(
        "BOT_REQUESTS (small, 2,981 records): Requests for automated bot operations on Wikidata. "
        "This involves 552 editors across 1,113 threads on 108 pages. Bot requests are technically "
        "specialised discussions involving a smaller community of bot operators and task requesters."
    )
    pdf.body(
        "Nodes represent unique Wikidata editors (usernames). An undirected edge connects two editors "
        "if they both participated in at least one common discussion, defined as appearing in the same "
        "(page_name, thread_subject) pair. Edge weight equals the number of distinct (page, thread) "
        "contexts in which two editors co-commented. This captures both the existence and intensity of "
        "editorial interaction."
    )

    pdf.section_title("Data Structures", 3)
    pdf.body(
        "I use networkx.Graph (undirected, no self-loops) with adjacency-list representation. "
        "Undirected edges reflect the symmetric nature of co-commenting: if editors A and B both "
        "commented on thread T, their relationship is mutual. Node attributes store activity metadata "
        "(comment count, unique pages, unique threads). Edge attributes store the co-occurrence weight "
        "and the list of shared discussion contexts, enabling traceability from any edge back to its "
        "source discussions."
    )

    pdf.section_title("Algorithmic Approach", 3)
    pdf.body(
        "The construction proceeds in four steps: (1) Load the CSV and deduplicate so each "
        "(username, page_name, thread_subject) triple is counted once. (2) Group rows by "
        "(page_name, thread_subject) to identify co-participants in each discussion. "
        "(3) For each group with two or more participants, generate all unique user pairs via "
        "itertools.combinations. (4) Accumulate edge weights in a dictionary and construct the "
        "networkx graph. Time complexity is O(sum of C(g_i, 2)) where g_i is the number of unique "
        "users in group i. The largest group contains 21 users (C(21,2) = 210 pairs), but the "
        "median group size is 2, keeping overall computation efficient (1.77 seconds for the "
        "648K-row dataset)."
    )

    pdf.section_title("Summary Statistics", 3)

    # Summary table
    col_w = [CONTENT_W * f for f in [0.22, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13]]
    pdf.table_row(["Metric", "RFD", "PP", "BR", "RFD", "PP", "BR"], col_w, bold=True)
    pdf.table_row(["", "(Large)", "(Medium)", "(Small)", "Random", "Random", "Random"], col_w, bold=True)
    for row in [
        ["Nodes", "9,935", "3,058", "552", "9,935", "3,058", "552"],
        ["Edges", "33,497", "46,154", "2,424", "33,497", "46,154", "2,424"],
        ["Density", "0.0007", "0.0099", "0.0159", "0.0007", "0.0099", "0.0159"],
        ["Avg Degree", "6.74", "30.19", "8.78", "6.74", "30.19", "8.78"],
        ["Max Degree", "4,940", "1,399", "226", "14", "40", "18"],
        ["Components", "57", "8", "29", "15", "1", "1"],
        ["Giant Comp %", "99.4%", "99.8%", "94.0%", "99.8%", "100%", "100%"],
    ]:
        pdf.table_row(row, col_w)

    pdf.ln(2)
    pdf.body(
        "A notable finding is that PROPERTY_PROPOSAL produces more edges (46,154) than the much larger "
        "REQUEST_FOR_DELETION (33,497). This is because PP discussions have a median of 5 participants "
        "per thread (vs 2 for RFD), generating C(5,2) = 10 pairwise connections per group compared to "
        "C(2,2) = 1. The structured voting process in property proposals naturally creates denser "
        "interaction patterns."
    )

    # Degree distribution figures (3-up)
    pdf.check_space(65)
    pdf.add_figures_3up(
        [
            fig("part1_taskA/figures/REQUEST_FOR_DELETION_degree_distribution.png"),
            fig("part1_taskA/figures/PROPERTY_PROPOSAL_degree_distribution.png"),
            fig("part1_taskA/figures/BOT_REQUESTS_degree_distribution.png"),
        ],
        "Figure 1: Degree distributions (log-log) for the three co-comment networks. "
        "All three show heavy-tailed distributions extending far beyond random baselines.",
    )

    # BOT_REQUESTS network vis
    pdf.check_space(75)
    pdf.add_figure(
        fig("part1_taskA/figures/BOT_REQUESTS_network.png"),
        "Figure 2: Full network visualization of BOT_REQUESTS (552 nodes, 2,424 edges). "
        "Node colour indicates degree (lighter = higher). A dense core of active editors is "
        "surrounded by peripheral contributors, with several small disconnected components "
        "visible at the margins. The spring layout reveals the community structure: tightly "
        "clustered subgroups connected through a few bridge nodes.",
        width=CONTENT_W * 0.70,
    )

    pdf.body(
        "The BOT_REQUESTS visualization (Figure 2) reveals the characteristic structure shared by "
        "all three networks: a dense core of highly active editors surrounded by a periphery of "
        "occasional contributors. The 29 connected components are visible as isolated clusters at "
        "the edges. This structure reflects the specialised nature of bot request discussions, where "
        "a core community of bot operators and reviewers handles most requests while occasional users "
        "submit isolated requests."
    )

    # ── Task B ───────────────────────────────────────────────
    pdf.check_space(30)
    pdf.section_title("Task B: Network Metrics and Small-World Analysis", 2)

    pdf.body(
        "I compare each observed network against Erdos-Renyi random graphs with identical node and "
        "edge counts (averaged over three random seeds). The small-world coefficient sigma = "
        "(C/C_random) / (L/L_random) quantifies deviation from randomness, where sigma >> 1 indicates "
        "small-world structure (Watts & Strogatz, 1998)."
    )

    # Metrics table
    col_w2 = [CONTENT_W * f for f in [0.28, 0.18, 0.18, 0.18, 0.18]]
    pdf.table_row(["Metric", "RFD", "PP", "BR", "Random (avg)"], col_w2, bold=True)
    for row in [
        ["Avg Clustering (C)", "0.392", "0.814", "0.658", "0.0005-0.017"],
        ["Transitivity", "0.014", "0.139", "0.175", "~density"],
        ["Avg Path Length (L)", "2.73*", "2.38", "2.60", "5.01/2.73/3.14"],
        ["Diameter", "5**", "5", "6", "9/4/5"],
        ["sigma", "1,394", "93", "47", "-"],
        ["Max Betweenness", "0.49", "0.11", "0.26", "-"],
    ]:
        pdf.table_row(row, col_w2)
    pdf.body_italic("* sampled BFS (256 sources); ** approximate diameter")

    pdf.ln(1)
    pdf.section_title("Small-World Spectrum Positioning", 3)
    pdf.body(
        "All three networks are firmly in the small-world regime (sigma >> 1), but exhibit distinct "
        "flavours. REQUEST_FOR_DELETION (sigma = 1,394) has a super-hub with degree 4,940 connecting "
        "approximately 50% of all nodes. This creates 'ultra-small-world' behaviour where L is actually "
        "shorter than L_random (ratio 0.54), more accurately described as hub-dominated with small-world "
        "properties, consistent with preferential attachment dynamics (Barabasi-Albert, 1999). "
        "PROPERTY_PROPOSAL (sigma = 93) most closely matches the classic Watts-Strogatz model: "
        "extremely high clustering (C = 0.81) from overlapping voting cliques, with L approximately "
        "equal to L_random. BOT_REQUESTS (sigma = 47) is an intermediate case with moderate clustering "
        "and more fragmentation (29 components vs 8 and 57)."
    )
    pdf.body(
        "The gap between average clustering and transitivity in all three networks (e.g., PP: 0.81 vs "
        "0.14) indicates that high-degree hub nodes have low local clustering. This is a hallmark of "
        "scale-free networks: hubs connect disparate communities but their neighbours do not form tight "
        "cliques among themselves."
    )

    pdf.section_title("Degree Distribution Analysis", 3)
    pdf.body(
        "The complementary cumulative distribution function (CCDF) plots in Figure 3 compare the "
        "observed degree distributions against matched Erdos-Renyi random baselines. In all three "
        "networks, the observed distributions extend far beyond the random cutoff. "
        "REQUEST_FOR_DELETION spans three orders of magnitude (degree 1 to ~5,000), while the "
        "matched random graph's maximum degree is only ~14. PROPERTY_PROPOSAL spans from degree 1 "
        "to ~1,400 versus a random maximum of ~40. Even BOT_REQUESTS extends to degree ~226 versus "
        "a random maximum of ~18. Visual inspection of the log-log CCDF suggests heavy-tailed degree "
        "distributions in all three networks, though I note that formal power-law fitting (e.g., via "
        "the Clauset et al., 2009, methodology) was not performed. The heavy tails are consistent with "
        "preferential attachment dynamics (Barabasi & Albert, 1999), where new editors preferentially "
        "interact with already well-connected editors, but alternative heavy-tailed distributions "
        "(e.g., log-normal, stretched exponential) cannot be ruled out without formal testing."
    )

    # CCDF figures (3-up)
    pdf.check_space(65)
    pdf.add_figures_3up(
        [
            fig("part1_taskB/figures/REQUEST_FOR_DELETION_degree_ccdf_vs_random.png"),
            fig("part1_taskB/figures/PROPERTY_PROPOSAL_degree_ccdf_vs_random.png"),
            fig("part1_taskB/figures/BOT_REQUESTS_degree_ccdf_vs_random.png"),
        ],
        "Figure 3: Degree CCDF (complementary cumulative distribution) comparing observed networks (blue) vs matched random baselines "
        "(orange). All observed distributions exhibit heavy right tails extending 1-2 orders of "
        "magnitude beyond the random cutoff.",
    )

    pdf.section_title("Centrality Analysis", 3)
    pdf.body(
        "Betweenness centrality reveals the bridge structure of each network. In REQUEST_FOR_DELETION, "
        "the maximum betweenness centrality is 0.49, meaning a single editor mediates nearly half of "
        "all shortest paths. This extreme concentration reflects a deletion review process dominated "
        "by a few power-users who participate across many discussion threads. In PROPERTY_PROPOSAL, "
        "maximum betweenness drops to 0.11, suggesting more distributed information flow through the "
        "structured voting system. BOT_REQUESTS has maximum betweenness of 0.26, indicating moderate "
        "concentration through key bot operators who bridge different task domains."
    )
    pdf.body(
        "The relationship between degree centrality and betweenness centrality differs across networks. "
        "In RFD, the highest-degree node is also the highest-betweenness node, consistent with a "
        "star-like topology. In PP, the correlation is weaker: high-degree nodes are embedded in dense "
        "cliques where many alternative paths exist, reducing their betweenness. This structural "
        "difference has implications for network resilience: removing the top-betweenness node in RFD "
        "would fragment the network far more than doing so in PP."
    )

    # ── Task C ───────────────────────────────────────────────
    pdf.check_space(30)
    pdf.section_title("Task C: Trolling Propagation Analysis", 2)

    pdf.section_title("SIR Model Setup", 3)
    pdf.body(
        "I model trolling propagation using the SIR (Susceptible-Infected-Recovered) framework from "
        "epidemiology, adapted for social networks (Del Vicario et al., 2016). In this analogy, "
        "'infection' represents the adoption of trolling behaviour, 'recovery' represents moderation or "
        "self-correction, and network edges represent the co-comment interactions through which "
        "disruptive behaviour can spread. Two randomly selected editors are designated as initial "
        "'infected' seeds. The SIR parameters are calibrated per-network using mean degree and "
        "clustering: beta (transmission rate) ranges from 0.24 to 0.28, and gamma (recovery rate) "
        "from 0.11 to 0.13. Transmission probability at each edge is scaled by log-weight, "
        "so stronger co-comment ties transmit more readily. The simulation runs for 8 steps "
        "with a single deterministic seed per dataset. It serves as supporting evidence rather than "
        "the main answer: the primary analysis is a structural risk assessment based on shortest "
        "paths, neighbourhood overlap, and local clustering."
    )
    pdf.body(
        "The choice of SIR over simpler models (e.g., SI or SIS) is deliberate: the recovery mechanism "
        "models the real-world effect of community moderation, where editors may initially adopt trolling "
        "behaviour but subsequently desist due to peer pressure, warnings, or sanctions. Cheng et al. "
        "(2017) demonstrated that trolling behaviour in online communities is context-dependent and "
        "recoverable, supporting the SIR assumption of transient infection rather than permanent state "
        "change."
    )

    pdf.section_title("Question 1: Is non-propagation plausible?", 3)
    pdf.body(
        "I consider a scenario where two randomly selected editors exhibit trolling behaviour and "
        "assess whether it is plausible that this behaviour has not spread to others. The structural "
        "analysis suggests non-propagation is weakly plausible but unlikely, based on four factors:"
    )
    pdf.body(
        "(1) Giant component dominance: 94-99.7% of editors are in the same connected component, "
        "meaning virtually any two editors are reachable from each other. "
        "(2) Short path lengths: average distances of 2.2-2.7 hops mean that even seemingly unrelated "
        "editors are only 2-3 discussion threads apart. "
        "(3) High clustering amplifies local spread: clustering coefficients of 0.39-0.81 mean that an "
        "infected editor's neighbours share many mutual connections, facilitating rapid local saturation. "
        "(4) Hub vulnerability: super-hubs connected to a large fraction of the network could serve as "
        "amplifiers if infected."
    )
    pdf.body(
        "However, non-propagation could occur if the infected pair are peripheral (low degree), if the "
        "'infection' requires sustained interaction rather than mere network proximity, or if community "
        "moderation acts as a recovery mechanism. In my sampled scenarios, the randomly selected seed "
        "pairs are REQUEST_FOR_DELETION (Doff, degree 3, and Jr8825, degree 1), PROPERTY_PROPOSAL "
        "(Ayoungprogrammer, degree 3, and Faux, degree 80), and BOT_REQUESTS (Powerek38, degree 4, "
        "and Pyb, degree 10). Despite starting from low-degree seeds in RFD and BR, the SIR simulation "
        "shows that by step 8, 96% of RFD, 99.5% of PP, and 92% of BR nodes are infected or recovered. "
        "Even with conservative parameters, the network structure facilitates rapid spread."
    )

    # SIR figure
    pdf.check_space(50)
    pdf.add_figure(
        fig("part1_taskC/figures/sir_timeline.png"),
        "Figure 4: SIR propagation from two infected editors across all three networks over 8 steps. "
        "PP (medium) shows the fastest cascade; all three reach 92-99% infection by step 8.",
        width=CONTENT_W * 0.90,
    )

    # Risk overlay figures
    pdf.check_space(55)
    pdf.add_figures_3up(
        [
            fig("part1_taskC/figures/request_for_deletion_risk_overlay.png"),
            fig("part1_taskC/figures/property_proposal_risk_overlay.png"),
            fig("part1_taskC/figures/bot_requests_risk_overlay.png"),
        ],
        "Figure 5: Risk overlay networks showing infected seeds (red) and high-priority editors "
        "(orange) for each dataset. Edge opacity reflects connection strength.",
    )

    pdf.section_title("Question 2: Priority checking list", 3)
    pdf.body(
        "I rank non-infected editors using a composite risk score: 50% inverse shortest-path distance "
        "to infected editors (proximity), 30% shared discussion context weight (direct interaction), "
        "and 20% degree centrality (influence potential). This network-informed triage balances "
        "structural proximity with interaction history. The weighting reflects the principle that "
        "proximity to an infected node is the strongest predictor of risk, followed by the intensity "
        "of direct interaction, with overall network influence as a secondary factor. I acknowledge "
        "these weights are heuristic: no sensitivity analysis or cross-validation was performed, and "
        "alternative weightings could produce materially different rankings. The resulting ranking "
        "is therefore a pragmatic triage list, not an estimated causal infection probability."
    )
    pdf.body(
        "Comparing one-infected vs two-infected scenarios reveals how additional infection sources "
        "reshape risk. In REQUEST_FOR_DELETION, with one infected editor (Doff, degree 3), the top "
        "priorities are Doff's three direct co-commenters (Ymblanter, Inkowik, Bill william compton), "
        "all at distance 1 with shared context weight 1. Adding Jr8825 as a second infected editor "
        "promotes BeneBot* from rank 6 to rank 1, because BeneBot* is directly connected to Jr8825 "
        "and has the highest degree centrality (0.44) among all distance-1 neighbours of the infected "
        "set. This demonstrates that each additional infected node opens a new propagation front that "
        "fundamentally changes the priority landscape."
    )
    pdf.body(
        "In PROPERTY_PROPOSAL, the effect is even more dramatic because the network is denser. Adding "
        "a second infected editor in the main component exposes a much larger neighbourhood to "
        "distance-1 risk. In BOT_REQUESTS, the smaller network means the top-priority lists for "
        "one-seed and two-seed scenarios overlap more heavily, as most high-centrality editors are "
        "already close to both seeds. The methodology aligns with influence maximization research "
        "(Kempe et al., 2003), adapted here for the inverse problem of identifying at-risk nodes "
        "from known infection sources."
    )

    pdf.section_title("Priority List Excerpt (REQUEST_FOR_DELETION)", 3)
    pdf.body_italic(
        "Top-5 non-infected editors to check, under one-seed vs two-seed scenarios "
        "(infected editors excluded from the ranking):"
    )
    col_pr = [CONTENT_W * f for f in [0.06, 0.24, 0.14, 0.14, 0.06, 0.24, 0.06, 0.06]]
    pdf.table_row(["Rank", "1-seed", "Dist", "Score", "|", "2-seed", "Dist", "Score"], col_pr, bold=True)
    pdf.table_row(["1", "Ymblanter", "1", "0.70", "|", "BeneBot*", "1", "0.85"], col_pr)
    pdf.table_row(["2", "Inkowik", "1", "0.68", "|", "Ymblanter", "1", "0.70"], col_pr)
    pdf.table_row(["3", "B.w.compton", "1", "0.68", "|", "Inkowik", "1", "0.68"], col_pr)
    pdf.table_row(["4", "DeltaBot", "2", "0.45", "|", "B.w.compton", "1", "0.68"], col_pr)
    pdf.table_row(["5", "BeneBot*", "2", "0.43", "|", "DeltaBot", "2", "0.45"], col_pr)
    pdf.ln(1)
    pdf.body(
        "BeneBot* rises from rank 5 to rank 1 when Jr8825 is added as a second infected editor, "
        "because BeneBot* is directly connected to Jr8825 and has the highest degree centrality (0.44) "
        "among distance-1 neighbours of the infected set. Meanwhile, the three direct neighbours of Doff "
        "(Ymblanter, Inkowik, Bill william compton) retain high scores in both scenarios, demonstrating "
        "the stability of proximity-based risk in dense regions of the network."
    )

    # ── Final Comparison D1-D4 ───────────────────────────────
    pdf.check_space(30)
    pdf.section_title("Comparative Discussion", 2)

    pdf.body(
        "All three Wikidata editor co-comment networks fall in the small-world/scale-free region of "
        "the network spectrum, far from both regular lattices and Erdos-Renyi random graphs. However, "
        "they occupy distinct positions reflecting their different social functions. "
        "REQUEST_FOR_DELETION has the most hub-dominated topology: the deletion process attracts a "
        "small number of prolific reviewers who participate in a very large fraction of discussions, "
        "creating extreme degree concentration and a super-hub dominating betweenness centrality (0.49). "
        "PROPERTY_PROPOSAL is the most classically small-world: the structured voting process creates "
        "dense, overlapping cliques (C = 0.81), closely matching the Watts-Strogatz model. "
        "BOT_REQUESTS is intermediate and most fragmented, reflecting the specialised nature of bot "
        "task requests."
    )
    pdf.body(
        "My edge definition (co-comment in same page and thread) captures meaningful interaction but "
        "has limitations. Symmetric edges cannot distinguish initiators from responders; no temporal "
        "dimension means edges from 2013 and 2020 are treated identically; and thread-level granularity, "
        "while avoiding spurious connections, may miss editors who read but do not comment. These "
        "construction choices shape the observed network structure and should be considered when "
        "interpreting metrics."
    )
    pdf.body(
        "My findings are consistent with prior work on Wikimedia editor networks. Brandes et al. "
        "(2009) found small-world properties and heavy-tailed degree distributions in Wikipedia "
        "co-authorship networks. Piscopo et al. (2024) specifically studied Wikidata discussions and "
        "found small-world structure with a small core of highly active editors responsible for the "
        "majority of contributions. My super-hub finding quantifies this concentration at the network "
        "level. The co-comment networks reveal that Wikidata editorial communities function as "
        "hierarchically organised small worlds: a small core of hub editors provides structural "
        "cohesion bridging disparate discussion domains, while local clusters form around specific "
        "topics, producing the high clustering coefficients observed."
    )

    pdf.section_title("Scale-Free vs Small-World Distinction", 3)
    pdf.body(
        "An important nuance in my results is the distinction between hub-dominated and classic "
        "small-world properties. REQUEST_FOR_DELETION exhibits strong hub dominance: a super-hub with "
        "degree 4,940, a heavy-tailed degree distribution, and an average path length shorter than the "
        "random baseline (L/L_random = 0.54). This 'ultra-short' path property is consistent with "
        "hub-mediated connectivity (Barabasi & Albert, 1999), where hubs create shortcuts, rather than "
        "classic small-world networks where L approximately equals L_random. I note that without formal "
        "power-law fitting, the precise distributional form remains uncertain. PROPERTY_PROPOSAL, by "
        "contrast, most closely matches the classic Watts-Strogatz (1998) model: high clustering from "
        "dense voting cliques combined with path lengths comparable to random. BOT_REQUESTS falls "
        "between these archetypes."
    )
    pdf.body(
        "The sigma metric captures this distinction imperfectly. RFD's extreme sigma of 1,394 is driven "
        "by both high clustering (C/C_random >> 1) and short paths (L/L_random < 1), but the standard "
        "sigma interpretation assumes L >= L_random. I report sigma for comparability with the literature "
        "while noting that the underlying mechanism differs: RFD's high sigma reflects hub-mediated "
        "connectivity rather than regular-lattice-like local structure."
    )

    pdf.section_title("Implications for Community Governance", 3)
    pdf.body(
        "The heavy reliance on hub editors in RFD creates a single point of failure: if the "
        "top-betweenness editor becomes inactive, the network's connectivity would substantially "
        "decrease. PP's more distributed structure is more resilient but slower to propagate "
        "information. Understanding these structural properties can inform governance strategies "
        "for collaborative knowledge platforms (Piscopo et al., 2024)."
    )

    # ══════════════════════════════════════════════════════════
    # PART 2: LEEDS ROAD NETWORK
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("Part 2: Leeds Road Network Analysis")

    pdf.body(
        "In this part, I shift from social networks to spatial networks, analysing the road network "
        "of Leeds, UK, and its relationship to traffic accident patterns. I download and characterise "
        "a local road network, analyse accident clustering using network-constrained spatial statistics, "
        "and extend to a city-wide network Voronoi partition for marathon route planning. Throughout, "
        "I emphasise the distinction between planar and network-based spatial methods, following "
        "Yamada and Thill (2004) and Okabe et al. (2000)."
    )

    # ── Task A ───────────────────────────────────────────────
    pdf.section_title("Task A: Spatial Network and Planarity", 2)

    pdf.body(
        "I loaded 21,435 accident records across 2009-2016 from the Leeds metropolitan area. "
        "Column name harmonisation was required: 2009-2012 files use 'Easting'/'Northing' while "
        "2013-2016 use 'Grid Ref: Easting'/'Grid Ref: Northing'. All coordinates are in British "
        "National Grid (EPSG:27700) and were converted to WGS84 (EPSG:4326) for osmnx compatibility "
        "using pyproj. Records with missing or zero coordinates were dropped, and the coordinate "
        "ranges were validated against the known Leeds boundary to detect anomalies."
    )
    pdf.body(
        "To find the optimal 1 km square study area, I overlaid a 1 km grid on all accident "
        "locations and counted accidents per cell. The densest cell spans the BNG bbox "
        "430000-431000 E, 433000-434000 N (approximately 53.7924-53.8014 N, -1.5461 to -1.5308 W) "
        "with 851 accidents, placing it over Leeds city centre just north of the River Aire and "
        "around Leeds City railway station, roughly 916 m from the overall accident centroid. "
        "This substantially exceeds the minimum requirement of 300 accidents and provides a "
        "rich dataset for spatial analysis."
    )
    pdf.body(
        "The road network was downloaded via osmnx 2.x using graph_from_bbox with network_type='drive' "
        "and truncate_by_edge=True (retaining full edges that cross the boundary). This yielded a "
        "MultiDiGraph with 266 nodes and 446 directed edges, which was simplified to an undirected "
        "graph for analysis."
    )

    pdf.check_space(60)
    pdf.add_figures_2up(
        fig("part2_taskA/figures/accident_density_grid.png"),
        fig("part2_taskA/figures/road_network_selected_area.png"),
        "Figure 6: Left - Accident density by 1 km grid cell (2009-2016). The green box marks the "
        "selected area (851 accidents). Right - Road network with accident points (red) in the "
        "selected area.",
    )

    pdf.section_title("Network Characteristics", 3)

    col_w3 = [CONTENT_W * 0.55, CONTENT_W * 0.45]
    for row in [
        ["Average street length", "65.3 m"],
        ["Average circuity", "1.040"],
        ["Node density (per km2)", "266"],
        ["Intersection density (per km2)", "235"],
        ["Edge density (per km2)", "446 directed / 358 street segments"],
        ["Street length density", "28.8 km/km2"],
        ["Spatial diameter", "2,714.7 m"],
        ["Planar", "No"],
    ]:
        pdf.table_row(row, col_w3)

    pdf.ln(2)
    pdf.body(
        "Circuity of 1.04 indicates highly direct roads, typical of a dense urban grid where routes "
        "are only 4% longer than straight-line distances. Boeing (2017) reports circuity values of "
        "1.01-1.10 for well-connected city centres. The spatial diameter of 2,715 m (longest shortest "
        "path using physical road lengths via Dijkstra's algorithm on the largest connected component) "
        "shows the road network approximately doubles the straight-line diagonal distance of the 1 km "
        "square, reflecting grid barriers such as one-way systems and the river. Edge density is "
        "reported both as a count (446 directed edges in the MultiDiGraph, collapsing to 358 unique "
        "street segments after removing parallel directions) and as street length density (28.8 km of "
        "road per km2), following the conventions in Boeing (2017)."
    )
    pdf.body(
        "The network is non-planar (networkx is_planar() returns False on the simplified undirected "
        "graph). Within this bbox OSM records contain concrete grade-separated crossings: "
        "rail-over-road around the Leeds station throat (where the station's western and eastern "
        "approaches pass over streets such as Neville Street and Swinegate) and road bridges "
        "spanning the River Aire at the southern edge of the cell. At each such crossing two edges "
        "physically cross without sharing a node, violating the condition that edges may only meet "
        "at endpoints and forcing the graph to contain a K3,3 or K5 minor (Barthelemy, 2011, "
        "characterises transport networks as 'approximately planar' for this reason - they fail "
        "strict planarity whenever grade separation exists). My code returns the boolean result "
        "rather than enumerating the offending edge pairs; the practical implication is that "
        "planarity-dependent algorithms cannot be applied to real urban road networks without "
        "first resolving these crossings."
    )

    pdf.section_title("Intersection Type Distribution", 3)
    pdf.body(
        "The intersection type distribution reveals the road hierarchy within the selected area. "
        "Of 266 nodes, 176 (66.2%) are three-way intersections (T-junctions), 43 (16.2%) are "
        "four-way crossroads, and 31 (11.7%) are dead-ends or cul-de-sacs. Only 2 nodes (0.8%) have "
        "five-way connections, typically roundabouts or complex junctions. The average streets-per-node "
        "of 2.89 is typical of a British city centre with a mix of through-roads and residential "
        "cul-de-sacs. The dominance of T-junctions over crossroads reflects the historical, organic "
        "growth pattern of Leeds rather than a planned grid layout."
    )

    # ── Task B ───────────────────────────────────────────────
    pdf.check_space(30)
    pdf.section_title("Task B: Road Accident Analysis", 2)

    pdf.body(
        "851 accidents from 2009-2016 were filtered to the selected 1 km square, snapped to the road "
        "network using spaghetti, and analysed for spatial clustering using network-constrained methods."
    )

    pdf.section_title("Network K-function", 3)
    pdf.body(
        "The network-constrained K-function (computed via spaghetti.GlobalAutoK with 39 permutations) "
        "exceeds the upper simulation envelope at 11 of 12 distance steps, with a maximum gap of 5,856 "
        "above the envelope. This provides strong evidence that accidents are significantly clustered "
        "along the network, rejecting the null hypothesis of complete spatial randomness. Following "
        "Yamada and Thill (2004), I use the network K-function rather than the planar version, as the "
        "latter tends to over-detect clusters by comparing against randomness in 2D space rather than "
        "along the constrained network."
    )

    pdf.check_space(55)
    pdf.add_figures_2up(
        fig("part2_taskB/figures/network_k_function.png"),
        fig("part2_taskB/figures/accidents_on_network.png"),
        "Figure 7: Left - Network K-function (blue) vs simulation envelope. Observed K exceeds the "
        "upper envelope at nearly all distance scales. Right - Accident locations (red) on the road "
        "network, showing visible clustering along certain corridors.",
    )

    pdf.section_title("Moran's I", 3)
    pdf.body(
        "Global Moran's I computed on edge-level accident counts with fuzzy contiguity weights yields "
        "I = 0.301 (z = 10.48, p < 0.001, permutation p = 0.002). This indicates significant positive "
        "spatial autocorrelation: edges with high accident counts tend to be adjacent to other "
        "high-accident edges. Together with the K-function results, this confirms that accident risk "
        "is not uniformly distributed but concentrated in persistent hotspots. One single road segment "
        "accumulated 45 accidents across the 8-year period."
    )

    pdf.body(
        "The K-function and Moran's I provide converging evidence from complementary perspectives: "
        "point-level clustering and edge-level autocorrelation both strongly reject spatial randomness. "
        "The K-function's maximum gap above the envelope occurs at intermediate distance scales, "
        "suggesting clustering is most pronounced at corridor level (Xie & Yan, 2008), while "
        "Moran's I = 0.301 confirms that adjacent edges share similar accident intensities, forming "
        "extended hazard zones rather than isolated hotspots."
    )

    pdf.section_title("Implications for Road Safety", 3)
    pdf.body(
        "The combined K-function and Moran's I results have direct implications for road safety "
        "interventions. The persistence of hotspots across 8 years (2009-2016) suggests these are "
        "not random fluctuations but structural features of the road network that create sustained "
        "risk. Targeted interventions at the highest-accident edges (one segment accumulated 45 "
        "accidents over the period) would have disproportionate impact. The spatial autocorrelation "
        "(Moran's I = 0.30) suggests that adjacent segments share risk factors, possibly due to "
        "shared road design characteristics, traffic volumes, or land use patterns."
    )

    pdf.section_title("Distance from Intersections", 3)
    pdf.body(
        "The distribution of accident distances to the nearest intersection is strongly left-skewed "
        f"(median {float(intersection_stats['median_distance_m']):.1f} m, "
        f"mean {float(intersection_stats['mean_distance_m']):.1f} m, "
        f"P90 = {float(intersection_stats['p90_distance_m']):.1f} m), indicating that accidents disproportionately "
        "occur near intersections. This is consistent with road safety literature: intersections create "
        "conflict points where vehicles, pedestrians, and cyclists interact, increasing accident risk "
        "through turning movements, signal violations, and pedestrian crossings. The rapid drop-off "
        "beyond 70 m suggests that mid-block accidents are comparatively rare in this urban area. "
        "Normalising by host edge length, the median accident occurs at about 16% of the segment "
        "length from the nearest intersection (mean 20%), so a typical accident sits in the first "
        "sixth of a road segment - close to an intersection not only in absolute metres but also "
        "as a fraction of road length."
    )

    pdf.check_space(45)
    pdf.add_figure(
        fig("part2_taskB/figures/distance_to_intersection_hist.png"),
        "Figure 8: Distribution of accident position along edges relative to the nearest intersection. "
        "The strong left skew confirms that accidents cluster near intersections.",
        width=CONTENT_W * 0.65,
    )

    # ── Task C ───────────────────────────────────────────────
    pdf.check_space(30)
    pdf.section_title("Task C: Network Voronoi and Marathon Routing", 2)

    pdf.body(
        "For this task I use a city-wide Leeds road network downloaded via osmnx "
        "(graph_from_place, network_type='drive'), projected to BNG (EPSG:27700) for accurate "
        "distance calculations. This yields a substantially larger network than the 1 km square "
        "used in Tasks A-B, as required to route approximately 42 km marathon paths."
    )

    pdf.section_title("Seed Point Selection", 3)
    pdf.body(
        "Four seed points were selected from major intersections (street_count >= 3), one per city "
        "quadrant, prioritising distance from the Task A/B accident hotspot (minimum 2.5 km) and "
        "intersection connectivity. Seeds are placed in the north-west, north-east, south-west, and "
        "south-east quadrants to ensure spatial coverage."
    )

    pdf.section_title("Voronoi Type Comparison", 3)
    pdf.body(
        "I implement three spatial partitioning methods as required by the coursework:"
    )
    pdf.body(
        "(1) Edge planar (Euclidean): assigns each node to the nearest seed by straight-line distance. "
        "Simple to compute but ignores road network topology. A node separated from a seed by an "
        "impassable barrier would be incorrectly assigned. "
        "(2) Node network: assigns nodes by shortest-path network distance via Dijkstra's algorithm. "
        "More accurate as it respects road connectivity, but only partitions nodes, leaving inter-cell "
        "edges unassigned. "
        "(3) Edge-point network (midpoint approximation): assigns each edge to the seed with the "
        "smallest network distance to the edge midpoint, approximated as min(d(seed, u), d(seed, v)) + "
        "L/2. This is the most complete partition as every road segment is assigned to a cell, though "
        "it assigns whole edges atomically rather than splitting edges at Voronoi boundaries."
    )
    pdf.body(
        "For marathon routing, the edge-point method is most appropriate because runners traverse "
        "roads, not just intersections. While the midpoint approximation does not split edges at exact "
        "Voronoi boundaries (as in Okabe et al., 2008), it provides a practical partition for route "
        "planning where whole-edge assignment suffices. Okabe et al. (2000, 2008) provide the "
        "theoretical foundation for exact network Voronoi diagrams."
    )

    # Voronoi cell table
    col_w4 = [CONTENT_W * f for f in [0.20, 0.20, 0.20, 0.20, 0.20]]
    pdf.table_row(["Seed", "Quadrant", "Planar", "Node Net.", "Edge-Pt"], col_w4, bold=True)
    pdf.table_row(["Seed_1", "NW", "2,199", "2,368", "2,758"], col_w4)
    pdf.table_row(["Seed_2", "NE", "2,031", "2,076", "2,389"], col_w4)
    pdf.table_row(["Seed_3", "SW", "19,797", "20,523", "24,773"], col_w4)
    pdf.table_row(["Seed_4", "SE", "7,573", "6,633", "7,735"], col_w4)

    pdf.ln(2)
    pdf.body(
        "The cell imbalance is extreme: Seed_3 (south-west) owns 65.5% of the city network. This "
        "is not a flaw but an insight. Seed_3 is closest to Leeds city centre, which has the densest "
        "road network. The network Voronoi reveals that equal spatial coverage does not equal equal "
        "network coverage. The planar vs network difference is also instructive: Seed_3 gains 726 "
        "additional nodes in the network assignment, reflecting that city-centre road density makes it "
        "effectively 'closer' by road than by straight line."
    )

    pdf.section_title("Marathon Routes", 3)

    col_w5 = [CONTENT_W * f for f in [0.17, 0.25, 0.22, 0.22, 0.14]]
    pdf.table_row(["Seed", "Length", "Gap", "Status", "Loops"], col_w5, bold=True)
    for seed_label in ["Seed_1", "Seed_2", "Seed_3", "Seed_4"]:
        route = marathon_routes[seed_label]
        pdf.table_row(
            [
                seed_label,
                fmt_km(float(route["route_length_m"])),
                fmt_gap_km(float(route["target_gap_m"])),
                route["status"].replace("_", " ").title().replace("Approximate", "Approx."),
                route["loop_count"],
            ],
            col_w5,
        )

    pdf.ln(2)
    pdf.body(
        "Routes are constructed as out-and-back loops from each seed within its Voronoi "
        "cell, allowing edge revisits. The heuristic selects target nodes at various distances from "
        "the seed, evaluates combinations of round-trip loops, and selects the combination closest "
        "to 42.195 km. Three of four seeds achieve routes within the 5% tolerance. Seed_4 overshoots "
        f"by {float(marathon_routes['Seed_4']['target_gap_m']) / 42195 * 100:.1f}%, a limitation of the greedy heuristic's discrete loop-combination search where the "
        "available loop lengths in that cell do not combine to precisely match the target."
    )
    pdf.body(
        "Finding an exact Hamiltonian circuit of precisely 42 km in a subgraph is NP-hard in general. "
        "My heuristic approach is a practical approximation consistent with the coursework's "
        "'approximately 42 km' specification. The approach allows edge revisits, which is realistic "
        "for marathon route planning: real marathon courses frequently double back on sections of road. "
        "The out-and-back structure also ensures all routes are circular (start and end at the seed), "
        "which is a standard requirement for marathon courses."
    )
    pdf.body(
        "For coursework step 5, I chose to allow routes to cross Voronoi cell boundaries slightly by "
        "expanding each seed's Voronoi cell by one graph-neighbourhood hop and rerunning the route "
        f"search. The rerun improves three cells: Seed_1 becomes {fmt_km(float(marathon_routes_refined['Seed_1']['route_length_m']))}, "
        f"Seed_2 becomes {fmt_km(float(marathon_routes_refined['Seed_2']['route_length_m']))}, "
        f"and Seed_3 becomes {fmt_km(float(marathon_routes_refined['Seed_3']['route_length_m']))}. "
        "Seed_4 also improves structurally, but in the opposite direction: "
        f"its route shortens from {fmt_km(float(marathon_routes['Seed_4']['route_length_m']))} "
        f"to {fmt_km(float(marathon_routes_refined['Seed_4']['route_length_m']))} and remains outside the 5% tolerance. This rerun "
        "shows that local cell geometry, not just the route heuristic, is the limiting factor for Seed_4."
    )

    pdf.section_title("Implications for Event Planning", 3)
    pdf.body(
        "The Voronoi partition combined with marathon routing demonstrates a practical methodology "
        "for dividing a city into service areas for distributed events. The extreme cell imbalance "
        "(Seed_3 owns 65% of the network) highlights that naive spatial partitioning would create "
        "unequal experiences for participants in different quadrants. Runners in the north-east "
        "(Seed_2's cell, 2,389 edges) face a much more constrained route choice than runners in the "
        "south-west (Seed_3's cell, 24,773 edges). This has practical implications: event organisers "
        "should consider network density when placing aid stations and selecting route options."
    )
    pdf.body(
        "The seed selection criterion of avoiding accident hotspots (minimum 2.5 km distance) is "
        "also practically motivated. Marathon routes passing through high-accident road segments "
        "would require additional safety measures and road closures. By integrating the Task B "
        "accident analysis with the Task C route planning, I demonstrate how network analysis can "
        "inform evidence-based event planning decisions."
    )

    pdf.check_space(80)
    pdf.add_figure(
        fig("part2_taskC/figures/leeds_voronoi_marathon_map.png"),
        "Figure 9: Leeds city network partitioned into four Voronoi cells (midpoint approximation) with "
        "marathon routes overlaid (bold lines). Cell colours correspond to seed assignments. The "
        "south-west cell (teal) dominates due to the dense city-centre road network.",
        width=CONTENT_W * 0.80,
    )

    # ══════════════════════════════════════════════════════════
    # REFERENCES
    # ══════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("References")

    refs = [
        "Barabasi, A.-L. & Albert, R. (1999) 'Emergence of scaling in random networks.' Science, 286, pp. 509-512.",
        "Barthelemy, M. (2011) 'Spatial networks.' Physics Reports, 499, pp. 1-101.",
        "Boeing, G. (2017) 'OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks.' Computers, Environment and Urban Systems, 65, pp. 126-139.",
        "Brandes, U., Kenis, P., Lerner, J. & van Raaij, D. (2009) 'Network analysis of collaboration structure in Wikipedia.' Proceedings of WWW 2009, pp. 731-740.",
        "Clauset, A., Shalizi, C.R. & Newman, M.E.J. (2009) 'Power-law distributions in empirical data.' SIAM Review, 51(4), pp. 661-703.",
        "Cheng, J., Danescu-Niculescu-Mizil, C. & Leskovec, J. (2017) 'Anyone can become a troll: Causes of trolling behavior in online discussions.' Proceedings of CSCW 2017.",
        "Del Vicario, M. et al. (2016) 'The spreading of misinformation online.' PNAS, 113(3), pp. 554-559.",
        "Kempe, D., Kleinberg, J. & Tardos, E. (2003) 'Maximizing the spread of influence through a social network.' Proceedings of KDD 2003, pp. 137-146.",
        "Massa, P. (2011) 'Social networks of Wikipedia.' Proceedings of the 22nd ACM Conference on Hypertext and Hypermedia.",
        "Okabe, A., Boots, B., Sugihara, K. & Chiu, S.N. (2000) Spatial Tessellations: Concepts and Applications of Voronoi Diagrams. 2nd ed. Wiley.",
        "Okabe, A. et al. (2008) 'Generalized network Voronoi diagrams: Concepts, computational methods, and applications.' IJGIS, 22(9), pp. 965-984.",
        "Okabe, A., Satoh, T. & Sugihara, K. (2006) 'SANET: A toolbox for spatial analysis on a network.' Geographical Analysis, 38(1), pp. 57-66.",
        "Piscopo, A. et al. (2024) 'Talking Wikidata: Communication patterns and their impact on community engagement in collaborative knowledge graphs.' TGDK, 3(1).",
        "Watts, D.J. & Strogatz, S.H. (1998) 'Collective dynamics of small-world networks.' Nature, 393, pp. 440-442.",
        "Xie, Z. & Yan, J. (2008) 'Kernel density estimation of traffic accidents in a network space.' CEUS, 32(5), pp. 396-406.",
        "Yamada, I. & Thill, J.-C. (2004) 'Comparison of planar and network K-functions in traffic accident analysis.' Journal of Transport Geography, 12, pp. 149-158.",
    ]
    for ref in refs:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(CONTENT_W, 4.8, ref)
        pdf.ln(2.5)

    # ── Save ─────────────────────────────────────────────────
    output_path = REPORT_DIR / "K25120780_7CUSMNDA_Coursework.pdf"
    pdf.output(str(output_path))
    return output_path


if __name__ == "__main__":
    path = build_report()
    total_pages = path.stat().st_size  # rough check
    print(f"Report generated: {path}")
    print(f"File size: {total_pages / 1024:.1f} KB")
