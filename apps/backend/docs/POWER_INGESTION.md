# NASA POWER Daily Ingestion Runbook

Last verified against official POWER documentation: 2026-11-15.

## What this integration does

The operator command calls NASA POWER Daily Regional JSON, parses each grid feature and date, stores one value per dataset/region/grid coordinate/date, and records an `ingestion_runs` audit row. It does not call NASA from player-facing HTTP requests.

The API Daily documentation states regional requests use a bounding box, accept JSON, and allow one requested parameter per regional request. The official OpenAPI exposes POWER Daily v2.10.3, the regional response as a FeatureCollection, point coordinates, units in `parameters`, and fill value in `header`. Daily coverage is documented from 1981-01-01 to near-real-time. Community codes accepted by the current client are `ag`, `hy`, `sb`, and `re`.

## Prerequisites

1. Configure the backend environment with the intended PostgreSQL/PostGIS `DATABASE_URL`.
2. Set `DATABASE_URL_DIRECT` to the same **dedicated test database** when applying migrations for test validation. Alembic prefers `DATABASE_URL_DIRECT`; verify it does not point at development or production before migration.
3. Install dependencies with `uv sync`.
4. Confirm the region exists and has a boundary geometry. The ingestion command obtains its bounding box from the region map configuration; the importer filters returned grid-point coordinates against that AOI polygon before persistence.
5. Choose a POWER parameter after checking the current official parameter catalog and its units/resolution. The command does not choose agronomic parameters automatically.

## Apply schema

Migration `0006` creates `datasets`, `indicators`, and `ingestion_runs`. It has not been applied by this repository task. Only run the migration after checking the selected database URL:

```bash
uv run alembic upgrade head
```

Never run this against the development/cloud database as a substitute for the dedicated test database.

## Run one ingestion

```bash
uv run python -m scripts.ingestion.ingest_power \
  --region-id <region-uuid> \
  --parameter T2M \
  --start 2026-01-01 \
  --end 2026-01-03 \
  --community ag
```

`T2M` is shown as a parameter example in the official POWER API documentation; verify availability, units, and source resolution for the selected community before operational use. The command is manual and can be invoked by an external cron. No scheduler is configured by this backend.

## Read stored data

After ingestion succeeds:

- `GET /api/v1/earth-observation/datasets`
- `GET /api/v1/earth-observation/metadata/{dataset_id}`
- `GET /api/v1/earth-observation/timeseries?region_id={uuid}&indicator_type=T2M&start=2026-01-01&end=2026-01-03`

Responses retain dataset source/version, unit, date, grid coordinates, category and synthetic status. Resolution warnings state that grid values are not field measurements.

## Idempotence and audit

The indicator uniqueness key is dataset version + region + longitude + latitude + date. Re-running the same request updates existing values instead of adding duplicate point/date rows. `ingestion_runs` records status, request period, dataset version, checksum, start/finish time, and error text on failure.

The run checksum describes normalized values and is stable across reruns; generated row UUIDs are excluded.

## Limits and scientific cautions

- The request uses the region bounding box, then retains only POWER grid points whose coordinates are covered by the AOI polygon. This is point-center filtering, not raster clipping or area-weighted clipping of grid cells; a retained cell can still partly extend outside the AOI.
- Native source resolution varies by POWER parameter; a generic resolution label is retained until parameter metadata is validated. Do not interpret these values as parcel-level observations.
- POWER data are analysis-ready gridded meteorological/solar data and must not be described as measurements from a local station.
- Parameter/community availability, units, data-source lineage and redistribution terms must be checked in official documentation before agronomic decisions or wider redistribution.
- The current service does not compute climatology, rainfall onset, dry spells, heat stress, or recommendations from these values.
- API ingestion tests use mocked responses. A live NASA request and a real PostgreSQL upgrade must be verified separately in an environment with network and dedicated test database access.

## Troubleshooting

- **No region boundary:** check the region seed/import; the command refuses to build a request without a bounding box.
- **HTTP 422:** verify parameter, community, date interval, and bounds against the current POWER configuration/API documentation.
- **HTTP 429:** stop repeated requests and retry later; avoid repeatedly requesting the same grid region.
- **No rows stored:** inspect `ingestion_runs.error`, response fill values, and the selected interval.
- **Database table missing:** migration `0006` has not been applied to the configured database.
