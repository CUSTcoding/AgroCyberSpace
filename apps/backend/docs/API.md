# AgroSight API Reference

Status of this reference: 2026-11-15. The live OpenAPI document is the contract of record at `/api/v1/openapi.json`; Swagger UI is available at `/api/v1/docs` and ReDoc at `/api/v1/redoc`.

## Base URL and conventions

- API base path: `/api/v1`
- Health: `/health` and `/api/v1/health`
- IDs are UUIDs unless stated otherwise.
- JSON request and response bodies use UTF-8.
- Protected routes accept `Authorization: Bearer <access_token>` from `/auth/login` or `/auth/register`.
- Paginated responses use `items`, `total`, `limit`, and `offset` where implemented. `limit` and `offset` constraints are described in OpenAPI.
- Domain and request errors use `{"error":{"code":"...","message":"...","details":...}}`.
- The API does not fetch NASA/USGS data while serving player requests. Ingestion is a separate operator command.

## Authentication and account

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/auth/register` | Public | Create player account and issue tokens |
| POST | `/auth/login` | Public | Authenticate and issue access/refresh tokens |
| POST | `/auth/refresh` | Public with refresh token | Issue refreshed tokens |
| GET | `/users/me` | Player | Read current account |
| PATCH | `/users/me` | Player | Update allowed profile fields |
| GET | `/users/admin/ping` | Admin | Verify admin role access |

## Regions

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/regions` | Public | List study regions; supports pagination |
| GET | `/regions/{region_id}` | Public | Read region metadata |
| GET | `/regions/{region_id}/districts` | Public | List districts attached to the study region |
| GET | `/regions/{region_id}/communities` | Public | List communities attached to the region |
| GET | `/regions/{region_id}/map` | Public | Return the region boundary as GeoJSON |
| GET | `/regions/{region_id}/map-config` | Public | Return bounding box and configured layers; currently `layers` can be empty |
| GET | `/regions/{region_id}/indicators` | Public | Return available agricultural crop statistics at district level, with source/campaign |

`/regions/{region_id}/indicators` currently exposes district crop-stat rows, not climate indicators or parcel observations. Climate profile and climate comparison routes are not implemented.

## Game and content

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/game/chapters?region_id=` | Player | List chapters with the caller's unlock state |
| GET | `/game/chapters/{chapter_id}?region_id=` | Player | Read chapter, ordered lessons, and missions |
| GET | `/game/lessons/{lesson_id}` | Public | Read lesson text and provenance |
| GET | `/game/missions?chapter_id=&region_id=` | Public | List missions |
| GET | `/game/missions/{mission_id}` | Public | Read mission without answer rules |
| POST | `/game/lessons/{lesson_id}/complete` | Player | Record lesson completion |
| POST | `/game/missions/{mission_id}/start` | Player | Start a mission |
| POST | `/game/missions/{mission_id}/submit` | Player | Submit `{"choice":"..."}` and receive authored-rule score/feedback |
| POST | `/game/missions/{mission_id}/field-observation` | Player | Record `observed_condition` and optional `note` during an active mission |
| GET | `/game/progress?limit=&offset=` | Player | Read own paginated progress |
| GET | `/game/achievements` | Player | Read achievement catalogue and own unlock state |
| GET | `/content/manifest?region_id=&language=pt` | Public | Return IDs and versions for verified content; regional content also needs published chapter status |

A mission submission is accepted only after it has started. A completed mission cannot be submitted again. Its answer key is not returned by the read API.

## Earth Observation data

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/earth-observation/datasets?limit=&offset=` | Public | List persisted dataset metadata and versions |
| GET | `/earth-observation/metadata/{dataset_id}` | Public | Read complete source metadata for a dataset |
| GET | `/earth-observation/indicators?region_id=&indicator_type=&start=&end=&limit=&offset=` | Public | Query persisted indicator points |
| GET | `/earth-observation/timeseries?region_id=&indicator_type=&start=&end=&limit=&offset=` | Public | Same point/date query contract as indicators |

NASA POWER rows include `source`, `dataset_version`, `unit`, `category`, `is_synthetic`, latitude/longitude, and a `resolution_warning`. Ingestion retains grid points covered by the region AOI; this is not full-cell raster clipping. POWER is gridded regional context, not a local station measurement or parcel observation. `data_as_of` reflects the newest observation returned in the requested page.

The first implementation stores values and source metadata in PostgreSQL. Raster/image endpoints, `layers`, TileJSON, and map tiles are not implemented yet.

## Template explanations

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/ai/explain` | Public | Explain allow-listed structured data context using deterministic Portuguese/English templates |
| POST | `/ai/hint` | Public | Return a field-observation hint using deterministic templates |
| GET | `/ai/health` | Public | Report the active local template provider |

AI request models forbid extra fields and accept only category, source, dataset version, limitations, and optional resolution warning. No external LLM provider is called.

## NASA POWER ingestion operation

The API is read-only for Earth Observation. An operator runs a separate ingestion command after applying migration `0006` to the intended database. See [POWER ingestion runbook](POWER_INGESTION.md). Do not point a migration command at a development/production database when intending to migrate the test database.

## Not implemented

The current API does not yet include climate profiles/comparisons, advisory endpoints, crop catalogue/planting windows, decision or simulation endpoints, imagery/layers/tiles, MODIS, GPM, Landsat, SMAP, GRACE, or admin CRUD. Do not treat the current district agricultural statistics as climate evidence.
