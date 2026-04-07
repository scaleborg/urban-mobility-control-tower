"""Expand component box heights and push subtitles down for breathing room."""
import json
from pathlib import Path

FILE = Path("docs/architecture.excalidraw")
ZONE_IDS = {"z1", "z2", "z3", "z4", "z5"}
SUBTITLE_IDS = {"s_gbfs", "s_ingest", "s_pg", "s_dbz", "s_kc", "s_flink", "s_km", "s_duck", "s_dbt", "s_api"}
EXPAND = 8


def main() -> None:
    data = json.loads(FILE.read_text())
    els = data["elements"]

    for el in els:
        # Expand non-zone rectangles
        if el["type"] == "rectangle" and el["id"] not in ZONE_IDS:
            el["height"] += EXPAND
        # Push subtitles down
        if el.get("id") in SUBTITLE_IDS:
            el["y"] += EXPAND

    FILE.write_text(json.dumps(data, indent=2))
    print(f"Expanded boxes by {EXPAND}px and shifted subtitles in {FILE}")


if __name__ == "__main__":
    main()
