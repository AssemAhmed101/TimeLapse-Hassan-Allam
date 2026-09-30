#!/usr/bin/env sh
set -eu

if [ ! -f .env.production ]; then
  echo "Missing .env.production"
  echo "Copy .env.production.example to .env.production and edit it first."
  exit 1
fi

docker compose build
docker compose up -d

echo
echo "Deployment started."
echo "Run: docker compose ps"
echo "Logs: docker compose logs -f"
