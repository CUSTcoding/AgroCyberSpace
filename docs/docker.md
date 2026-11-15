# Docker Containers & Deployment Guide

This guide provides technical reference documentation for the containerized architecture of **AgroSight** (FastAPI backend) and **AgroSpace** (React web frontend).

---

## 1. Container Overview & Topology

The containerized stack consists of two primary services connected over an internal Docker bridge network:

```mermaid
flowchart LR
    Client(["Web Browser"]) -->|Port 3000| Frontend["frontend (Nginx / React SPA)"]
    Frontend -->|Internal DNS http://backend:8000| Backend["backend (FastAPI / Uvicorn)"]
    Backend -->|SSL / External Network| CloudDB[("Cloud PostgreSQL + PostGIS")]
    Backend -->|Local Volume| Storage[("backend_storage volume")]
```

| Container | Image Tag | Base OS / Runtime | Port (Host:Container) | Purpose |
|---|---|---|---|---|
| **backend** | `agrosight-backend:local` | Python 3.12-slim (`ghcr.io/astral-sh/uv`) | `8000:8000` | REST API, PostGIS models, game engine, AI hints |
| **frontend** | `agrosight-frontend:local` | Alpine Linux 3.20 (`nginx:1.27-alpine`) | `3000:3000` | Static asset delivery, SPA routing, `/api` proxy |

---

## 2. Dockerfile Specifications

### 2.1 Backend Dockerfile (`apps/backend/Dockerfile`)
The backend uses a multi-stage, security-hardened production build:

```dockerfile
# Multi-stage Python 3.12 image
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /bin/uv
```

**Key Characteristics:**
- **Dependency Isolation:** Dependencies are locked and synchronized using `uv sync --frozen --no-dev`.
- **Non-Root Execution:** Runs under a dedicated unprivileged user (`appuser:10001`).
- **Lean Runtime:** Avoids packaging C compilers or unnecessary build artifacts in the final container layer.
- **Embedded Health Check:**
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
      CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
  ```

---

### 2.2 Frontend Dockerfile (`infra/docker/Dockerfile.frontend`)
The frontend uses a two-stage build separating Node compilation from runtime web serving:

- **Stage 1 (Builder):** `node:20-alpine` runs `npm ci` and `npm run build`, producing an optimized production bundle in `/app/dist`.
- **Stage 2 (Runner):** `nginx:1.27-alpine` serves the pre-rendered static files:
  - Custom Nginx configuration handles Single Page Application fallback (`try_files $uri $uri/ /index.html;`).
  - Automatically proxies `/api/` and `/health` to `http://backend:8000`.
  - Enables Gzip compression for text, CSS, JavaScript, and SVG assets.
  - Implements 1-year caching headers for immutable static assets.
  - **Embedded Health Check:**
    ```dockerfile
    HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
        CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
    ```

---

## 3. Docker Compose Configurations

The Compose definitions reside in `infra/`:

### 3.1 Production Stack (`infra/docker-compose.yml`)
Designed for standard container execution without source code mounting:

```yaml
services:
  backend:
    build:
      context: ../apps/backend
      dockerfile: Dockerfile
      args:
        UV_SYNC_ARGS: --no-dev
    image: agrosight-backend:local
    restart: unless-stopped
    environment:
      ENVIRONMENT: ${ENVIRONMENT:-production}
      DATABASE_URL: ${DATABASE_URL:?Set DATABASE_URL in infra/.env}
      JWT_SECRET: ${JWT_SECRET:?Set JWT_SECRET in infra/.env}
      CORS_ORIGINS: ${CORS_ORIGINS:-http://localhost:3000}
      STORAGE_BACKEND: local
      STORAGE_PATH: /app/storage
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    volumes:
      - backend_storage:/app/storage

  frontend:
    build:
      context: ../apps/frontend/web
      dockerfile: ../../../infra/docker/Dockerfile.frontend
      args:
        VITE_API_URL: /api/v1
    image: agrosight-frontend:local
    restart: unless-stopped
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    depends_on:
      backend:
        condition: service_healthy

volumes:
  backend_storage:
```

---

### 3.2 Development Stack (`infra/docker-compose.dev.yml`)
Overrides production settings to mount local source directories and enable hot reload:

```yaml
services:
  backend:
    build:
      args:
        UV_SYNC_ARGS: ""
    command:
      - uv
      - run
      - uvicorn
      - app.main:app
      - --host
      - 0.0.0.0
      - --port
      - "8000"
      - --reload
    volumes:
      - ../apps/backend:/app
      - backend_venv:/app/.venv
      - backend_storage:/app/storage

volumes:
  backend_venv:
```

---

## 4. Operational Runbook

### 4.1 Prerequisites
- Docker Engine >= 24.0
- Docker Compose v2 (e.g. `docker compose`)

### 4.2 Setup Environment
Create `infra/.env` by copying the template:
```bash
cp infra/.env.example infra/.env
```
Edit `infra/.env` and supply your database connection and security secret:
```ini
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://username:password@cloud-host.neon.tech/agrosight?sslmode=require
JWT_SECRET=super_secret_jwt_key_at_least_32_characters_long
CORS_ORIGINS=http://localhost:3000
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### 4.3 Starting Containers

#### Run in Production Mode:
```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml up --build -d
```

#### Run in Development Mode (Live Reload):
```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build
```

### 4.4 Verifying Service Status
Inspect the status and health check state:
```bash
docker compose -f infra/docker-compose.yml ps
```

Check real-time application logs:
```bash
# Follow both containers
docker compose -f infra/docker-compose.yml logs -f

# Follow backend only
docker compose -f infra/docker-compose.yml logs -f backend
```

Test endpoints via curl:
```bash
# Frontend health
curl -I http://localhost:3000/

# Backend health
curl http://localhost:8000/health
```

### 4.5 Applying Database Migrations Inside Container
To run Alembic migrations within the running backend container:
```bash
docker compose -f infra/docker-compose.yml exec backend uv run alembic upgrade head
```

### 4.6 Stopping and Teardown
To stop containers without losing local storage:
```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml down
```

> [!CAUTION]
> Do not pass the `-v` flag (`docker compose down -v`) unless you explicitly intend to delete the `backend_storage` persistent volume containing downloaded rasters and assets.

---

## 5. Troubleshooting & FAQ

### Database connection fails on startup
- **Cause:** Cloud PostgreSQL instance (Neon / Supabase) was asleep or SSL mode was omitted.
- **Fix:** Ensure `?sslmode=require` is appended to `DATABASE_URL` in `infra/.env`. The application retries connections automatically on boot.

### Port conflict on 8000 or 3000
- **Fix:** Change `BACKEND_PORT` or `FRONTEND_PORT` in `infra/.env` to alternate ports (e.g., `8080` or `3001`).

### CORS error when calling backend from custom origin
- **Fix:** Update `CORS_ORIGINS` in `infra/.env` to include your origin, e.g. `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`.
