# Part 1 Task C Summary

## Plausibility Summary

| dataset              | infected_a   | infected_b   |   component_size |   component_share |   shortest_path_between_infected |   mean_infected_degree |   mean_infected_weighted_degree |   mean_infected_local_clustering | verdict                   |
|:---------------------|:-------------|:-------------|-----------------:|------------------:|---------------------------------:|-----------------------:|--------------------------------:|---------------------------------:|:--------------------------|
| BOT_REQUESTS         | Hanira       | Scott5114    |              519 |          0.940217 |                                3 |                    3   |                             3   |                         1        | plausible_non_propagation |
| PROPERTY_PROPOSAL    | Ipoellet     | ThelmOSO     |             3051 |          0.997711 |                                2 |                    7.5 |                             9   |                         0.967949 | mixed_risk                |
| REQUEST_FOR_DELETION | Defender     | Elyparker    |             9870 |          0.993457 |                                3 |                    2   |                             4.5 |                         0.5      | plausible_non_propagation |

## Priority Ranking Preview

| dataset              | scenario     |   rank | username               |   min_shortest_path_to_infected |   direct_shared_context_count |   infected_neighbor_count |   degree_centrality |   priority_score |
|:---------------------|:-------------|-------:|:-----------------------|--------------------------------:|------------------------------:|--------------------------:|--------------------:|-----------------:|
| BOT_REQUESTS         | one_infected |      1 | Yamaha5                |                               1 |                             1 |                         1 |           0.0173745 |          6.51737 |
| BOT_REQUESTS         | one_infected |      2 | Emaus                  |                               1 |                             1 |                         1 |           0.015444  |          6.51544 |
| BOT_REQUESTS         | one_infected |      3 | Pasleim                |                               2 |                             0 |                         0 |           0.436293  |          1.76963 |
| BOT_REQUESTS         | one_infected |      4 | Jura1                  |                               2 |                             0 |                         0 |           0.382239  |          1.71557 |
| BOT_REQUESTS         | one_infected |      5 | Matěj Suchánek         |                               2 |                             0 |                         0 |           0.293436  |          1.62677 |
| BOT_REQUESTS         | one_infected |      6 | ValterVB               |                               2 |                             0 |                         0 |           0.189189  |          1.52252 |
| BOT_REQUESTS         | one_infected |      7 | Multichill             |                               2 |                             0 |                         0 |           0.158301  |          1.49163 |
| BOT_REQUESTS         | one_infected |      8 | Ricordisamoa           |                               2 |                             0 |                         0 |           0.131274  |          1.46461 |
| BOT_REQUESTS         | one_infected |      9 | Nikki                  |                               2 |                             0 |                         0 |           0.102317  |          1.43565 |
| BOT_REQUESTS         | one_infected |     10 | GZWDer                 |                               2 |                             0 |                         0 |           0.0907336 |          1.42407 |
| BOT_REQUESTS         | two_infected |      1 | Ricordisamoa           |                               1 |                             1 |                         1 |           0.131274  |          6.63127 |
| BOT_REQUESTS         | two_infected |      2 | Docu                   |                               1 |                             1 |                         1 |           0.0849421 |          6.58494 |
| BOT_REQUESTS         | two_infected |      3 | Hazard-SJ              |                               1 |                             1 |                         1 |           0.0559846 |          6.55598 |
| BOT_REQUESTS         | two_infected |      4 | Akkakk                 |                               1 |                             1 |                         1 |           0.0405405 |          6.54054 |
| BOT_REQUESTS         | two_infected |      5 | Yamaha5                |                               1 |                             1 |                         1 |           0.0173745 |          6.51737 |
| BOT_REQUESTS         | two_infected |      6 | Emaus                  |                               1 |                             1 |                         1 |           0.015444  |          6.51544 |
| BOT_REQUESTS         | two_infected |      7 | Pasleim                |                               2 |                             0 |                         0 |           0.436293  |          1.76963 |
| BOT_REQUESTS         | two_infected |      8 | Jura1                  |                               2 |                             0 |                         0 |           0.382239  |          1.71557 |
| BOT_REQUESTS         | two_infected |      9 | Matěj Suchánek         |                               2 |                             0 |                         0 |           0.293436  |          1.62677 |
| BOT_REQUESTS         | two_infected |     10 | ValterVB               |                               2 |                             0 |                         0 |           0.189189  |          1.52252 |
| PROPERTY_PROPOSAL    | one_infected |      1 | Fralambert             |                               1 |                             3 |                         1 |           0.104262  |          9.60426 |
| PROPERTY_PROPOSAL    | one_infected |      2 | ديفيد عادل وهبة خليل 2 |                               1 |                             2 |                         1 |           0.42918   |          8.42918 |
| PROPERTY_PROPOSAL    | one_infected |      3 | ArthurPSmith           |                               1 |                             1 |                         1 |           0.458689  |          6.95869 |
| PROPERTY_PROPOSAL    | one_infected |      4 | Pigsonthewing          |                               1 |                             1 |                         1 |           0.410492  |          6.91049 |
| PROPERTY_PROPOSAL    | one_infected |      5 | Jura1                  |                               1 |                             1 |                         1 |           0.388197  |          6.8882  |
| PROPERTY_PROPOSAL    | one_infected |      6 | Thierry Caro           |                               1 |                             1 |                         1 |           0.283279  |          6.78328 |
| PROPERTY_PROPOSAL    | one_infected |      7 | Nomen ad hoc           |                               1 |                             1 |                         1 |           0.189508  |          6.68951 |
| PROPERTY_PROPOSAL    | one_infected |      8 | Tinker Bell            |                               1 |                             1 |                         1 |           0.17377   |          6.67377 |
| PROPERTY_PROPOSAL    | one_infected |      9 | Mahir256               |                               1 |                             1 |                         1 |           0.170164  |          6.67016 |
| PROPERTY_PROPOSAL    | one_infected |     10 | Epìdosis               |                               1 |                             1 |                         1 |           0.124918  |          6.62492 |
| PROPERTY_PROPOSAL    | two_infected |      1 | Fralambert             |                               1 |                             3 |                         1 |           0.104262  |          9.60426 |
| PROPERTY_PROPOSAL    | two_infected |      2 | ArthurPSmith           |                               1 |                             2 |                         2 |           0.458689  |         11.4587  |
| PROPERTY_PROPOSAL    | two_infected |      3 | Tinker Bell            |                               1 |                             2 |                         2 |           0.17377   |         11.1738  |
| PROPERTY_PROPOSAL    | two_infected |      4 | ديفيد عادل وهبة خليل 2 |                               1 |                             2 |                         1 |           0.42918   |          8.42918 |
| PROPERTY_PROPOSAL    | two_infected |      5 | Pigsonthewing          |                               1 |                             1 |                         1 |           0.410492  |          6.91049 |
| PROPERTY_PROPOSAL    | two_infected |      6 | Jura1                  |                               1 |                             1 |                         1 |           0.388197  |          6.8882  |
| PROPERTY_PROPOSAL    | two_infected |      7 | Thierry Caro           |                               1 |                             1 |                         1 |           0.283279  |          6.78328 |
| PROPERTY_PROPOSAL    | two_infected |      8 | Nomen ad hoc           |                               1 |                             1 |                         1 |           0.189508  |          6.68951 |
| PROPERTY_PROPOSAL    | two_infected |      9 | Mahir256               |                               1 |                             1 |                         1 |           0.170164  |          6.67016 |
| PROPERTY_PROPOSAL    | two_infected |     10 | Epìdosis               |                               1 |                             1 |                         1 |           0.124918  |          6.62492 |
| REQUEST_FOR_DELETION | one_infected |      1 | BeneBot*               |                               1 |                             6 |                         1 |           0.441281  |         14.4413  |
| REQUEST_FOR_DELETION | one_infected |      2 | Cycn                   |                               2 |                             0 |                         0 |           0.122403  |          1.45574 |
| REQUEST_FOR_DELETION | one_infected |      3 | MisterSynergy          |                               2 |                             0 |                         0 |           0.0721451 |          1.40548 |
| REQUEST_FOR_DELETION | one_infected |      4 | Lymantria              |                               2 |                             0 |                         0 |           0.0716385 |          1.40497 |
| REQUEST_FOR_DELETION | one_infected |      5 | Ymblanter              |                               2 |                             0 |                         0 |           0.0648495 |          1.39818 |
| REQUEST_FOR_DELETION | one_infected |      6 | 분당선M                |                               2 |                             0 |                         0 |           0.0640389 |          1.39737 |
| REQUEST_FOR_DELETION | one_infected |      7 | Stryn                  |                               2 |                             0 |                         0 |           0.0521836 |          1.38552 |
| REQUEST_FOR_DELETION | one_infected |      8 | Mbch331                |                               2 |                             0 |                         0 |           0.051069  |          1.3844  |
| REQUEST_FOR_DELETION | one_infected |      9 | Jura1                  |                               2 |                             0 |                         0 |           0.050461  |          1.38379 |
| REQUEST_FOR_DELETION | one_infected |     10 | Wiki13                 |                               2 |                             0 |                         0 |           0.0456987 |          1.37903 |
| REQUEST_FOR_DELETION | two_infected |      1 | BeneBot*               |                               1 |                             6 |                         1 |           0.441281  |         14.4413  |
| REQUEST_FOR_DELETION | two_infected |      2 | DeltaBot               |                               1 |                             1 |                         1 |           0.500557  |          7.00056 |
| REQUEST_FOR_DELETION | two_infected |      3 | MisterSynergy          |                               1 |                             1 |                         1 |           0.0721451 |          6.57215 |
| REQUEST_FOR_DELETION | two_infected |      4 | Peter James            |                               1 |                             1 |                         1 |           0.0355659 |          6.53557 |
| REQUEST_FOR_DELETION | two_infected |      5 | Cycn                   |                               2 |                             0 |                         0 |           0.122403  |          1.45574 |
| REQUEST_FOR_DELETION | two_infected |      6 | Lymantria              |                               2 |                             0 |                         0 |           0.0716385 |          1.40497 |
| REQUEST_FOR_DELETION | two_infected |      7 | Ymblanter              |                               2 |                             0 |                         0 |           0.0648495 |          1.39818 |
| REQUEST_FOR_DELETION | two_infected |      8 | 분당선M                |                               2 |                             0 |                         0 |           0.0640389 |          1.39737 |
| REQUEST_FOR_DELETION | two_infected |      9 | Quakewoody             |                               2 |                             0 |                         0 |           0.0577566 |          1.39109 |
| REQUEST_FOR_DELETION | two_infected |     10 | Stryn                  |                               2 |                             0 |                         0 |           0.0521836 |          1.38552 |

