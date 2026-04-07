# dbt — Urban Mobility Analytics

## Running dbt

The system `dbt` binary is dbt Cloud CLI. Use dbt-core via Python instead:

```bash
cd analytics/dbt
/usr/bin/python3 -m dbt.cli.main run --profiles-dir .
```

## DuckDB single-writer caveat

DuckDB allows only one write connection at a time. The `duckdb-consumer` service holds a write connection while running. You must stop it before running dbt:

```bash
# Stop consumer
docker compose stop duckdb-consumer

# Run dbt
cd analytics/dbt
/usr/bin/python3 -m dbt.cli.main run --profiles-dir .

# Restart consumer (resumes from last committed Kafka offset)
docker compose start duckdb-consumer
```

The consumer will not lose data — Kafka retains messages and the consumer group tracks offsets. Any events produced while the consumer is stopped will be picked up on restart.
