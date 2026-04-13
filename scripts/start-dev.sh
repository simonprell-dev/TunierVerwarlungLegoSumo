#!/usr/bin/env bash
set -euo pipefail

export COMPOSE_PROFILES=${COMPOSE_PROFILES:-dev}
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

echo "Development stack started."
