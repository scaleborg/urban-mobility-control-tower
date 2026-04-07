# Urban Mobility Control Tower

End-to-end real-time data pipeline for bike-share availability metrics.
Ingests [Citi Bike GBFS](https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json) feeds, captures changes via CDC, computes streaming aggregates, and serves analytical data through a low-latency API.

## Architecture

![Architecture](docs/architecture.png?v=2)

| Component | Role |
|---|---|
| `ingest/` | Polls Citi Bike GBFS feed into [Postgres](https://www.postgresql.org/) every 60s |
| `connectors/` | [Debezium](https://debezium.io/) CDC connector config |
| `flink/` | [Flink SQL](https://flink.apache.org/): tumbling 1-min availability windows |
| `analytics/consumer/` | [Kafka](https://kafka.apache.org/) → [DuckDB](https://duckdb.org/) landing |
| `analytics/dbt/` | [dbt](https://www.getdbt.com/) mart: `mart_station_availability_hourly` |
| `api/` | [FastAPI](https://fastapi.tiangolo.com/) read-only API over DuckDB |

## How to run

### 1. Start the pipeline

```bash
docker compose up -d
```

This starts Postgres, Kafka, Debezium, Flink, the GBFS ingestor, and the DuckDB consumer.

### 2. Register the Debezium connector

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connectors/debezium-postgres.json
```

### 3. Submit the Flink SQL job

```bash
docker compose exec jobmanager ./bin/sql-client.sh -f /opt/flink/sql/station_availability_1min.sql
```

### 4. Run dbt (after data lands in DuckDB)

```bash
cd analytics/dbt
dbt run
```

### 5. Start the API

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Example outputs

```bash
$ curl localhost:8000/metrics/stations/hourly?limit=2
```
```json
[
  {
    "station_id": "66dd5a42-0aca-11e7-82f6-3863bb44ef7c",
    "hour_ts": "2026-04-03T10:00:00",
    "avg_bikes_available": 18.0,
    "avg_docks_available": 2.0,
    "avg_capacity": 22.0,
    "avg_availability_ratio": 0.818,
    "min_availability_ratio": 0.818,
    "total_low_availability_events": 0,
    "total_events": 8
  }
]
```

```bash
$ curl localhost:8000/system/freshness
```
```json
{
  "latest_emitted_at": "2026-04-03T10:40:00",
  "latest_mart_hour_ts": "2026-04-03T10:00:00",
  "checked_at": "2026-04-03T10:40:55.494591+00:00",
  "raw_lag_seconds": 55
}
```

## Design trade-offs

- **Streaming correctness** — Flink watermarks and tumbling windows produce deterministic 1-minute aggregates from CDC events
- **Batch/serving parity** — the same DuckDB mart backs both dbt analysis and API serving
- **Production-style data contracts** — each layer (raw → staging → mart → API) has a clear schema boundary
