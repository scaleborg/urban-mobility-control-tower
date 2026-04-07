select
    station_id,
    window_start,
    window_end,
    avg_bikes_available,
    avg_docks_available,
    avg_capacity,
    avg_availability_ratio,
    low_availability_events,
    event_count,
    emitted_at
from {{ source('raw', 'raw_station_metrics_1min') }}
