# Part 1 Task C Summary

## Scenario Summary

| dataset              |   nodes |   edges |   average_clustering |   transitivity | infected_1       | infected_2   |   same_component_share |   average_finite_distance |   max_finite_distance | plausibility   | interpretation                                                                                                        |   infected_1_degree |   infected_2_degree |   infected_1_degree_centrality |   infected_2_degree_centrality | one_seed_plausibility   |
|:---------------------|--------:|--------:|---------------------:|---------------:|:-----------------|:-------------|-----------------------:|--------------------------:|----------------------:|:---------------|:----------------------------------------------------------------------------------------------------------------------|--------------------:|--------------------:|-------------------------------:|-------------------------------:|:------------------------|
| REQUEST_FOR_DELETION |    9935 |   33497 |             0.391952 |       0.014013 | Doff             | Jr8825       |               0.993457 |                   2.55299 |                     4 | low            | Non-propagation is moderately plausible, but the main component is large enough that spread remains realistic.        |                   3 |                   1 |                    0.000301993 |                    0.000100664 | low                     |
| PROPERTY_PROPOSAL    |    3058 |   46154 |             0.814377 |       0.139433 | Ayoungprogrammer | Faux         |               0.997711 |                   2.24582 |                     3 | low            | Non-propagation is weakly plausible; the graph is dense, clustered, and the infected pair sits in the main component. |                   3 |                  80 |                    0.000981354 |                    0.0261694   | low                     |
| BOT_REQUESTS         |     552 |    2424 |             0.65764  |       0.174522 | Powerek38        | Pyb          |               0.940217 |                   2.40848 |                     4 | moderate       | Non-propagation is weakly plausible; the graph is dense, clustered, and the infected pair sits in the main component. |                   4 |                  10 |                    0.00725953  |                    0.0181488   | moderate                |

## Top Priority Rankings

| dataset              | scenario                      |   rank | username             |   combined_score |   distance_to_infected |   shared_context_weight |   degree_centrality |   distance_score |   shared_score |   degree_score |   same_component |
|:---------------------|:------------------------------|-------:|:---------------------|-----------------:|-----------------------:|------------------------:|--------------------:|-----------------:|---------------:|---------------:|-----------------:|
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      1 | Ymblanter            |         0.700911 |                      1 |                       1 |           0.0644252 |             0.75 |              1 |      0.129555  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      2 | Inkowik              |         0.681842 |                      1 |                       1 |           0.0170123 |             0.75 |              1 |      0.0342105 |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      3 | Bill william compton |         0.681761 |                      1 |                       1 |           0.016811  |             0.75 |              1 |      0.0338057 |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      4 | DeltaBot             |         0.45     |                      2 |                       0 |           0.497282  |             0.5  |              0 |      1         |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      5 | BeneBot*             |         0.426316 |                      2 |                       0 |           0.438393  |             0.5  |              0 |      0.881579  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      6 | Cycn                 |         0.298907 |                      2 |                       0 |           0.121603  |             0.5  |              0 |      0.244534  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      7 | MisterSynergy        |         0.278826 |                      2 |                       0 |           0.071673  |             0.5  |              0 |      0.14413   |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      8 | Lymantria            |         0.278623 |                      2 |                       0 |           0.0711697 |             0.5  |              0 |      0.143117  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |      9 | 분당선M              |         0.275587 |                      2 |                       0 |           0.0636199 |             0.5  |              0 |      0.127935  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |     10 | Quakewoody           |         0.273077 |                      2 |                       0 |           0.0573787 |             0.5  |              0 |      0.115385  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |     11 | Stryn                |         0.27085  |                      2 |                       0 |           0.0518422 |             0.5  |              0 |      0.104251  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |     12 | Mbch331              |         0.270405 |                      2 |                       0 |           0.0507349 |             0.5  |              0 |      0.102024  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |     13 | Jura1                |         0.270162 |                      2 |                       0 |           0.0501309 |             0.5  |              0 |      0.10081   |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |     14 | Wiki13               |         0.268259 |                      2 |                       0 |           0.0453996 |             0.5  |              0 |      0.0912955 |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_one_seed |     15 | Wolverène            |         0.267773 |                      2 |                       0 |           0.0441917 |             0.5  |              0 |      0.0888664 |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      1 | BeneBot*             |         0.851316 |                      1 |                       1 |           0.438393  |             0.75 |              1 |      0.881579  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      2 | Ymblanter            |         0.700911 |                      1 |                       1 |           0.0644252 |             0.75 |              1 |      0.129555  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      3 | Inkowik              |         0.681842 |                      1 |                       1 |           0.0170123 |             0.75 |              1 |      0.0342105 |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      4 | Bill william compton |         0.681761 |                      1 |                       1 |           0.016811  |             0.75 |              1 |      0.0338057 |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      5 | DeltaBot             |         0.45     |                      2 |                       0 |           0.497282  |             0.5  |              0 |      1         |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      6 | Cycn                 |         0.298907 |                      2 |                       0 |           0.121603  |             0.5  |              0 |      0.244534  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      7 | MisterSynergy        |         0.278826 |                      2 |                       0 |           0.071673  |             0.5  |              0 |      0.14413   |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      8 | Lymantria            |         0.278623 |                      2 |                       0 |           0.0711697 |             0.5  |              0 |      0.143117  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |      9 | 분당선M              |         0.275587 |                      2 |                       0 |           0.0636199 |             0.5  |              0 |      0.127935  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |     10 | Quakewoody           |         0.273077 |                      2 |                       0 |           0.0573787 |             0.5  |              0 |      0.115385  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |     11 | Stryn                |         0.27085  |                      2 |                       0 |           0.0518422 |             0.5  |              0 |      0.104251  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |     12 | Mbch331              |         0.270405 |                      2 |                       0 |           0.0507349 |             0.5  |              0 |      0.102024  |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |     13 | Jura1                |         0.270162 |                      2 |                       0 |           0.0501309 |             0.5  |              0 |      0.10081   |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |     14 | Wiki13               |         0.268259 |                      2 |                       0 |           0.0453996 |             0.5  |              0 |      0.0912955 |                1 |
| REQUEST_FOR_DELETION | REQUEST_FOR_DELETION_two_seed |     15 | Wolverène            |         0.267773 |                      2 |                       0 |           0.0441917 |             0.5  |              0 |      0.0888664 |                1 |

