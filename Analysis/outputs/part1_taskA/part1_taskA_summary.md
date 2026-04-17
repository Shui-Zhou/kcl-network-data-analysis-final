# Part 1 Task A Summary

## Graph Summary

| dataset              | size_label   |   rows |   unique_users |   unique_pages |   unique_threads |   unique_page_thread_groups |   max_users_in_group |   median_users_in_group |   nodes |   edges |   density |   average_degree |   median_degree |   max_degree |   connected_components |   largest_component_size |   largest_component_share |   isolated_nodes |   mean_edge_weight |   max_edge_weight |   build_runtime_seconds |
|:---------------------|:-------------|-------:|---------------:|---------------:|-----------------:|----------------------------:|---------------------:|------------------------:|--------:|--------:|----------:|-----------------:|----------------:|-------------:|-----------------------:|-------------------------:|--------------------------:|-----------------:|-------------------:|------------------:|------------------------:|
| REQUEST_FOR_DELETION | large        | 648637 |           9935 |           3303 |           316267 |                      318883 |                   21 |                       2 |    9935 |   33497 |    0.0007 |           6.7432 |               1 |         4940 |                     57 |                     9870 |                    0.9935 |               48 |            10.5831 |             14325 |                  1.7611 |
| PROPERTY_PROPOSAL    | medium       |  52160 |           3058 |           8649 |            10005 |                       10018 |                   42 |                       5 |    3058 |   46154 |    0.0099 |          30.1857 |              11 |         1399 |                      8 |                     3051 |                    0.9977 |                7 |             3.1627 |              1992 |                  0.2399 |
| BOT_REQUESTS         | small        |   2981 |            552 |            108 |             1113 |                        1126 |                   18 |                       2 |     552 |    2424 |    0.0159 |           8.7826 |               3 |          226 |                     29 |                      519 |                    0.9402 |               25 |             1.5611 |                64 |                  0.0194 |

## Output Files

- `tables/dataset_profiles.csv`
- `tables/graph_summary.csv`
- `figures/*_degree_distribution.png`
- `figures/BOT_REQUESTS_network.png`