## Simulation Summary

| dataset              |   step |   infected_mean |   infected_p90 |   recovered_mean |   susceptible_mean |
|:---------------------|-------:|----------------:|---------------:|-----------------:|-------------------:|
| BOT_REQUESTS         |      0 |           2     |            2   |            0     |            517     |
| BOT_REQUESTS         |      1 |           2.332 |            4   |            0.612 |            516.056 |
| BOT_REQUESTS         |      2 |           7.34  |           18.1 |            1.332 |            510.328 |
| BOT_REQUESTS         |      3 |          45.928 |          111   |            3.432 |            469.64  |
| BOT_REQUESTS         |      4 |         129.768 |          231   |           17.076 |            372.156 |
| BOT_REQUESTS         |      5 |         181.096 |          245.1 |           56.088 |            281.816 |
| BOT_REQUESTS         |      6 |         183.996 |          241   |          110.744 |            224.26  |
| PROPERTY_PROPOSAL    |      0 |           2     |            2   |            0     |           3049     |
| PROPERTY_PROPOSAL    |      1 |           3.584 |            6   |            0.616 |           3046.8   |
| PROPERTY_PROPOSAL    |      2 |         372.884 |          662.8 |            1.668 |           2676.45  |
| PROPERTY_PROPOSAL    |      3 |        1665.84  |         1941   |          112.928 |           1272.23  |
| PROPERTY_PROPOSAL    |      4 |        1731.44  |         1899.3 |          611.584 |            707.98  |
| PROPERTY_PROPOSAL    |      5 |        1413.98  |         1590.3 |         1129.76  |            507.256 |
| PROPERTY_PROPOSAL    |      6 |        1074.52  |         1210   |         1553.27  |            423.208 |
| REQUEST_FOR_DELETION |      0 |           2     |            2   |            0     |           9868     |
| REQUEST_FOR_DELETION |      1 |           2.188 |            3   |            0.564 |           9867.25  |
| REQUEST_FOR_DELETION |      2 |         846.824 |         1611   |            1.248 |           9021.93  |
| REQUEST_FOR_DELETION |      3 |        1712.35  |         3001.2 |          255.384 |           7902.26  |
| REQUEST_FOR_DELETION |      4 |        2303.28  |         3256.2 |          769.632 |           6797.09  |
| REQUEST_FOR_DELETION |      5 |        2271.06  |         3052.2 |         1458.44  |           6140.5   |
| REQUEST_FOR_DELETION |      6 |        2003.23  |         2757.9 |         2141.54  |           5725.23  |

## Verdict Labels

- `plausible_non_propagation`: infected editors are separated enough and locally sparse enough that lack of spread is believable.
- `mixed_risk`: some local spread risk exists, but the structure does not force a large cascade.
- `non_propagation_less_plausible`: the infected editors sit in highly connected local structure, so absence of spread is harder to defend.
