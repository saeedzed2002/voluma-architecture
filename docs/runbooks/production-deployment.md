# Production deployment runbook

This runbook deploys the single-server VOLUMA stack defined in the product
specification. It is not a local-development procedure.

## Preconditions

- Use a supported Linux host with Docker Engine and Docker Compose available to the
  deployment operator.
- Point DNS for the canonical HTTPS hostname to the host before issuing a
  certificate.
- Keep the protected environment file outside the checkout, for example at
  `/etc/voluma/production.env`, with permissions readable only by the deployment
  operator.
- Obtain the initial valid certificate before starting the public stack with Certbot's
  standalone flow, replacing the sample hostname and email:

```sh
sudo certbot certonly --standalone \
  --domain architecture.example.com --email operations@example.com --agree-tos --non-interactive
```

  `VOLUMA_TLS_CERT_PATH` and `VOLUMA_TLS_KEY_PATH` then point to Certbot's `fullchain.pem`
  and `privkey.pem`. The scheduled renewal command must briefly free port `80`, then
  restart only Nginx after a successful renewal:

```sh
certbot renew \
  --pre-hook 'cd /srv/voluma && docker compose --env-file /etc/voluma/production.env stop nginx' \
  --post-hook 'cd /srv/voluma && docker compose --env-file /etc/voluma/production.env start nginx'
```

The protected file must set `VOLUMA_ENVIRONMENT=production`, a canonical
`VOLUMA_PUBLIC_ORIGIN` beginning with `https://`, database and Redis URLs that use the
internal `postgres` and `redis` service names, strong distinct `POSTGRES_PASSWORD` and
`REDIS_PASSWORD` values, and absolute `VOLUMA_TLS_CERT_PATH` and
`VOLUMA_TLS_KEY_PATH` host paths. URL-encode reserved characters in passwords embedded
in database or Redis URLs.

Do not set `NEXT_PUBLIC_API_BASE_URL` in production. The frontend server uses the
private `api` network address; browsers use the same public origin through Nginx.

## First deployment

1. Put the certificate and key at the paths named in the protected file. The key must
   be readable by the non-root Nginx container account (the official image uses numeric
   UID/GID `101`) but not world-readable; use a dedicated group-readable copy or a
   Docker secret-compatible mount rather than making the private key globally readable.
2. Set `VOLUMA_INITIAL_ADMIN_EMAIL` and `VOLUMA_INITIAL_ADMIN_PASSWORD` only in the
   protected bootstrap environment. The password must be unique and at least 12
   characters. It is never committed or printed by the release process.
3. Build and start the stack, including the one-shot migration service:

```sh
docker compose --env-file /etc/voluma/production.env up --build --detach --wait
docker compose --env-file /etc/voluma/production.env --profile bootstrap run --rm --no-deps provision-admin
```

4. Record the resulting application-image digests, then run the release smoke suite:

```sh
docker image inspect voluma-api:local voluma-frontend:local voluma-nginx:local --format '{{index .RepoDigests 0}}'
VOLUMA_SMOKE_ADMIN_EMAIL="$VOLUMA_INITIAL_ADMIN_EMAIL" \
VOLUMA_SMOKE_ADMIN_PASSWORD="$VOLUMA_INITIAL_ADMIN_PASSWORD" \
sh infra/scripts/release-smoke.sh
```

5. Remove the initial-admin password from the deployment environment after confirming
   the administrator can sign in. Future releases do not enable the `bootstrap`
   profile.

## Subsequent release

1. Read the migration revision and rollback notes before applying the release. A
   migration without a reversible downgrade requires a tested backup/restore plan.
2. Create and verify an encrypted database-plus-media backup using the backup runbook.
3. Build the immutable images from the committed lockfiles and update the services:

```sh
docker compose --env-file /etc/voluma/production.env up --build --detach --wait
```

4. Record application-image digests and scan them before accepting traffic.
5. Run the release smoke suite and inspect the Nginx, API, and worker logs.

Only Nginx maps host ports `80` and `443`. PostgreSQL, Redis, the API, Celery worker,
and Next.js remain on the private Compose network. Do not add port mappings for those
services as a troubleshooting shortcut.

## Rollback boundary

Roll back only to a previously recorded application-image digest after assessing the
database migration. Never use `docker compose down --volumes` for a release rollback.
If the new schema cannot be safely downgraded, restore the verified PostgreSQL and
media backup together, then start the prior image set and rerun smoke checks.
