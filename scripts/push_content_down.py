"""Push everything except the title/subtitle down to add space below the header."""
import json
from pathlib import Path

FILE = Path("docs/architecture.excalidraw")
TITLE_IDS = {"title", "subtitle"}
PUSH = 40  # extra px below title


def main() -> None:
    data = json.loads(FILE.read_text())
    for el in data["elements"]:
        if el.get("id") not in TITLE_IDS:
            el["y"] += PUSH
    FILE.write_text(json.dumps(data, indent=2))
    print(f"Pushed content down {PUSH}px below title")


if __name__ == "__main__":
    main()
