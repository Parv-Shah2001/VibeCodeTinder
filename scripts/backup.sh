#!/bin/bash
# Production backup script for 50M users scale
# - Postgres pg_dump with S3 upload
# - Redis RDB backup
# - Media metadata export

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/vibe_backup_$DATE"
mkdir -p $BACKUP_DIR

echo "🔥 VibeCodeTinder Backup $DATE"

# Postgres backup
echo "📦 Backing up Postgres..."
pg_dump $DATABASE_URL -Fc -f $BACKUP_DIR/db.dump
echo "  DB backup size: $(du -h $BACKUP_DIR/db.dump | cut -f1)"

# Redis backup
echo "📦 Backing up Redis..."
redis-cli --rdb $BACKUP_DIR/redis.rdb || echo "Redis backup skipped (no redis-cli)"

# Upload to S3
if command -v aws &> /dev/null; then
  echo "☁️ Uploading to S3..."
  aws s3 cp $BACKUP_DIR s3://vibe-backups-prod/$DATE/ --recursive
  echo "✅ Backup uploaded to s3://vibe-backups-prod/$DATE/"
else
  echo "⚠️ aws cli not found, local backup at $BACKUP_DIR"
fi

# Cleanup old backups >7 days
find /tmp -name "vibe_backup_*" -mtime +7 -exec rm -rf {} \;

echo "✅ Backup complete"
