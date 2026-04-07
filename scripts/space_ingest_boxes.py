"""Add vertical spacing between INGEST column boxes and expand zone to fit."""
import json
from pathlib import Path

FILE = Path("docs/architecture.excalidraw")
GAP = 40  # extra px between each box


def shift_element(by_id, eid, dy):
    """Shift an element and its title/subtitle down by dy."""
    el = by_id[eid]
    el["y"] += dy


def main() -> None:
    data = json.loads(FILE.read_text())
    by_id = {e["id"]: e for e in data["elements"]}

    # Shift Ingest Service + its labels down
    for eid in ("ingest_svc", "t_ingest", "s_ingest"):
        shift_element(by_id, eid, GAP)

    # Shift Postgres + its labels down (2x gap since it's the third box)
    for eid in ("postgres", "t_pg", "s_pg"):
        shift_element(by_id, eid, GAP * 2)

    # Also shift arrows and labels that connect within INGEST
    # a1 (gbfs->ingest): push start down slightly, end down by GAP
    by_id["a1"]["points"][1][1] += GAP  # arrow gets longer
    by_id["a1"]["height"] += GAP

    # a2 (ingest->postgres): shift start and end down
    by_id["a2"]["y"] += GAP
    by_id["a2"]["points"][1][1] += GAP
    by_id["a2"]["height"] += GAP
    by_id["a2l"]["y"] += GAP

    # a3 (postgres->debezium): shift down
    by_id["a3"]["y"] += GAP * 2
    by_id["a3l"]["y"] += GAP * 2

    # Expand INGEST zone height to fit
    by_id["z1"]["height"] += GAP * 2

    FILE.write_text(json.dumps(data, indent=2))
    print(f"Added {GAP}px spacing between INGEST boxes")


if __name__ == "__main__":
    main()
