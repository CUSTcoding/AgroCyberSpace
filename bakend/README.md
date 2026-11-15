# AgroSight Fair Space — Backend API

Backend do **AgroSight Fair Space**: jogo educativo desenvolvido no contexto do desafio NASA Space Apps que capacita agricultores moçambicanos a tomar decisões agrícolas fundamentadas através de dados de observação da Terra (NASA, USGS e dados nacionais abertos).

## 1. Stack Tecnológica
- **Linguagem:** Python 3.12
- **Framework Web:** FastAPI + Pydantic v2
- **Base de Dados:** PostgreSQL + PostGIS (Cloud: Neon / Supabase)
- **ORM / Migrações:** SQLAlchemy 2.x + GeoAlchemy2 + Alembic (driver `psycopg` v3)
- **Gestor de Dependências:** `uv`
- **Qualidade de Código:** Ruff (lint & format), Mypy (tipagem estrita), Pytest + HTTPX

## 2. Estrutura do Projeto
```
bakend/
├── app/
│   ├── main.py
│   ├── core/           # Configuração, segurança, base de dados, storage
│   ├── modules/        # Módulos funcionais (auth, game, regions, earth_observation, etc.)
│   └── shared/         # Schemas e exceções transversais
├── migrations/         # Migrações Alembic
├── seeds/              # AOIs, conteúdos de capítulos/missões, dados agronómicos
├── scripts/            # Verificação de ambiente, ingestão e utilitários
├── storage/            # Rasters COG/GeoTIFF locais (fora do Git)
├── tests/              # Testes unitários e de integração
└── docs/               # Documentação técnica e registo de construção
```

## 3. Instalação e Execução

### Requisitos
- `uv` (>= 0.4.0)
- Python 3.12 (gerido automaticamente pelo `uv`)

### Instalação de Dependências
```bash
uv sync
```

### Verificação de Qualidade
```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest
```

### Executar a API em Modo de Desenvolvimento
```bash
uv run fastapi dev app/main.py
```
