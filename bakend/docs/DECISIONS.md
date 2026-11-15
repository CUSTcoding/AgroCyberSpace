# AgroSight Fair Space API — Architecture & Technical Decisions

Registo formal de decisões de arquitetura e implementação (ADR).

---

## ADR 001: Gestão de Dependências e Ambiente com uv
- **Data:** 2026-11-15
- **Contexto:** Necessidade de gerir dependências de forma reprodutível, rápida e determinística com Python 3.12.
- **Opções:** Poetry, Pipenv, pip-tools, uv.
- **Escolha:** `uv` com `pyproject.toml` e `uv.lock`.
- **Motivo:** Performance ordens de magnitude superior, suporte integrado a download de toolchains Python oficiais (`cpython-3.12`), resolução rigorosa de dependências e compatibilidade total com os padrões PEP 621.

---

## ADR 002: Resiliência a Instâncias PostgreSQL Cloud Suspensas
- **Data:** 2026-11-15
- **Contexto:** Bases de dados em camadas gratuitas de clouds como Neon e Supabase suspendem a computação após períodos de inatividade. O primeiro pacote SYN/handshake pode sofrer latência ou timeout transitório.
- **Opções:** 
  1. Falhar imediatamente sem retry.
  2. Implementar retries com backoff curto no diagnóstico (`scripts/check_env.py`) e no health check (`/health`).
- **Escolha:** Implementação de retries configuráveis (com espera curta) e `pool_pre_ping=True` no SQLAlchemy.
- **Motivo:** Evita falsos positivos de indisponibilidade quando o nó da cloud está a acordar da suspensão.

---

## ADR 003: Separação de Conexão Direta para Migrações DDL (Alembic)
- **Data:** 2026-11-15
- **Contexto:** Connection poolers (ex.: PgBouncer em modo `transaction`) comuns no Neon/Supabase bloqueiam ou falham em certas operações DDL transacionais ou comandos específicos como `CREATE EXTENSION`.
- **Opções:**
  1. Forçar a mesma URL com pooler para a API e para o Alembic.
  2. Suportar `DATABASE_URL_DIRECT` para o Alembic, caindo para `DATABASE_URL` quando não configurada.
- **Escolha:** Suporte nativo no `migrations/env.py` para priorizar `DATABASE_URL_DIRECT`.
- **Motivo:** Garante que operações de esquema e extensões como PostGIS corram diretamente contra o primário sem interferência do pooler.

---

## ADR 004: Isolamento Estrito de Testes sem SQLite
- **Data:** 2026-11-15
- **Contexto:** Como o projeto utiliza tipos geométricos PostGIS nativos (`Geometry`, índices GIST), SQLite não é compatível sem extensões C externas complexas (SpatiaLite) que divergem do comportamento do PostgreSQL.
- **Opções:** SQLite em memória vs PostgreSQL real com PostGIS em `TEST_DATABASE_URL`.
- **Escolha:** Proibição de SQLite. Testes de banco correm exclusivamente contra `TEST_DATABASE_URL` dedicada, com rollback transacional por teste via fixtures em `conftest.py`.
- **Motivo:** Fidelidade científica e técnica absoluta com o ambiente de produção.
