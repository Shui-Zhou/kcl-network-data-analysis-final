# Network Data Analysis Coursework (7CUSMNDA)

Final submission for the MSc Network Data Analysis coursework, King's College London.

## Layout

- `Analysis/part1_task[A-C]_*.py` — scripts for Part 1 (Wikidata editor co-comment networks)
- `Analysis/part2_task[A-C]_*.py` — scripts for Part 2 (Leeds road network, accidents, marathon routing)
- `Analysis/outputs/` — per-task figures, tables, JSON summaries consumed by the report
- `report/generate_report.py` — builds the final PDF via fpdf2
- `report/K25120780_7CUSMNDA_Coursework.pdf` — submitted report

## Reproducing

Run scripts from the project root, in order within each Part. Later tasks read pickle graphs saved by Task A, so Task A must run first.

Part 1:
```
python3 Analysis/part1_taskA_network_construction.py
python3 Analysis/part1_taskB_network_metrics.py
python3 Analysis/part1_taskC_propagation_model.py
```

Part 2:
```
python3 Analysis/part2_taskA_spatial_network.py
python3 Analysis/part2_taskB_accident_analysis.py
python3 Analysis/part2_taskC_marathon_route.py
```

Report:
```
python3 report/generate_report.py
```

Part 1 expects the three Wikidata CSVs in `Assessment/Part1_Data/datasets/` (`REQUEST_FOR_DELETION`, `PROPERTY_PROPOSAL`, `BOT_REQUESTS`). Part 2 expects the Leeds shapefiles and accident spreadsheets in `Assessment/Part2_Data/`. Raw data is not redistributed here — paths match the coursework materials.

Part 2 Task A downloads the Leeds drive network via OSMnx on first run (internet required); subsequent runs reuse the cached graph in `Analysis/outputs/part2_taskA/graphs/`.

## Dependencies

Python 3.10+. See `requirements.txt`.
