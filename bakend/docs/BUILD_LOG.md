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
