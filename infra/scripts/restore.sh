#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: VOLUMA_RESTORE_CONFIRM=RESTORE-VOLUMA ./infra/scripts/restore.sh <encrypted-backup>" >&2
  exit 64
fi

if [ "${VOLUMA_RESTORE_CONFIRM:-}" != "RESTORE-VOLUMA" ]; then
  echo "Refusing restore: set VOLUMA_RESTORE_CONFIRM=RESTORE-VOLUMA after validating the target and backup." >&2
  exit 64
fi

: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${VOLUMA_BACKUP_ENCRYPTION_PASSWORD:?VOLUMA_BACKUP_ENCRYPTION_PASSWORD is required}"

archive_path=$1
if [ ! -f "$archive_path" ]; then
  echo "Encrypted backup does not exist: $archive_path" >&2
  exit 66
fi

hmac_path="$archive_path.hmac"
if [ ! -f "$hmac_path" ]; then
  echo "Authenticated backup checksum does not exist: $hmac_path" >&2
  exit 66
fi

work_dir=$(mktemp -d)
umask 077
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

expected_hmac=$(awk '{print $NF}' "$hmac_path")
actual_hmac=$(openssl dgst -sha256 -mac HMAC -macopt keyenv:VOLUMA_BACKUP_ENCRYPTION_PASSWORD "$archive_path" | awk '{print $NF}')
if [ "$expected_hmac" != "$actual_hmac" ]; then
  echo "Backup authentication check failed." >&2
  exit 65
fi

openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 \
  -in "$archive_path" \
  -out "$work_dir/payload.tar.gz" \
  -pass env:VOLUMA_BACKUP_ENCRYPTION_PASSWORD
tar -xzf "$work_dir/payload.tar.gz" -C "$work_dir"

(
  cd "$work_dir"
  sha256sum --check payload.sha256
)

docker compose exec -T postgres pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" < "$work_dir/database.dump"

docker compose run --rm --no-deps --entrypoint sh api -c \
  'find /var/lib/voluma-media -mindepth 1 -maxdepth 1 -exec rm -rf {} +'
docker compose run --rm --no-deps --entrypoint tar api \
  -C /var/lib/voluma-media \
  -xzf - < "$work_dir/media.tar.gz"

echo "Database and media restore completed. Run the documented post-restore smoke checks before accepting traffic."
