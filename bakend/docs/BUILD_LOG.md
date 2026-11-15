# AgroSight Fair Space API — Build Log

Registo sequencial e detalhado do desenvolvimento de cada passo do backend.

---

## Passo 0.1 — Estrutura Inicial e Tooling
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Configuração da estrutura modular do projeto, `pyproject.toml` gerido com `uv`, tooling de qualidade (`ruff`, `mypy`, `pytest`), `.gitignore` defensivo, documentação inicial e branch `dev`.
- **Ficheiros criados/alterados:**
  - `pyproject.toml`
  - `uv.lock`
  - `.gitignore`
  - `README.md`
  - `docs/BUILD_LOG.md`
  - `app/main.py`
  - `tests/test_init.py`
  - Estrutura de pastas modular (`app/core`, `app/modules/*`, `app/shared/*`, `migrations`, `seeds`, `scripts`, `storage`, `tests`, `docs`, `extras`)
- **Erros e Correções:**
  - Nenhum.
- **Resultado dos Testes e Linters:**
  - `pytest`: 1 passou / 0 falhas (tempo: 0.77s)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 24 files already formatted
  - `mypy app`: Success (0 issues in 19 source files)
  - `mypy tests`: Success (0 issues in 2 source files)

---

## Passo 0.2 — Configuração de Ambiente e Diagnóstico de BD
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Criação do `.env.example` completo com as variáveis documentadas e implementação do `scripts/check_env.py` para diagnóstico de conectividade com PostgreSQL e PostGIS na cloud com retry automático para instâncias suspensas.
- **Ficheiros criados/alterados:**
  - `.env.example`
  - `scripts/check_env.py`
  - `scripts/__init__.py`
  - `tests/test_check_env.py`
  - `pyproject.toml` (adicionadas dependências: `sqlalchemy`, `geoalchemy2`, `psycopg[binary]`, `alembic`, `explicit_package_bases`)
  - `uv.lock`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *Ruff F541:* f-string sem placeholders em `scripts/check_env.py` -> corrigido para string regular.
  - *Mypy module resolution:* scripts sem package base -> adicionado `scripts/__init__.py` e `explicit_package_bases = true`.
  - *Mypy arg-type:* estreitamento de tipos para variáveis de ambiente obrigatórias com `assert`.
- **Resultado dos Testes e Linters:**
  - `pytest`: 6 passaram / 0 falhas (tempo: 0.40s)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 27 files already formatted
  - `mypy app scripts tests`: Success (0 issues in 24 source files)

---

## Passo 0.3 — Configuração Central, Conectividade de Base de Dados e Endpoint /health
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Implementação de `app/core/config.py` com `pydantic-settings`, `app/core/database.py` com pool e retries resilientes a instâncias cloud suspensas, e endpoints `GET /health` e `GET /api/v1/health` reportando integridade da API, PostgreSQL e PostGIS.
- **Ficheiros criados/alterados:**
  - `app/core/config.py`
  - `app/core/database.py`
  - `app/main.py`
  - `tests/test_health.py`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *Mock de propriedade imutável:* tentativa de fazer `patch` direto em `@property sync_database_url` causou `AttributeError` por ausência de deleter no Pydantic -> corrigido testando `get_engine("")` diretamente com `ValueError`.
- **Resultado dos Testes e Linters:**
  - `pytest`: 14 passaram / 0 falhas (tempo: 0.52s)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 30 files already formatted
  - `mypy app scripts tests`: Success (0 issues in 27 source files)

---

## Passo 0.4 — Configuração do Alembic, Primeira Migração PostGIS e Fixtures de Teste
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Configuração do Alembic para migrações DDL seguras (preferindo `DATABASE_URL_DIRECT` sem pooler), criação da migração `0001` habilitando a extensão `postgis`, isolamento transacional nos testes com fixtures em `tests/conftest.py`, e validação automatizada da cadeia de migrações.
- **Ficheiros criados/alterados:**
  - `alembic.ini`
  - `migrations/env.py`
  - `migrations/script.py.mako`
  - `migrations/versions/0001_enable_postgis.py`
  - `migrations/__init__.py`
  - `migrations/versions/__init__.py`
  - `tests/conftest.py`
  - `tests/test_migrations.py`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *Alembic context import sem runner:* importar `get_migration_url` a partir de `migrations.env` em testes falhava com `AttributeError: module 'alembic.context' has no attribute 'config'` -> protegido com `getattr(context, "config", None)` permitindo imports em testes unitários.
  - *Deprecation warning de path separator:* adicionado `path_separator = os` no `alembic.ini`.
- **Resultado dos Testes e Linters:**
  - `pytest`: 17 passaram / 0 falhas (tempo: 0.20s)
  - `alembic heads`: 0001 (head)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 36 files already formatted
  - `mypy app scripts tests migrations`: Success (0 issues in 33 source files)

