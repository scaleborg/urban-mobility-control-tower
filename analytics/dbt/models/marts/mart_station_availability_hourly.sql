select
    station_id,
    date_trunc('hour', window_start)            as hour_ts,
    avg(avg_bikes_available)                    as avg_bikes_available,
    avg(avg_docks_available)                    as avg_docks_available,
    avg(avg_capacity)                           as avg_capacity,
    avg(avg_availability_ratio)                 as avg_availability_ratio,
    min(avg_availability_ratio)                 as min_availability_ratio,
    sum(low_availability_events)                as total_low_availability_events,
    sum(event_count)                            as total_events
from {{ ref('stg_station_metrics_1min') }}
group by station_id, date_trunc('hour', window_start)
