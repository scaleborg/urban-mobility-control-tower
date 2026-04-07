"""Update only colors in the architecture diagram. Layout is untouched."""
import json
from pathlib import Path

FILE = Path("docs/architecture.excalidraw")

# Color replacements: old -> new
# More vibrant, higher-contrast palette that reads well on the dark card
STROKE_MAP = {
    # Zone strokes + labels — brighter
    "#22c55e": "#34d399",  # green
    "#f59e0b": "#fbbf24",  # amber
    "#8b5cf6": "#a78bfa",  # purple
    "#06b6d4": "#22d3ee",  # cyan
    "#4a9eed": "#60a5fa",  # blue
}

BG_MAP = {
    # Zone backgrounds — richer
    "#1a4d2e": "#14532d",  # green zone
    "#5c3d1a": "#713f12",  # amber zone
    "#2d1b69": "#3b0764",  # purple zone
    "#1a4d4d": "#134e4a",  # cyan zone
    "#1e3a5f": "#1e3a5f",  # blue zone (keep)
}

TEXT_COLOR_MAP = {
    "#e5e5e5": "#ffffff",  # titles -> pure white
    "#8f9399": "#c9cdd3",  # subtitles -> brighter gray
    "#a0a0a0": "#b8bcc2",  # arrow labels -> brighter gray
}


def update_colors(elements: list) -> None:
    for el in elements:
        # Update stroke colors
        sc = el.get("strokeColor", "")
        if sc in STROKE_MAP:
            el["strokeColor"] = STROKE_MAP[sc]
        if sc in TEXT_COLOR_MAP:
            el["strokeColor"] = TEXT_COLOR_MAP[sc]

        # Update background colors
        bg = el.get("backgroundColor", "")
        if bg in BG_MAP:
            el["backgroundColor"] = BG_MAP[bg]

        # Boost zone background opacity from 20 to 35
        if el.get("type") == "rectangle" and el.get("opacity") == 20:
            el["opacity"] = 35


def main() -> None:
    data = json.loads(FILE.read_text())
    update_colors(data["elements"])
    FILE.write_text(json.dumps(data, indent=2))
    print(f"Updated colors in {FILE}")


if __name__ == "__main__":
    main()
