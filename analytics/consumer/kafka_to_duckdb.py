import json
import os
import time
import logging

import duckdb
from confluent_kafka import Consumer, KafkaError

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "metrics.station_availability_1min"
KAFKA_GROUP_ID = "duckdb-consumer"
DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "/data/mobility.duckdb")
BATCH_SIZE = 500
FLUSH_INTERVAL_S = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_station_metrics_1min (
    station_id              VARCHAR,
    window_start            TIMESTAMP,
    window_end              TIMESTAMP,
    avg_bikes_available     DOUBLE,
    avg_docks_available     DOUBLE,
    avg_capacity            DOUBLE,
    avg_availability_ratio  DOUBLE,
    low_availability_events BIGINT,
    event_count             BIGINT,
    emitted_at              TIMESTAMP
)
"""

INSERT_SQL = """
INSERT INTO raw_station_metrics_1min VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def init_duckdb():
    con = duckdb.connect(DUCKDB_PATH)
    con.execute(CREATE_TABLE_SQL)
    return con


def flush_batch(con, batch):
    if not batch:
        return
    rows = []
    for msg in batch:
        m = json.loads(msg)
        rows.append((
            m["station_id"],
            m["window_start"],
            m["window_end"],
            m["avg_bikes_available"],
            m["avg_docks_available"],
            m["avg_capacity"],
            m["avg_availability_ratio"],
            m["low_availability_events"],
            m["event_count"],
            m["emitted_at"],
        ))
    con.executemany(INSERT_SQL, rows)
    log.info("Flushed %d rows to DuckDB", len(rows))


def main():
    log.info("Starting Kafka-to-DuckDB consumer, topic=%s", KAFKA_TOPIC)
    con = init_duckdb()

    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": KAFKA_GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    consumer.subscribe([KAFKA_TOPIC])

    batch = []
    last_flush = time.time()

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                if batch and time.time() - last_flush >= FLUSH_INTERVAL_S:
                    flush_batch(con, batch)
                    batch = []
                    last_flush = time.time()
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                log.error("Consumer error: %s", msg.error())
                continue

            batch.append(msg.value().decode("utf-8"))

            if len(batch) >= BATCH_SIZE or time.time() - last_flush >= FLUSH_INTERVAL_S:
                flush_batch(con, batch)
                batch = []
                last_flush = time.time()
    except KeyboardInterrupt:
        log.info("Shutting down")
    finally:
        if batch:
            flush_batch(con, batch)
        consumer.close()
        con.close()


if __name__ == "__main__":
    main()