## SIR Illustration

|   step |    S |    I |    R | dataset              |
|-------:|-----:|-----:|-----:|:---------------------|
|      0 | 9933 |    2 |    0 | REQUEST_FOR_DELETION |
|      1 | 9931 |    4 |    0 | REQUEST_FOR_DELETION |
|      2 | 6943 | 2991 |    1 | REQUEST_FOR_DELETION |
|      3 | 4155 | 5421 |  359 | REQUEST_FOR_DELETION |
|      4 | 1869 | 7062 | 1004 | REQUEST_FOR_DELETION |
|      5 | 1034 | 7039 | 1862 | REQUEST_FOR_DELETION |
|      6 |  654 | 6565 | 2716 | REQUEST_FOR_DELETION |
|      7 |  455 | 5947 | 3533 | REQUEST_FOR_DELETION |
|      8 |  379 | 5280 | 4276 | REQUEST_FOR_DELETION |
|      0 | 3056 |    2 |    0 | PROPERTY_PROPOSAL    |
|      1 | 3001 |   57 |    0 | PROPERTY_PROPOSAL    |
|      2 | 1636 | 1414 |    8 | PROPERTY_PROPOSAL    |
|      3 |  146 | 2756 |  156 | PROPERTY_PROPOSAL    |
|      4 |   35 | 2553 |  470 | PROPERTY_PROPOSAL    |
|      5 |   20 | 2282 |  756 | PROPERTY_PROPOSAL    |
|      6 |   16 | 2056 |  986 | PROPERTY_PROPOSAL    |
|      7 |   16 | 1832 | 1210 | PROPERTY_PROPOSAL    |
|      8 |   15 | 1628 | 1415 | PROPERTY_PROPOSAL    |
|      0 |  550 |    2 |    0 | BOT_REQUESTS         |
|      1 |  542 |   10 |    0 | BOT_REQUESTS         |
|      2 |  386 |  165 |    1 | BOT_REQUESTS         |
|      3 |  157 |  377 |   18 | BOT_REQUESTS         |
|      4 |   83 |  406 |   63 | BOT_REQUESTS         |
|      5 |   57 |  388 |  107 | BOT_REQUESTS         |
|      6 |   49 |  339 |  164 | BOT_REQUESTS         |
|      7 |   45 |  301 |  206 | BOT_REQUESTS         |
|      8 |   44 |  263 |  245 | BOT_REQUESTS         |

## Figures

- REQUEST_FOR_DELETION_risk_overlay: `figures/request_for_deletion_risk_overlay.png`
- PROPERTY_PROPOSAL_risk_overlay: `figures/property_proposal_risk_overlay.png`
- BOT_REQUESTS_risk_overlay: `figures/bot_requests_risk_overlay.png`
- sir_timeline: `figures/sir_timeline.png`
