#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for Flink REST API..."
until curl -sf http://localhost:8081/overview > /dev/null 2>&1; do
    sleep 2
done
echo "Flink is ready."

echo "Submitting availability SQL job..."
/opt/flink/bin/sql-client.sh -f /opt/flink/sql/availability.sql
echo "Job submitted."
