CREATE TABLE IF NOT EXISTS stations (
    station_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    short_name   TEXT,
    lat          DOUBLE PRECISION NOT NULL,
    lon          DOUBLE PRECISION NOT NULL,
    capacity     INTEGER,
    region_id    TEXT,
    station_type TEXT,
    has_kiosk    BOOLEAN,
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS station_status (
    station_id           TEXT PRIMARY KEY REFERENCES stations(station_id),
    num_bikes_available  INTEGER NOT NULL DEFAULT 0,
    num_ebikes_available INTEGER NOT NULL DEFAULT 0,
    num_bikes_disabled   INTEGER NOT NULL DEFAULT 0,
    num_docks_available  INTEGER NOT NULL DEFAULT 0,
    num_docks_disabled   INTEGER NOT NULL DEFAULT 0,
    is_installed         BOOLEAN NOT NULL DEFAULT FALSE,
    is_renting           BOOLEAN NOT NULL DEFAULT FALSE,
    is_returning         BOOLEAN NOT NULL DEFAULT FALSE,
    last_reported        TIMESTAMPTZ,
    ingested_at          TIMESTAMPTZ DEFAULT now()
);

-- REPLICA IDENTITY FULL gives rich before/after images in Debezium CDC events.
-- Increases WAL volume (full row logged per UPDATE); acceptable for ~2359 rows.
ALTER TABLE station_status REPLICA IDENTITY FULL;
