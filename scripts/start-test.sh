#!/usr/bin/env bash
set -euo pipefail

docker compose -f docker-compose.yml -f docker-compose.test.yml up -d --build

echo "Test stack started."