---

## Passo 1.1 — Modelo User, Repositório e Migração da Tabela users
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Criação do modelo ORM `User` (com UUID como chave primária, email único, hash de senha, role padrão 'player', idioma de preferência e timestamps UTC), repositório desacoplado `UserRepository` e migração Alembic `0002_create_users_table.py`.
- **Ficheiros criados/alterados:**
  - `app/modules/users/models.py`
  - `app/modules/users/__init__.py`
  - `app/modules/users/repository.py`
  - `migrations/versions/0002_create_users_table.py`
  - `migrations/env.py`
  - `tests/test_users_model.py`
  - `tests/test_migrations.py`
  - `pyproject.toml` (adicionados `argon2-cffi` e `pyjwt[crypto]`)
  - `uv.lock`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *Alembic heads assertion:* teste de migração esperava apenas revisão 0001; atualizado para cadeia sequencial 0001 -> 0002 (head).
  - *Valores padrão em memória no ORM:* instanciação do modelo `User` sem passagem explícita de `role` retornava `None` em memória antes do commit; implementado construtor `__init__` que inicializa os defaults (`role='player'`, `preferred_language='pt'`, `is_active=True`, timestamps UTC).
  - *Ruff UP017 & I001:* modernização para `datetime.UTC` (Python 3.12) e ordenação de imports no `migrations/env.py`.
- **Resultado dos Testes e Linters:**
  - `pytest`: 22 passaram / 0 falhas (tempo: 0.22s)
  - `alembic heads`: 0002 (head)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 41 files already formatted
  - `mypy app scripts tests migrations`: Success (0 issues in 37 source files)

---

## Passos 1.2 e 1.3 — Registo, Autenticação com Argon2 e Tokens JWT (Access/Refresh)
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Implementação de hashing e verificação de senhas com Argon2id em `app/core/security.py`, emissão e validação de tokens JWT (access e refresh), tratamento uniforme de exceções de domínio (`{"error": {"code", "message", "details"}}`), schemas Pydantic de auth, serviço `AuthService`, e endpoints `POST /auth/register`, `POST /auth/login` e `POST /auth/refresh`.
- **Ficheiros criados/alterados:**
  - `app/core/security.py`
  - `app/shared/exceptions/base.py`
  - `app/shared/exceptions/__init__.py`
  - `app/modules/auth/schemas.py`
  - `app/modules/auth/service.py`
  - `app/modules/auth/router.py`
  - `app/main.py` (handlers globais de erro e montagem do router de auth)
  - `tests/test_security.py`
  - `tests/test_auth.py`
  - `pyproject.toml` (adicionado `email-validator`)
  - `uv.lock`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *Ruff B904:* tratamento de exceções internas exigia encadeamento explícito com `from err` -> corrigido em `decode_token` e `refresh`.
  - *Ruff B008:* chamadas de `Depends` em defaults de função no router -> refatorado para o padrão moderno `Annotated[..., Depends(...)]`.
  - *StarletteDeprecationWarning:* substituído `HTTP_422_UNPROCESSABLE_ENTITY` por `HTTP_422_UNPROCESSABLE_CONTENT`.
- **Resultado dos Testes e Linters:**
  - `pytest`: 34 passaram / 0 falhas (tempo: 0.95s)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 48 files already formatted
  - `mypy app scripts tests migrations`: Success (0 issues in 44 source files)

---

## Passo 1.4 — Perfil do Utilizador (/users/me) e Controlo de Permissões (RBAC)
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Implementação das dependências de segurança `get_current_user` e `require_role` em `app/modules/auth/dependencies.py`, schemas e serviço `UserService` para atualização de perfil, e endpoints `GET /users/me`, `PATCH /users/me` e `GET /users/admin/ping`.
- **Ficheiros criados/alterados:**
  - `app/modules/auth/dependencies.py`
  - `app/modules/users/schemas.py`
  - `app/modules/users/service.py`
  - `app/modules/users/router.py`
  - `app/main.py` (montagem do router `/users`)
  - `tests/test_users_me.py`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *Dependency override generator:* substituição de gerador `get_db` por lambda causava falha na resolução assíncrona; ajustado para função geradora `override_get_db`.
  - *FastAPI Bearer header parsing no teste:* fixture de teste precisava anotar `HTTPAuthorizationCredentials` com `Depends(http_bearer)` para extração do cabeçalho `Authorization`.
  - *Ruff F401:* remoção de imports não utilizados em `router.py` e `test_users_me.py`.
