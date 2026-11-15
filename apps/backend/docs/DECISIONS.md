# AgroSight Fair Space API — Architecture & Technical Decisions

Formal log of Architecture Decision Records (ADRs).

---

## ADR 001: Dependency and Environment Management with uv
- **Date:** 2026-11-15
- **Status:** Accepted
- **Context:** Need to manage dependencies reproducibly, rapidly, and deterministically using Python 3.12.
- **Alternatives Considered:** Poetry, Pipenv, pip-tools, uv.
- **Decision:** Adopt `uv` with `pyproject.toml` and `uv.lock`.
- **Rationale:** Orders of magnitude faster execution, native support for pinned Python toolchains (`cpython-3.12`), strict cross-platform lockfile resolution, and full compliance with PEP 621 standards.

---

## ADR 002: Resilience Against Cold Cloud PostgreSQL Instances
- **Date:** 2026-11-15
- **Status:** Accepted
- **Context:** Cloud serverless PostgreSQL tiers (e.g. Neon, Supabase) pause compute resources during inactivity. The initial connection handshake may encounter transient latency or timeouts while the compute node wakes up.
- **Alternatives Considered:**
  1. Fail immediately on first timeout.
  2. Implement retries with exponential backoff in diagnostics (`scripts/check_env.py`) and health check (`/health`).
- **Decision:** Configure short retries and enable `pool_pre_ping=True` in SQLAlchemy.
- **Rationale:** Eliminates false-positive outage reports during cold starts while compute instances initialize.

---

## ADR 003: Dedicated Direct Connection for DDL Migrations (Alembic)
- **Date:** 2026-11-15
- **Status:** Accepted
- **Context:** Transaction poolers (e.g. PgBouncer in transaction mode) common in Neon and Supabase reject or break transactional DDL operations such as `CREATE EXTENSION` or schema alterations.
- **Alternatives Considered:**
  1. Force the pooled URL for both the API and Alembic.
  2. Support `DATABASE_URL_DIRECT` for Alembic migrations, falling back to `DATABASE_URL` if direct is unset.
- **Decision:** Support `DATABASE_URL_DIRECT` in `migrations/env.py`.
- **Rationale:** Guarantees that spatial extension installations (PostGIS) and table modifications run directly against the primary node without pooler interference.

---

## ADR 004: Strict Test Isolation Without SQLite
- **Date:** 2026-11-15
- **Status:** Accepted
- **Context:** Because AgroSight heavily leverages native PostGIS geometric types (`Geometry`, GIST indexes), SQLite is incompatible without external C extensions (SpatiaLite) whose behavior diverges from production PostgreSQL.
- **Alternatives Considered:** In-memory SQLite with SpatiaLite mocks vs real PostgreSQL + PostGIS via `TEST_DATABASE_URL`.
- **Decision:** Prohibit SQLite. All database integration tests run exclusively against a dedicated `TEST_DATABASE_URL` with per-test transactional rollback via pytest fixtures in `conftest.py`.
- **Rationale:** Complete scientific and architectural parity between the test suite and production deployments.

---

## ADR 005: Regional NASA POWER Daily Ingestion & Persistence
- **Date:** 2026-11-15
- **Status:** Accepted
- **Context:** The NASA POWER regional API provides FeatureCollections of gridded coordinates across date intervals. Player requests must be served without issuing live upstream requests to NASA servers.
- **Decision:** Ingest and persist grid points per day into the `indicators` table, storing latitude, longitude, unit, category, `is_synthetic`, and mandatory foreign key to `datasets`. Audit runs in `ingestion_runs`. Enforce uniqueness on `(dataset_id, region_id, latitude, longitude, observed_at)` for idempotent upserts.
- **Rationale:** Preserves native spatial grid resolution and provenance without storing heavy raster tiles in the relational schema.
- **Limitations:** Spatial points are filtered by the region AOI polygon. Raw raster COG files remain reserved for object storage in future milestones.
