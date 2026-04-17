# Part 2 Task B Summary

## Accident subset

|   accidents_in_square | years_covered   |   unique_edges_with_accidents |   max_accidents_on_single_edge |   mean_accidents_per_edge |
|----------------------:|:----------------|------------------------------:|-------------------------------:|--------------------------:|
|                   851 | 2009-2016       |                           173 |                             45 |                   1.90807 |

## Network K-function

|   observed_exceeds_upper_steps |   max_gap_over_upper |
|-------------------------------:|---------------------:|
|                             11 |              5855.14 |

## Moran's I

|   moran_i |   expected_i |   z_score |     p_value |   permutation_p_value |
|----------:|-------------:|----------:|------------:|----------------------:|
|   0.30067 |  -0.00224719 |   10.4801 | 1.06683e-25 |                 0.002 |

## Distance from intersections

|   mean_distance_m |   median_distance_m |   p90_distance_m |   mean_edge_fraction |   median_edge_fraction |
|------------------:|--------------------:|-----------------:|---------------------:|-----------------------:|
|           24.9361 |             11.8841 |          63.3313 |             0.196483 |               0.163298 |

## Output artifacts

- `figures/accidents_on_network.png`
- `figures/network_k_function.png`
- `figures/distance_to_intersection_hist.png`
