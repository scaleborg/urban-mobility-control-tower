import json
from pathlib import Path

SRC = Path("docs/architecture.excalidraw")
OUT = Path("docs/architecture.excalidraw")


def main() -> None:
    data = json.loads(SRC.read_text())
    els = data["elements"]
    by_id = {e["id"]: e for e in els}

    def set_text(eid: str, text: str, x: float, y: float, font_size: int, color: str = "#e5e5e5"):
        e = by_id[eid]
        e["text"] = text
        e["x"] = x
        e["y"] = y
        e["fontSize"] = font_size
        e["strokeColor"] = color

    def set_box(
        box_id: str,
        title_id: str,
        subtitle_id: str,
        x: float,
        y: float,
        w: float,
        h: float,
        title: str,
        subtitle: str,
        title_size: int = 15,
        subtitle_size: int = 11,
        title_color: str = "#e5e5e5",
        subtitle_color: str = "#8f9399",
    ):
        box = by_id[box_id]
        box["x"] = x
        box["y"] = y
        box["width"] = w
        box["height"] = h

        # center title/subtitle inside box
        title_x = x + w / 2 - len(title) * title_size * 0.22
        title_y = y + 12
        subtitle_x = x + w / 2 - len(subtitle) * subtitle_size * 0.19
        subtitle_y = y + 35

        set_text(title_id, title, title_x, title_y, title_size, title_color)
        set_text(subtitle_id, subtitle, subtitle_x, subtitle_y, subtitle_size, subtitle_color)

    def set_zone(zone_id: str, label_id: str, x: float, y: float, w: float, h: float, label: str, color: str):
        z = by_id[zone_id]
        z["x"] = x
        z["y"] = y
        z["width"] = w
        z["height"] = h
        set_text(label_id, label, x + w / 2 - len(label) * 4.7, y + 10, 16, color)

    def set_arrow_horizontal(aid: str, x1: float, y1: float, x2: float):
        a = by_id[aid]
        a["x"] = x1
        a["y"] = y1
        a["width"] = x2 - x1
        a["height"] = 0
        a["points"] = [[0, 0], [x2 - x1, 0]]

    def set_arrow_vertical(aid: str, x: float, y1: float, y2: float):
        a = by_id[aid]
        a["x"] = x
        a["y"] = y1
        a["width"] = 0
        a["height"] = y2 - y1
        a["points"] = [[0, 0], [0, y2 - y1]]

    # canvas/title
    set_text("title", "Urban Mobility Control Tower", 425, -52, 24, "#e5e5e5")
    set_text("subtitle", "CDC \u2192 Streaming \u2192 Analytics \u2192 API", 470, -18, 15, "#a0a0a0")

    # zones
    zone_y = 0
    zone_h = 305
    zone_w = 220
    xs = [0, 250, 500, 750, 1000]

    set_zone("z1", "zl1", xs[0], zone_y, zone_w, zone_h, "INGEST", "#22c55e")
    set_zone("z2", "zl2", xs[1], zone_y, zone_w, zone_h, "CDC", "#f59e0b")
    set_zone("z3", "zl3", xs[2], zone_y, zone_w, zone_h, "STREAM", "#8b5cf6")
    set_zone("z4", "zl4", xs[3], zone_y, zone_w, zone_h, "ANALYTICAL", "#06b6d4")
    set_zone("z5", "zl5", xs[4], zone_y, zone_w, zone_h, "SERVE", "#4a9eed")

    # common box sizing
    bx = 20
    bw = 180
    bh = 62

    # INGEST
    set_box("gbfs", "t_gbfs", "s_gbfs", xs[0] + bx, 48, bw, bh, "GBFS API", "Citi Bike station feeds")
    set_box("ingest_svc", "t_ingest", "s_ingest", xs[0] + bx, 142, bw, bh, "Ingest Service", "upsert station state")
    set_box("postgres", "t_pg", "s_pg", xs[0] + bx, 236, bw, bh, "Postgres", "operational source of truth")

    # Zigzag layout: cross-zone arrows stay horizontal by alternating
    # which box is top vs bottom row in each zone.
    # Row 1 (top, y=72):  Kafka CDC, Flink, dbt, FastAPI
    # Row 2 (bot, y=208): Debezium, Kafka Metrics, DuckDB
    # Internal arrows go vertical; cross-zone arrows go horizontal.

    # CDC — Kafka top, Debezium bottom (Postgres connects horizontally to Debezium)
    set_box("kafka_cdc", "t_kc", "s_kc", xs[1] + bx, 72, bw, bh, "Kafka", "mobility.public.station_status")
    set_box("debezium", "t_dbz", "s_dbz", xs[1] + bx, 208, bw, bh, "Debezium", "Postgres CDC capture")

    # STREAM — Flink top, Kafka Metrics bottom
    set_box("flink", "t_flink", "s_flink", xs[2] + bx, 72, bw, bh, "Flink SQL", "1-min tumbling windows")
    set_box("kafka_met", "t_km", "s_km", xs[2] + bx, 208, bw, bh, "Kafka Metrics Topic", "metrics.station_availability_1min")

    # ANALYTICAL — dbt top, DuckDB bottom
    set_box("dbt", "t_dbt", "s_dbt", xs[3] + bx, 72, bw, bh, "dbt", "mart_station_availability_hourly")
    set_box("duckdb", "t_duck", "s_duck", xs[3] + bx, 208, bw, bh, "DuckDB", "raw_station_metrics_1min")

    # SERVE — FastAPI top row (aligns with dbt for horizontal arrow)
    set_box("fastapi", "t_api", "s_api", xs[4] + bx, 72, bw, bh, "FastAPI", "read-only analytics API")

    # endpoint annotation (below FastAPI)
    set_text("ep_label", "endpoints", 1086, 145, 12, "#a0a0a0")
    set_text(
        "ep_list",
        "/health\n/metrics/stations/hourly\n/stations/{id}/hourly\n/system/freshness",
        1040,
        165,
        11,
        "#a0a0a0",
    )

    # --- Arrows ---
    # Box centers:  top row cy=103, bottom row cy=239, Ingest rows: 79, 173, 267

    # INGEST vertical: GBFS -> Ingest Service -> Postgres
    set_arrow_vertical("a1", 110, 110, 142)       # gbfs bottom -> ingest top
    set_text("a1l", "poll every 60s", 118, 118, 12, "#a0a0a0")

    set_arrow_vertical("a2", 110, 204, 236)        # ingest bottom -> postgres top
    set_text("a2l", "upsert", 118, 212, 12, "#a0a0a0")

    # Postgres(bot) -> Debezium(bot): HORIZONTAL at y=239
    set_arrow_horizontal("a3", 200, 239, 270)
    set_text("a3l", "change events", 206, 222, 12, "#a0a0a0")

    # Debezium(bot) -> Kafka(top): VERTICAL UP within CDC
    set_arrow_vertical("a4", 360, 208, 134)        # debezium top -> kafka bottom
    set_text("a4l", "CDC stream", 368, 163, 12, "#a0a0a0")

    # Kafka(top) -> Flink(top): HORIZONTAL at y=103
    set_arrow_horizontal("a5", 450, 103, 520)
    set_text("a5l", "consume CDC", 456, 86, 12, "#a0a0a0")

    # Flink(top) -> Kafka Metrics(bot): VERTICAL DOWN within STREAM
    set_arrow_vertical("a6", 610, 134, 208)
    set_text("a6l", "windowed metrics", 618, 163, 12, "#a0a0a0")

    # Kafka Metrics(bot) -> DuckDB(bot): HORIZONTAL at y=239
    set_arrow_horizontal("a7", 700, 239, 770)
    set_text("a7l", "land", 724, 222, 12, "#a0a0a0")

    # DuckDB(bot) -> dbt(top): VERTICAL UP within ANALYTICAL
    set_arrow_vertical("a8", 860, 208, 134)
    set_text("a8l", "transform", 868, 163, 12, "#a0a0a0")

    # dbt(top) -> FastAPI(top): HORIZONTAL at y=103
    set_arrow_horizontal("a9", 950, 103, 1020)
    set_text("a9l", "read mart", 958, 86, 12, "#a0a0a0")

    # FastAPI -> endpoints dashed
    set_arrow_vertical("a_ep", 1110, 134, 158)

    OUT.write_text(json.dumps(data, indent=2))
    print(f"Updated {OUT}")


if __name__ == "__main__":
    main()
