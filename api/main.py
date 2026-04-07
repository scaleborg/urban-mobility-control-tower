from datetime import datetime, timezone
from pathlib import Path

import duckdb
from fastapi import FastAPI, Query

DB_PATH = str(Path(__file__).resolve().parent.parent / "analytics" / "data" / "mobility.duckdb")

app = FastAPI(title="Urban Mobility Control Tower")


def get_conn() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH, read_only=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics/stations/hourly")
def stations_hourly(limit: int = Query(default=24, ge=1, le=1000)):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM mart_station_availability_hourly ORDER BY hour_ts DESC LIMIT ?",
        [limit],
    ).fetchall()
    columns = [desc[0] for desc in conn.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


@app.get("/stations/{station_id}/hourly")
def station_hourly(station_id: str, limit: int = Query(default=24, ge=1, le=1000)):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM mart_station_availability_hourly WHERE station_id = ? ORDER BY hour_ts DESC LIMIT ?",
        [station_id, limit],
    ).fetchall()
    columns = [desc[0] for desc in conn.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


@app.get("/system/freshness")
def freshness():
    conn = get_conn()
    now = datetime.now(timezone.utc)

    raw_row = conn.execute("SELECT max(emitted_at) AS latest_emitted_at FROM raw_station_metrics_1min").fetchone()
    mart_row = conn.execute("SELECT max(hour_ts) AS latest_hour_ts FROM mart_station_availability_hourly").fetchone()
    conn.close()

    latest_emitted = raw_row[0] if raw_row else None
    latest_hour = mart_row[0] if mart_row else None

    result = {
        "latest_emitted_at": latest_emitted.isoformat() if latest_emitted else None,
        "latest_mart_hour_ts": latest_hour.isoformat() if latest_hour else None,
        "checked_at": now.isoformat(),
    }

    if latest_emitted:
        emitted_utc = latest_emitted if latest_emitted.tzinfo else latest_emitted.replace(tzinfo=timezone.utc)
        result["raw_lag_seconds"] = round((now - emitted_utc).total_seconds())

    return result
