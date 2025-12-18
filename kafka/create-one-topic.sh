#!/usr/bin/env bash
set -euo pipefail

BS="kafka-1:29092"

create_topic () {
  local TOPIC="$1"
  local PARTITIONS="$2"
  local RF="$3"

  kafka-topics --bootstrap-server "$BS" --create \
    --topic "$TOPIC" \
    --partitions "$PARTITIONS" \
    --replication-factor "$RF"

  echo "Created topic: $TOPIC"
}

create_topic "my.single.topic" 3 2
