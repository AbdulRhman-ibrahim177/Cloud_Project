#!/usr/bin/env bash
set -euo pipefail

# Use kafka-1 internal listener; containers talk inside the network.
# BS="kafka-1:9092"
BS="kafka-1:29092"
MSIR=2

create_topic () {
  local TOPIC="$1" PARTITIONS="$2" RF="$3" RET_MS="$4" CLEANUP="$5"
  kafka-topics --bootstrap-server "$BS" --create \
    --topic "$TOPIC" \
    --partitions "$PARTITIONS" \
    --replication-factor "$RF" \
    --config retention.ms="$RET_MS" \
    --config cleanup.policy="$CLEANUP" \
    --config min.insync.replicas="$MSIR"
  echo "Created: $TOPIC"
}

# Document pipeline
create_topic document.uploaded                 6 2 604800000 delete
create_topic document.processed                6 2 604800000 delete
create_topic notes.generated                   6 2 1209600000 delete

# Quiz flow
create_topic quiz.requested                    4 2 604800000 delete
create_topic quiz.generated                    4 2 1209600000 delete

# Audio STT/TTS
create_topic audio.transcription.requested     4 2 259200000 delete
create_topic audio.transcription.completed     4 2 604800000 delete
create_topic audio.generation.requested        4 2 259200000 delete
create_topic audio.generation.completed        4 2 604800000 delete

# Chat
create_topic chat.message                      12 2 259200000 compact

# Event sourcing
create_topic domain.events                     12 2 31536000000 compact