- **Resultado dos Testes e Linters:**
  - `pytest`: 38 passaram / 0 falhas (tempo: 1.29s)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 53 files already formatted
  - `mypy app scripts tests migrations`: Success (0 issues in 49 source files)

---

## Passo 2.1 — Modelos Geoespaciais (regions, districts, communities) e Migração com Índices GIST
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Criação dos modelos ORM `Region`, `District` e `Community` com GeoAlchemy2 (SRID 4326), repositórios desacoplados com extração GeoJSON via `ST_AsGeoJSON`, e migração Alembic `0003_create_regions_districts_communities.py` com índices GIST espaciais e FK `users.selected_region_id`.
- **Ficheiros criados/alterados:**
  - `app/modules/regions/models.py`
  - `app/modules/regions/__init__.py`
  - `app/modules/regions/repository.py`
  - `migrations/versions/0003_create_regions_districts_communities.py`
  - `migrations/env.py`
  - `tests/test_regions_model.py`
  - `tests/test_migrations.py`
  - `pyproject.toml` (adicionado `shapely`)
  - `uv.lock`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *Ruff E501:* quebra de linha em docstring e string GeoJSON longa em `repository.py` e `test_regions_model.py`.
- **Resultado dos Testes e Linters:**
  - `pytest`: 45 passaram / 0 falhas (tempo: 1.48s)
  - `alembic heads`: 0003 (head)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 57 files already formatted
  - `mypy app scripts tests migrations`: Success (0 issues in 53 source files)

---

## Passo 2.2 — Importação de Camadas Nacionais (CENACARTA 2017) e Seeds de AOI
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Registo rigoroso da ficha da fonte CENACARTA 2017 em `docs/DATA_SOURCES.md`, criação dos GeoJSONs canónicos de AOI das 3 regiões confirmadas (`seeds/aoi/{gaza,zambezia,tete}.geojson`) com buffer e `is_proposed_study_area: true` (mantendo Maputo pendente de confirmação), script de validação e importação `scripts/import_national_layers.py`, e script de seed idempotente `scripts/seed.py` para popular regiões, distritos e comunidades.
- **Ficheiros criados/alterados:**
  - `docs/DATA_SOURCES.md`
  - `seeds/aoi/gaza.geojson`
  - `seeds/aoi/zambezia.geojson`
  - `seeds/aoi/tete.geojson`
  - `scripts/seed.py`
  - `scripts/import_national_layers.py`
  - `tests/test_seeds_and_layers.py`
  - `pyproject.toml` (adicionado `types-shapely`)
  - `uv.lock`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *ImportError SessionLocal:* `app/core/database.py` expõe `get_session_factory()` em vez de `SessionLocal` direto -> adaptado nos scripts.
  - *Mypy import-untyped:* shapely sem stubs de tipo -> adicionado `types-shapely` às dependências de desenvolvimento com `uv`.
  - *Ruff E501:* linhas longas em descrições e asserções -> quebradas para limite de 100 caracteres.
- **Resultado dos Testes e Linters:**
  - `pytest`: 54 passaram / 0 falhas (tempo: 1.43s)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 61 files already formatted
  - `mypy app scripts tests migrations`: Success (0 issues in 56 source files)

---

## Passo 2.3 — Endpoints de Regiões, Distritos, Comunidades e Mapa GeoJSON
- **Data:** 2026-11-15
- **Estado:** ✅ Concluído
- **Objetivo:** Implementação dos schemas Pydantic v2 paginados (`items`, `total`, `limit`, `offset`), serviço de domínio `RegionService`, router FastAPI em `/api/v1/regions`, e endpoints: `GET /regions`, `GET /regions/{id}`, `GET /regions/{id}/districts`, `GET /regions/{id}/communities` e `GET /regions/{id}/map` (GeoJSON Feature).
- **Ficheiros criados/alterados:**
  - `app/modules/regions/schemas.py`
  - `app/modules/regions/service.py`
  - `app/modules/regions/router.py`
  - `app/modules/regions/repository.py`
  - `app/main.py` (montagem de `regions_router`)
  - `tests/test_regions_endpoints.py`
  - `docs/BUILD_LOG.md`
- **Erros e Correções:**
  - *FastAPI dependency resolution sem BD:* teste de UUID inválido falhava antes da validação porque `get_db` tentava aceder a `DATABASE_URL` não configurada -> configurado mock explícito na fixture de teste.
  - *Ruff E501:* strings de descrição em schemas e router excediam 100 caracteres -> quebradas em tuplos de strings.
- **Resultado dos Testes e Linters:**
  - `pytest`: 61 passaram / 0 falhas (tempo: 1.17s)
  - `ruff check .`: All checks passed!
  - `ruff format --check .`: 65 files already formatted
  - `mypy app scripts tests migrations`: Success (0 issues in 60 source files)


