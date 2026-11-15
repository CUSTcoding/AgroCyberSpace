# Optional Docker Runtime

Docker is optional for this backend. The application connects to PostgreSQL/PostGIS through `DATABASE_URL`; Compose does not create a database and does not require Redis or MinIO.

## Files

- `apps/backend/Dockerfile`: Python 3.12 FastAPI image, non-root runtime user, dependency lockfile, and application/migration/seed code.
- `apps/backend/.dockerignore`: excludes Git metadata, virtual environments, caches, local storage, and rasters from the build context.
- `infra/docker-compose.yml`: one FastAPI service, external database URL, and persistent `backend_storage` volume.
- `infra/docker-compose.dev.yml`: source bind mount and Uvicorn reload.
- Legacy `infra/docker/Dockerfile.*` files are not referenced by this backend Compose stack.

## Configure

From the repository root:

```bash
cp infra/.env.example infra/.env
```

Edit `infra/.env` and set:

- `DATABASE_URL`: reachable PostgreSQL/PostGIS URL; use `sslmode=require` for cloud providers.
- `JWT_SECRET`: random secret of at least 32 characters in production.
- `CORS_ORIGINS`: comma-separated allowed frontend origins.

Do not commit `infra/.env` or put real credentials in the example file.

## Start

Production-style container:

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml up --build -d
```

Development with reload:

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build
```

The API is exposed at `http://localhost:8000`; Swagger UI is at `/api/v1/docs`. Raster/object storage maps to the named volume `backend_storage` at `/app/storage`.

## Migrations and shutdown

Compose does not run Alembic automatically. Confirm the target database URL before applying migrations. Use a dedicated test database for migration validation; do not substitute a development/production database.

Stop containers without deleting local assets:

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml down
```

Do not add `-v` unless you intend to delete the named storage volume.

## Verification status

The Dockerfile and Compose files were not built or started because disk space is constrained. No tests were run for this Docker/documentation adjustment.
