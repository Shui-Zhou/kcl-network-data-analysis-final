# Network Data Analysis Coursework (7CUSMNDA)

Final submission for the MSc Network Data Analysis coursework, King's College London.

## Layout

- `Analysis/part1_task[A-C]_*.py` — scripts for Part 1 (Wikidata editor co-comment networks)
- `Analysis/part2_task[A-C]_*.py` — scripts for Part 2 (Leeds road network, accidents, marathon routing)
- `Analysis/outputs/` — per-task figures, tables, JSON summaries consumed by the report
- `report/generate_report.py` — builds the final PDF via fpdf2
- `report/NDA_Coursework_Report.pdf` — submitted report

## Reproducing

Each script is standalone and run from the project root, e.g.:

```
python3 Analysis/part1_taskA_network_construction.py
python3 Analysis/part2_taskA_spatial_network.py
python3 report/generate_report.py
```

Part 1 expects the three Wikidata CSVs in `Assessment/Part1_Data/datasets/` (`REQUEST_FOR_DELETION`, `PROPERTY_PROPOSAL`, `BOT_REQUESTS`). Part 2 expects the Leeds shapefiles and accident spreadsheets in `Assessment/Part2_Data/`. Raw data is not redistributed here — paths match the coursework materials.

Part 2 Task A caches the OSMnx download of the Leeds drive network; first run needs internet access, subsequent runs reuse `Analysis/outputs/part2_taskA/graphs/`.

## Dependencies

Python 3.10+. Main libraries: `networkx`, `osmnx` 2.x, `spaghetti`, `libpysal`, `esda`, `pandas`, `numpy`, `matplotlib`, `pyproj`, `fpdf2`.
