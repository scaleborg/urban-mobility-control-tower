#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for Kafka Connect..."
until curl -sf http://localhost:8083/connectors > /dev/null 2>&1; do
    sleep 2
done
echo "Kafka Connect is ready."

curl -sf -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mobility-postgres-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": "postgres",
        "database.port": "5432",
        "database.user": "mobility",
        "database.password": "mobility",
        "database.dbname": "mobility",
        "database.server.name": "mobility",
        "topic.prefix": "mobility",
        "table.include.list": "public.station_status",
        "plugin.name": "pgoutput",
        "publication.autocreate.mode": "filtered",
        "slot.name": "mobility_slot",
        "heartbeat.interval.ms": "10000",
        "tombstones.on.delete": "false",
        "key.converter": "org.apache.kafka.connect.json.JsonConverter",
        "key.converter.schemas.enable": "false",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false"
    }
}' | python3 -m json.tool

echo ""
echo "Connector registered. Topic: mobility.public.station_status"
