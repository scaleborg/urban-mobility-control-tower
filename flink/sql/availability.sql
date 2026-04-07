-- Source: Debezium CDC events from station_status
CREATE TABLE station_status (
    station_id           STRING,
    num_bikes_available  INT,
    num_docks_available  INT,
    num_bikes_disabled   INT,
    num_docks_disabled   INT,
    ingested_at          TIMESTAMP_LTZ(3),
    WATERMARK FOR ingested_at AS ingested_at - INTERVAL '10' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'mobility.public.station_status',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-availability',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'debezium-json',
    'debezium-json.timestamp-format.standard' = 'ISO-8601',
    'debezium-json.ignore-parse-errors' = 'false'
);

-- Sink: 1-minute windowed availability metrics
CREATE TABLE station_availability_1min (
    station_id              STRING,
    window_start            TIMESTAMP_LTZ(3),
    window_end              TIMESTAMP_LTZ(3),
    avg_bikes_available     DOUBLE,
    avg_docks_available     DOUBLE,
    avg_capacity            DOUBLE,
    avg_availability_ratio  DOUBLE,
    low_availability_events BIGINT,
    event_count             BIGINT,
    emitted_at              TIMESTAMP_LTZ(3)
) WITH (
    'connector' = 'kafka',
    'topic' = 'metrics.station_availability_1min',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json'
);

-- 1-minute tumbling window aggregation
INSERT INTO station_availability_1min
SELECT
    station_id,
    TUMBLE_START(ingested_at, INTERVAL '1' MINUTE)  AS window_start,
    TUMBLE_END(ingested_at, INTERVAL '1' MINUTE)    AS window_end,
    AVG(CAST(num_bikes_available AS DOUBLE))         AS avg_bikes_available,
    AVG(CAST(num_docks_available AS DOUBLE))         AS avg_docks_available,
    AVG(CAST(num_bikes_available + num_docks_available
           + num_bikes_disabled + num_docks_disabled AS DOUBLE)) AS avg_capacity,
    AVG(
        CAST(num_bikes_available AS DOUBLE)
        / NULLIF(CAST(num_bikes_available + num_docks_available
                     + num_bikes_disabled + num_docks_disabled AS DOUBLE), 0)
    )                                                AS avg_availability_ratio,
    SUM(CASE
        WHEN CAST(num_bikes_available AS DOUBLE)
             / NULLIF(CAST(num_bikes_available + num_docks_available
                          + num_bikes_disabled + num_docks_disabled AS DOUBLE), 0)
             < 0.2
        THEN 1 ELSE 0
    END)                                             AS low_availability_events,
    COUNT(*)                                         AS event_count,
    TUMBLE_END(ingested_at, INTERVAL '1' MINUTE)     AS emitted_at
FROM station_status
GROUP BY station_id, TUMBLE(ingested_at, INTERVAL '1' MINUTE);
