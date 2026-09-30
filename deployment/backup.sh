#!/usr/bin/env sh
set -eu

BACKUP_DIR="${BACKUP_DIR:-./backups}"
STAMP="$(date +%Y%m%d_%H%M%S)"
TARGET="$BACKUP_DIR/$STAMP"

mkdir -p "$TARGET"

docker compose exec -T backend sh -c 'cat /data/backend/timelapse.db'   > "$TARGET/timelapse.db"

docker run --rm   -v timelapse-system_timelapse_storage:/source:ro   -v "$(pwd)/$TARGET":/backup   alpine   sh -c 'cd /source && tar czf /backup/storage.tar.gz .'

echo "Backup created at: $TARGET"
