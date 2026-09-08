# Backup and restore runbook

VOLUMA recovery always includes both PostgreSQL and the complete `media_data` volume.
Database-only recovery is invalid because media metadata and derivative files must stay
consistent.

## Daily encrypted backup

Before backup, place the site in a planned maintenance window and stop the API and
worker so that no content or media operation changes the database or shared volume.
Do not stop PostgreSQL or Redis.

```sh
docker compose --env-file /etc/voluma/production.env stop api worker
VOLUMA_BACKUP_QUIESCED=1 \
VOLUMA_BACKUP_ENCRYPTION_PASSWORD='<protected backup password>' \
VOLUMA_OFFSITE_BACKUP_DIR=/mnt/offsite/voluma \
sh infra/scripts/backup.sh
docker compose --env-file /etc/voluma/production.env start api worker
```

The script creates a PostgreSQL custom dump and a complete media archive, hashes both,
encrypts the payload with `openssl` using `PBKDF2` plus an `HMAC` integrity check,
writes the encrypted artifact below `infra/backups/`, and copies the encrypted artifact and checksums to the configured
off-host mounted destination. Keep the encryption password out of shell history and
source control. Configure retention at the off-host destination; retain at least one
recent restore-tested backup and multiple dated recovery points.

After every backup, validate the off-host checksum against the local checksum. At least
quarterly, execute the restore procedure on an isolated non-production host and record
the date, archive identifier, operator, and smoke-check result in the operational
release record.

## Restore procedure

1. Verify the exact target host, Compose project, encrypted archive checksum, and
   recovery point. Announce maintenance before any destructive action.
2. Start only `postgres` and `redis`, then run the restore script with the explicit
   confirmation value. It cleans the target database and media volume before importing
   the verified archive.

```sh
docker compose --env-file /etc/voluma/production.env up --detach postgres redis
VOLUMA_RESTORE_CONFIRM=RESTORE-VOLUMA \
VOLUMA_BACKUP_ENCRYPTION_PASSWORD='<protected backup password>' \
sh infra/scripts/restore.sh /mnt/offsite/voluma/voluma-YYYYMMDDTHHMMSSZ.tar.gz.enc
```

3. Start `migrate`, `api`, `worker`, `frontend`, and `nginx` with the prior approved
   image set. Do not seed development fixtures.
4. Verify `/api/readyz` through Nginx, localized public pages, an existing derivative,
   administrator authentication, and Nginx cache/security headers before ending the
   maintenance window.

The restore command is deliberately confirmation-gated. Do not run it against a host
whose target or backup identity is uncertain.
