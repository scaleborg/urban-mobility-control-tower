# Control Tower API

FastAPI service that reads from the DuckDB analytical layer (read-only).

## Run

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /metrics/stations/hourly?limit=24` | Recent hourly station metrics |
| `GET /stations/{station_id}/hourly?limit=24` | Hourly metrics for one station |
| `GET /system/freshness` | Latest timestamps and data lag |
