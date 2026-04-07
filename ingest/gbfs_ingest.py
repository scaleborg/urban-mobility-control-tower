import os
import time
import logging
from datetime import datetime, timezone

import requests
import psycopg2
from psycopg2.extras import execute_values

STATION_INFO_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 60))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", 5432),
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
    )


def upsert_stations(conn):
    resp = requests.get(STATION_INFO_URL, timeout=30)
    resp.raise_for_status()
    stations = resp.json()["data"]["stations"]

    rows = [
        (
            s["station_id"],
            s["name"],
            s.get("short_name"),
            s["lat"],
            s["lon"],
            s.get("capacity"),
            s.get("region_id"),
            s.get("station_type"),
            s.get("has_kiosk", False),
        )
        for s in stations
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO stations
                (station_id, name, short_name, lat, lon,
                 capacity, region_id, station_type, has_kiosk)
            VALUES %s
            ON CONFLICT (station_id) DO UPDATE SET
                name         = EXCLUDED.name,
                short_name   = EXCLUDED.short_name,
                lat          = EXCLUDED.lat,
                lon          = EXCLUDED.lon,
                capacity     = EXCLUDED.capacity,
                region_id    = EXCLUDED.region_id,
                station_type = EXCLUDED.station_type,
                has_kiosk    = EXCLUDED.has_kiosk,
                updated_at   = now()
            """,
            rows,
        )
    conn.commit()
    log.info("Upserted %d stations", len(rows))


def upsert_status(conn):
    resp = requests.get(STATION_STATUS_URL, timeout=30)
    resp.raise_for_status()
    statuses = resp.json()["data"]["stations"]

    rows = [
        (
            s["station_id"],
            s.get("num_bikes_available", 0),
            s.get("num_ebikes_available", 0),
            s.get("num_bikes_disabled", 0),
            s.get("num_docks_available", 0),
            s.get("num_docks_disabled", 0),
            bool(s.get("is_installed", 0)),
            bool(s.get("is_renting", 0)),
            bool(s.get("is_returning", 0)),
            datetime.fromtimestamp(s["last_reported"], tz=timezone.utc)
            if s.get("last_reported") and s["last_reported"] > 86400
            else None,
        )
        for s in statuses
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO station_status
                (station_id, num_bikes_available, num_ebikes_available,
                 num_bikes_disabled, num_docks_available, num_docks_disabled,
                 is_installed, is_renting, is_returning, last_reported, ingested_at)
            VALUES %s
            ON CONFLICT (station_id) DO UPDATE SET
                num_bikes_available  = EXCLUDED.num_bikes_available,
                num_ebikes_available = EXCLUDED.num_ebikes_available,
                num_bikes_disabled   = EXCLUDED.num_bikes_disabled,
                num_docks_available  = EXCLUDED.num_docks_available,
                num_docks_disabled   = EXCLUDED.num_docks_disabled,
                is_installed         = EXCLUDED.is_installed,
                is_renting           = EXCLUDED.is_renting,
                is_returning         = EXCLUDED.is_returning,
                last_reported        = EXCLUDED.last_reported,
                ingested_at          = now()
            """,
            [r + (None,) for r in rows],
        )
    conn.commit()
    log.info("Upserted %d station statuses", len(rows))


def main():
    log.info("Starting GBFS ingestor, poll interval=%ds", POLL_INTERVAL)
    while True:
        try:
            conn = get_conn()
            try:
                upsert_stations(conn)
                upsert_status(conn)
            finally:
                conn.close()
        except Exception:
            log.exception("Error in poll cycle, will retry")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
