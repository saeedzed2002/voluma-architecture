#!/usr/bin/env sh
set -eu

if [ "${VOLUMA_BACKUP_QUIESCED:-}" != "1" ]; then
  echo "Refusing backup: stop API writes and the worker first, then set VOLUMA_BACKUP_QUIESCED=1." >&2
  exit 64
fi

: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${VOLUMA_BACKUP_ENCRYPTION_PASSWORD:?VOLUMA_BACKUP_ENCRYPTION_PASSWORD is required}"
: "${VOLUMA_OFFSITE_BACKUP_DIR:?VOLUMA_OFFSITE_BACKUP_DIR is required}"

timestamp=$(date -u +%Y%m%dT%H%M%SZ)
backup_root="$(pwd)/infra/backups/$timestamp"
work_dir=$(mktemp -d)

umask 077
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
mkdir -p "$backup_root" "$VOLUMA_OFFSITE_BACKUP_DIR"

docker compose exec -T postgres pg_dump \
  --format=custom \
  --no-owner \
  --no-privileges \
  --username "$POSTGRES_USER" \
  "$POSTGRES_DB" > "$work_dir/database.dump"

docker compose run --rm --no-deps --entrypoint tar api \
  -C /var/lib/voluma-media \
  -czf - . > "$work_dir/media.tar.gz"

(
  cd "$work_dir"
  sha256sum database.dump media.tar.gz > payload.sha256
  tar -czf payload.tar.gz database.dump media.tar.gz payload.sha256
)

openssl enc -aes-256-cbc -salt -pbkdf2 -iter 600000 \
  -in "$work_dir/payload.tar.gz" \
  -out "$backup_root/voluma-$timestamp.tar.gz.enc" \
  -pass env:VOLUMA_BACKUP_ENCRYPTION_PASSWORD

sha256sum "$backup_root/voluma-$timestamp.tar.gz.enc" > "$backup_root/voluma-$timestamp.tar.gz.enc.sha256"
openssl dgst -sha256 -mac HMAC -macopt keyenv:VOLUMA_BACKUP_ENCRYPTION_PASSWORD \
  "$backup_root/voluma-$timestamp.tar.gz.enc" > "$backup_root/voluma-$timestamp.tar.gz.enc.hmac"
cp "$backup_root/voluma-$timestamp.tar.gz.enc" \
  "$backup_root/voluma-$timestamp.tar.gz.enc.sha256" \
  "$backup_root/voluma-$timestamp.tar.gz.enc.hmac" \
  "$VOLUMA_OFFSITE_BACKUP_DIR/"

echo "Encrypted database and media backup written to $backup_root and copied off-host."
