# Part 2 Task C Summary

## Seed Points

|   rank |    node_id | label   |      x |      y |   street_count |   distance_to_hotspot_m | quadrant   |
|-------:|-----------:|:--------|-------:|-------:|---------------:|------------------------:|:-----------|
|      1 |   27563083 | Seed_1  | 419098 | 446398 |              4 |                 17215.4 | north_west |
|      2 |  764416147 | Seed_2  | 443320 | 445958 |              5 |                 17876.5 | north_east |
|      3 |  448707924 | Seed_3  | 420282 | 433694 |              4 |                 10219.6 | south_west |
|      4 | 1329998313 | Seed_4  | 444437 | 432697 |              4 |                 13960.5 | south_east |

## Voronoi Strategy Counts

### Planar nearest-seed node counts

| owner   |   node_count |
|:--------|-------------:|
| Seed_3  |        19797 |
| Seed_4  |         7573 |
| Seed_1  |         2199 |
| Seed_2  |         2031 |

### Node-network nearest-seed node counts

| owner   |   node_count |
|:--------|-------------:|
| Seed_3  |        20523 |
| Seed_4  |         6633 |
| Seed_1  |         2368 |
| Seed_2  |         2076 |

### Edge-point (midpoint network-distance approximation) edge counts

| owner   |   edge_count |
|:--------|-------------:|
| Seed_3  |        24773 |
| Seed_4  |         7735 |
| Seed_1  |         2758 |
| Seed_2  |         2389 |

## Marathon Route Attempts

| seed_label   |   seed_node_id | status      |   route_length_m |   target_gap_m |   loop_count |   cell_nodes |   cell_edges |
|:-------------|---------------:|:------------|-----------------:|---------------:|-------------:|-------------:|-------------:|
| Seed_1       |       27563083 | success     |          44260.1 |        2065.14 |            2 |         2384 |         2758 |
| Seed_2       |      764416147 | success     |          44215.5 |        2020.54 |            2 |         2096 |         2389 |
| Seed_3       |      448707924 | success     |          43984.6 |        1789.56 |            2 |        20563 |        24773 |
| Seed_4       |     1329998313 | approximate |          46508.3 |        4313.25 |            2 |         6657 |         7735 |

## Step 5 Rerun: Slight Boundary Relaxation

Chosen option: allow routes to cross cell boundaries slightly by expanding each edge-point cell to include one graph-neighbourhood hop beyond its original nodes, then repeat the route search.

| seed_label   |   seed_node_id | status      |   route_length_m |   target_gap_m |   loop_count |   cell_nodes |   cell_edges | rerun_option                   |
|:-------------|---------------:|:------------|-----------------:|---------------:|-------------:|-------------:|-------------:|:-------------------------------|
| Seed_1       |       27563083 | success     |          42972.2 |        777.205 |            2 |         2427 |         2815 | allow_slight_boundary_crossing |
| Seed_2       |      764416147 | success     |          44176   |       1981.04  |            2 |         2135 |         2438 | allow_slight_boundary_crossing |
| Seed_3       |      448707924 | success     |          42916.3 |        721.334 |            1 |        20652 |        24898 | allow_slight_boundary_crossing |
| Seed_4       |     1329998313 | approximate |          39331.5 |      -2863.53  |            1 |         6721 |         7820 | allow_slight_boundary_crossing |

## Output artifacts

- `figures/leeds_voronoi_marathon_map.png`
- `figures/leeds_voronoi_marathon_refined_map.png`
- `tables/seed_nodes.csv`
- `tables/marathon_routes.csv`
- `tables/marathon_routes_refined.csv`
