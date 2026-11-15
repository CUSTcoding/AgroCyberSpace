# Local Development & Contribution Guide

This guide walks through configuring your local development environment for **AgroCyberSpace / AgroSight**.

---

## 1. System Requirements

Ensure the following tools are installed:
- **Python:** Version 3.12 (managed automatically via `uv`)
- **uv:** Version >= 0.4.0 ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Node.js:** Version 20.x or higher LTS
- **Package Manager:** `npm` (>= 10) or `pnpm`
- **Database:** PostgreSQL (>= 15) with the `postgis` extension installed (or free cloud tier on Neon / Supabase).

---

## 2. Initial Setup

### 2.1 Clone the Repository
```bash
git clone https://github.com/your-org/AgroCyberSpace.git
cd AgroCyberSpace
```

### 2.2 Configure Environment Variables
Copy the consolidated environment configuration template:
```bash
cp .env.example .env
```
Open `.env` and configure your credentials:
- `DATABASE_URL`: Active PostgreSQL connection string with PostGIS enabled.
- `JWT_SECRET`: Random string at least 32 characters long.
- `VITE_API_URL`: Set to `/api/v1` for local development.

---

## 3. Backend Setup (`apps/backend`)

### 3.1 Install Python Dependencies
```bash
cd apps/backend
uv sync
```

### 3.2 Verify Database & PostGIS Health
Run the automated environment check to ensure your database connection and PostGIS extension are functional:
```bash
uv run python scripts/check_env.py
```

### 3.3 Apply Database Migrations
Run Alembic migrations to create tables and spatial indexes:
```bash
uv run alembic upgrade head
```

### 3.4 Seed Initial Data
Seed study regions, national crop statistics, soil classifications, and 12 game chapters:
```bash
uv run python scripts/seed.py
```

Validate chapter content integrity:
```bash
uv run python scripts/validate_content.py
```

### 3.5 Run the Backend Dev Server
```bash
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/api/v1/docs`
- Health check: `http://localhost:8000/health`

### 3.6 Run Tests & Code Quality Linters
```bash
# Run test suite
uv run pytest

# Linting and formatting
uv run ruff check .
uv run ruff format --check .

# Static type checking
uv run mypy app
```

---

## 4. Frontend Setup (`apps/frontend/web`)

### 4.1 Install Node Dependencies
```bash
cd apps/frontend/web
npm install
```

### 4.2 Start the Frontend Dev Server
```bash
npm run dev
```
Open `http://localhost:3000` (or the port output by Vite).

The development server includes a proxy configuration in `vite.config.ts` that routes `/api` and `/health` requests directly to `http://localhost:8000`.

### 4.3 Build and Lint
```bash
# Verify TypeScript and create production bundle in dist/
npm run build

# Run Oxlint
npx oxlint src
```

---

## 5. Working with Docker Locally

To spin up the entire application stack using Docker Compose:
```bash
cp infra/.env.example infra/.env
docker compose --env-file infra/.env -f infra/docker-compose.yml up --build -d
```
See the [Docker Guide](docker.md) for full operational instructions.
