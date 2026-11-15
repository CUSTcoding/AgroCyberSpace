# AgroSight & AgroSpace Documentation Hub

Welcome to the centralized documentation for **AgroSight Fair Space** (backend API) and **AgroSpace** (educational web client). This project was developed for the NASA Space Apps Challenge to empower smallholder farmers and agricultural communities in Mozambique (Gaza, Tete, and Zambézia) through satellite Earth Observation data and interactive storytelling.

---

## Documentation Map

| Document | Focus & Scope | Target Audience |
|---|---|---|
| [**Architecture Overview**](architecture.md) | High-level system design, monorepo layout, data pipelines, and design decisions | Developers, Architects, Reviewers |
| [**Docker & Containers**](docker.md) | Detailed guide to Dockerfiles, Docker Compose, networking, volumes, and health checks | DevOps, Operators, Developers |
| [**API Specification**](api.md) | FastAPI REST endpoints, OpenAPI schemas, authentication, and error standards | Frontend/Backend Engineers |
| [**Local Development Guide**](development.md) | Step-by-step setup, database migrations, testing, and seed data loading | Contributors, New Developers |
| [**Conventional Commits Guide**](conventional-commits.md) | Git commit conventions, message formatting, and automated workflow checks | All Contributors |

---

## Monorepo Layout

```
.
├── apps/
│   ├── backend/            # FastAPI Python 3.12 backend + PostGIS + Alembic
│   └── frontend/
│       └── web/            # Vite + React 19 + TypeScript web application
├── docs/                   # Centralized architectural & operational documentation
├── infra/                  # Infrastructure configurations:
│   ├── docker/             # Production Dockerfiles (backend, frontend)
│   ├── postgres/           # Database initialization scripts
│   ├── docker-compose.yml  # Production compose stack
│   └── docker-compose.dev.yml # Development compose stack with live reload
├── .github/                # CI/CD pipelines & GitHub Actions workflows
├── .dockerignore           # Root container build exclusions
├── .gitignore              # Root version control exclusions
└── .env.example            # Consolidated environment configuration template
```

---

## Quick Reference Links

- **Backend OpenAPI Docs (Swagger):** `http://localhost:8000/api/v1/docs`
- **Backend ReDoc:** `http://localhost:8000/api/v1/redoc`
- **Frontend Web Client:** `http://localhost:3000`
- **Backend Health Check:** `http://localhost:8000/health`
