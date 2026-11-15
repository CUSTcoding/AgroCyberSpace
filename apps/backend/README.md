# AgroSight Fair Space — Backend API

Backend for **AgroSight Fair Space**: an educational game API developed for the NASA Space Apps Challenge that empowers Mozambican farmers to make data-informed agricultural decisions through Earth Observation data (NASA POWER, USGS, and national open datasets).

---

## 1. Technology Stack

- **Language:** Python 3.12
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic v2](https://docs.pydantic.dev/)
- **Database:** PostgreSQL + PostGIS (Cloud: Neon / Supabase)
- **ORM & Migrations:** SQLAlchemy 2.x + GeoAlchemy2 + Alembic (driver: `psycopg` v3 binary)
- **Package & Environment Manager:** [`uv`](https://docs.astral.sh/uv/)
- **Code Quality:** Ruff (linting & formatting), Mypy (strict type checking), Pytest + HTTPX

---

## 2. Directory Structure

```
apps/backend/
├── app/
│   ├── main.py             # FastAPI entrypoint, middleware, exception handlers, and router mounts
│   ├── core/               # Configuration, security/JWT, database engine, storage
│   ├── modules/            # Domain modules:
│   │   ├── auth/           # Registration, login, token refresh, and dependencies
│   │   ├── users/          # User profiles and admin checks
│   │   ├── regions/        # Study regions (Gaza, Tete, Zambézia), districts, and GeoJSON maps
│   │   ├── game/           # 12 Chapters, lessons, missions, progress, achievements, and manifest
│   │   ├── ai/             # Deterministic template-based agronomic hints and explanations
│   │   ├── earth_observation/ # Datasets metadata, timeseries, and indicators
│   │   ├── agriculture/    # Crop statistics and soil classification models
│   │   └── admin/          # Administrative operations
│   └── shared/             # Shared Pydantic schemas and domain exceptions
├── migrations/             # Alembic migration scripts (0001 through 0006)
├── seeds/                  # Seed data:
│   ├── aoi/                # Area of Interest GeoJSON polygons for Mozambique study regions
│   ├── content/            # 12 Chapter seeds, lessons, and authored mission challenges
│   └── agriculture/        # National crop statistics and soil units
├── scripts/                # Utility scripts:
│   ├── check_env.py        # Cloud database connectivity and PostGIS health diagnostics
│   ├── seed.py             # Database seed runner
│   ├── validate_content.py # Content integrity and schema validator
│   └── ingestion/          # NASA POWER and national layer ingestion scripts
├── storage/                # Local raster and COG storage (excluded from git)
├── tests/                  # Unit and integration test suite
└── docs/                   # Technical references and build logs:
    ├── API.md              # Complete API reference
    ├── DOCKER.md           # Optional Docker runtime guide
    ├── DATA_SOURCES.md     # Earth Observation & national data provenance
    ├── DECISIONS.md        # Architecture Decision Records (ADRs)
    ├── POWER_INGESTION.md  # NASA POWER ingestion runbook
    └── BUILD_LOG.md        # Engineering build log
```

---

## 3. API Documentation & Interactive Specs

Once the backend is running, interactive API documentation is available at:
- **Interactive Swagger UI:** `http://localhost:8000/api/v1/docs`
- **ReDoc Documentation:** `http://localhost:8000/api/v1/redoc`
- **OpenAPI Schema (JSON):** `http://localhost:8000/api/v1/openapi.json`
- **Health Check Endpoint:** `http://localhost:8000/health` (or `/api/v1/health`)

Detailed documentation guides:
- [API Reference](docs/API.md) — Endpoint specifications, request/response models, and error structures.
- [NASA POWER Ingestion](docs/POWER_INGESTION.md) — Operator instructions for regional meteorological ingestion.
- [Data Sources & Provenance](docs/DATA_SOURCES.md) — Metadata sheets for NASA and national datasets.
- [Architecture Decisions (ADRs)](docs/DECISIONS.md) — Formal engineering decisions.
- [Docker Runtime](docs/DOCKER.md) — Containerized deployment.

---

## 4. Local Setup & Execution

### Prerequisites
- Python 3.12 (managed automatically by `uv`)
- [`uv`](https://docs.astral.sh/uv/) (>= 0.4.0)
- PostgreSQL database with PostGIS extension enabled (e.g. Neon, Supabase, or local)

### Installation
From within `apps/backend/`:
```bash
# Sync all dependencies including dev tools
uv sync
```

### Environment Configuration
Copy `.env.example` to `.env` (or use the root `.env`):
```bash
cp .env.example .env
```
Ensure `DATABASE_URL` points to an active PostgreSQL instance with PostGIS enabled, and configure `JWT_SECRET`:
```ini
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://user:password@host/dbname?sslmode=require
JWT_SECRET=your_secure_random_string_at_least_32_characters
```

### Environment Diagnostics
Verify database connectivity and PostGIS installation:
```bash
uv run python scripts/check_env.py
```

### Database Migrations
Apply Alembic migrations to create tables and spatial indexes:
```bash
uv run alembic upgrade head
```

### Seed Initial Content
Seed study regions, national agricultural statistics, chapters, and missions:
```bash
uv run python scripts/seed.py
```

### Running the API Server
```bash
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```

---

## 5. Code Quality & Testing

Run all quality checks and tests:
```bash
# Linting with Ruff
uv run ruff check .

# Code formatting check
uv run ruff format --check .

# Strict static type checking
uv run mypy app

# Run full test suite
uv run pytest
```

---

## 6. Optional Docker Execution

Docker is optional for the backend. The service connects to a managed PostgreSQL/PostGIS database configured via `DATABASE_URL`; Compose does not start a local database.

1. Ensure `infra/.env` has a reachable `DATABASE_URL` and `JWT_SECRET`.
2. Start the container:
   ```bash
   docker compose --env-file infra/.env -f infra/docker-compose.yml up --build -d
   ```
3. For development with live reload:
   ```bash
   docker compose --env-file infra/.env -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build
   ```
