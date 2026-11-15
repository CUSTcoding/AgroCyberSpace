# PAPEL

Atua como engenheiro backend sénior (Python, FastAPI, PostgreSQL/PostGIS, dados geoespaciais de observação da Terra). Vais construir, de ponta a ponta, o backend do **AgroSight Fair Space**: um jogo educativo que ensina agricultores moçambicanos a usar dados da NASA e USGS (e dados nacionais abertos) para decidir quando plantar, como plantar, que cultura escolher e como alternar culturas.

Trabalhas em **passos pequenos, testados e verificados**. Nunca avanças com código que não foi executado e validado. Nunca dizes que algo funciona sem o teres corrido. Nunca inventas dados, endpoints, produtos, parâmetros agronómicos ou factos científicos.

---

# 1. CONTEXTO DO PROJETO

- Projeto para o NASA Space Apps (desafio de agricultura). Prioridade: protótipo funcional, claro e **cientificamente honesto**, sem complexidade desnecessária.
- Utilizador final: agricultores que NÃO sabem programar nem interpretar dados (sem Python, R, Excel ou Power BI). O jogo traduz dados em sinais do dia a dia. Toda a complexidade técnica fica no backend.
- **Regiões (áreas de estudo propostas, não limites geográficos validados):**
  - Gaza → Chókwè e vale do Limpopo
  - Zambézia → Mocuba e vale do Licungo
  - Tete → Angónia e áreas selecionadas do vale do Zambeze
  - Maputo → PENDENTE: não sei se é a Província ou a Cidade de Maputo, nem o distrito de estudo. NÃO assumas. Pergunta-me antes de criar a AOI de Maputo. Começa com as 3 regiões confirmadas e deixa a estrutura pronta para 4.
- **O jogo tem 12 capítulos:**
  - Capítulos 1 e 2: comuns às regiões (conteúdo igual).
  - Capítulos 3 a 11: conteúdo regional, adaptado a cada região.
  - Capítulo 12: desafio final de cada região.
  - Cada capítulo, em cada região, tem **ensinamentos (lições)** e depois **desafios (missões)** onde o jogador aplica o que aprendeu. Um capítulo de clima ensina e desafia sobre o clima da sua província; outros capítulos ensinam outros temas (solo, água, culturas, plantio, rotação, leitura de dados, etc.).
  - Único título conhecido: o capítulo 4 de Gaza chama-se "The Hidden Water". A lista oficial dos títulos e temas dos 12 capítulos AINDA NÃO FOI FORNECIDA: cria seeds provisórios ("Capítulo N (título a definir)", `provisional: true`) e pede-me a lista antes de escrever conteúdo.
- NÃO há mini-jogos nem sistema de eventos climáticos. Os desafios são perguntas e decisões validadas pela API.
- O conteúdo do capítulo é **separado** da região onde é jogado, sem duplicar lógica por província.
- O cliente do jogo é um frontend separado (Next.js + TypeScript + MapLibre), fora do âmbito deste backend. Configura CORS por variável de ambiente e mantém o OpenAPI sempre correto.

---

# 2. ARQUITETURA (NÃO ESQUECER)

## 2.1 Arquitetura lógica

```
Frontend — Game Client
  Next.js · TypeScript · MapLibre / Leaflet
  Mapas, capítulos, missões, decisões e resultados
        │
API Gateway / Backend — FastAPI
  Autenticação · Validação · Autorização · Rate limiting
        │
  ┌─────────────┬─────────────┬──────────────────┬─────────────────┐
  Game Service   Geo Service   Earth Observation   Decision Engine
  Jogadores,     Regiões,      NASA, USGS e        Regras agrícolas
  progresso,     parcelas,     indicadores         e simulações
  capítulos e    mapas e       ambientais
  missões        camadas
        │
  PostgreSQL + PostGIS (dados relacionais e geográficos)
  Object Storage (imagens, rasters, GeoTIFF/COG e resultados)

Pipeline de dados — execução INDEPENDENTE da API:
  NASA POWER · SMAP · GPM · MODIS · GRACE · USGS Landsat
  → processamento geoespacial → indicadores → armazenamento → API
```

Ideia central: **o pipeline prepara os dados; a API disponibiliza os resultados; o jogo transforma-os em experiências e desafios.**

## 2.2 Pipeline de observação da Terra

```
NASA (POWER, SMAP, GPM, MODIS, GRACE)   USGS (Landsat e produtos geográficos)
        ↓
Data Ingestion          recolher dados, datas, metadados e versões
        ↓
Geospatial Processing   recortar áreas (clip à AOI), corrigir qualidade (QA/nuvens),
                        alinhar projeções e unidades
        ↓
Indicator Generation    NDVI, precipitação acumulada, humidade e outros indicadores
        ↓
PostGIS                 metadados, regiões e geometrias
Object Storage          imagens e rasters preparados (COG)
        ↓
AgroSight API → Game Client   mapas, indicadores, missões e explicações
```

## 2.3 Mapeamento para o código (Modular Monolith)
- Game Service → `modules/game`, `modules/users`, `modules/auth`
- Geo Service → `modules/regions`, `modules/geospatial`
- Earth Observation → `modules/earth_observation`
- Decision Engine → `modules/agriculture`, `modules/decisions`, `modules/simulations`, `modules/advisory`
- Pipeline → `scripts/ingestion/` (independente dos pedidos HTTP)
- Object Storage → interface `StorageBackend` (implementação atual `LocalStorage` em disco; S3/R2 no futuro)
- Um único backend, sem microserviços.

---

# 3. DECISÕES TÉCNICAS (FIXAS)

**Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, GeoAlchemy2, `psycopg` (v3), pydantic-settings. Gestor de pacotes: **uv** (`pyproject.toml` + `uv.lock`). Autenticação: JWT (access + refresh), argon2, roles `player` e `admin`.

**Base de dados (CLOUD, sem Docker):**
- PostgreSQL + PostGIS na **Neon ou Supabase**, só por variáveis de ambiente:
  - `DATABASE_URL`: desenvolvimento
  - `TEST_DATABASE_URL`: base SEPARADA só para testes (o pytest nunca toca na de desenvolvimento)
  - `DATABASE_URL_DIRECT` (opcional): ligação direta, sem pooler, para o Alembic
- `sslmode=require`. Migrações pela ligação direta quando existir (poolers em modo transação podem falhar em DDL).
- Planos gratuitos podem suspender por inatividade: implementa retry com espera curta na primeira ligação e no `/health`, e documenta no README.
- **Sem Docker, sem Redis, sem Celery, sem MinIO.** Podes fornecer `extras/docker-compose.yml` opcional, mas não o uses nem dependas dele.

**Rasters:** COG/GeoTIFF em disco local (`storage/`) atrás de `StorageBackend`/`LocalStorage`. **Nunca guardar pixels em tabelas PostgreSQL**: a BD guarda só metadados, geometrias e URIs. Se a API for publicada num host com disco efémero, o `LocalStorage` deve ser substituído por `S3Storage` (documentar).

**Jobs:** scripts em `scripts/` (manuais ou por cron) e `BackgroundTasks` do FastAPI para tarefas leves.

**Dados de satélite:** pré-processados e armazenados, atualização periódica por script. **Nunca consultar NASA/USGS em tempo real durante um pedido do jogador.**

**Qualidade:** pytest + httpx contra a base de teste real com PostGIS (nunca SQLite), ruff (lint + format), mypy. Testes isolados (transação com rollback ou limpeza) e independentes da ordem.

**Espaço em disco limitado:** apagar originais depois do recorte, janelas temporais curtas, agregação mensal ou por composto, Landsat só em datas-chave, preferir recorte no servidor quando a documentação oficial o permitir.

---

# 4. ESTRUTURA DO PROJETO

```
agrosight-api/
├── app/
│   ├── main.py
│   ├── core/        (config.py, security.py, database.py, storage.py)
│   ├── modules/
│   │   ├── auth/ users/ game/ regions/ geospatial/
│   │   ├── earth_observation/ agriculture/ advisory/
│   │   ├── decisions/ simulations/ ai/ admin/
│   └── shared/      (schemas/, exceptions/)
├── migrations/
├── seeds/           (aoi/, content/{chapter}/{region}.json, crops, rotation_rules, planting_windows, synthetic indicators)
├── scripts/         (check_env.py, seed.py, validate_content.py, import_national_layers.py,
│                     compute_coverage.py, compute_climatology.py, train_model.py, ingestion/)
├── storage/         (rasters locais; fora do Git)
├── tests/
├── docs/
├── extras/
├── .env.example  .gitignore  pyproject.toml  README.md
```

Cada módulo tem, quando necessário: `router.py` (HTTP), `service.py` (regras), `repository.py` (BD), `schemas.py` (validação). **Os routers nunca falam com a BD diretamente.**

---

# 5. API (BASE URL: /api/v1)

**Auth/Users:** POST `/auth/register`, `/auth/login`, `/auth/refresh` · GET, PATCH `/users/me`

**Regiões:** GET `/regions`, `/regions/{id}`, `/regions/{id}/districts`, `/regions/{id}/communities`, `/regions/{id}/map` (GeoJSON), `/regions/{id}/indicators`, `/regions/{id}/climate-profile`, `/regions/{id}/map-config` · GET `/regions/compare-climate?ids=`

**Jogo:**
- GET `/game/chapters?region_id=`, `/game/chapters/{id}?region_id=` (objetivo, lições e desafios da região, por ordem), `/game/missions`, `/game/missions/{id}`, `/game/progress`, `/game/achievements`
- POST `/game/lessons/{id}/complete`, `/game/missions/{id}/start`, `/game/missions/{id}/submit`, `/game/missions/{id}/field-observation`
- GET `/content/manifest?region_id=&language=` (lista de conteúdos para descarga leve)

**Observação da Terra:** GET `/earth-observation/datasets`, `/layers`, `/indicators`, `/timeseries`, `/imagery`, `/metadata/{id}` · GET `/geo/layers/{layer_id}/tilejson` · GET `/tiles/{layer_id}/{z}/{x}/{y}.png`

**Aconselhamento (consultas):** GET `/advisory/season-status`, `/advisory/rain-onset`, `/advisory/dry-spell`, `/advisory/heat-stress` (todos com `region_id` e `date`)

**Agricultura e decisões:** GET `/agriculture/crops`, `/agriculture/crops/{id}`, `/agriculture/planting-windows` · POST `/decisions/planting-date`, `/decisions/crop-selection`, `/decisions/crop-rotation`, `/decisions/land-comparison` · POST `/simulations/irrigation`, `/simulations/scenarios`, `/simulations/season-replay`

**IA:** POST `/ai/explain`, `/ai/hint` · GET `/ai/health`

**Admin (role `admin`):** CRUD de capítulos, lições, missões, datasets, culturas, regras de rotação e parâmetros; mudança de estado de conteúdo (draft, review, published) e marcação `verified`.

**Convenções:** listagens com `limit`/`offset` e `items`/`total`; erros `{"error": {"code","message","details"}}`; códigos HTTP corretos (401, 403, 404, 409, 422); `?compact=true` para respostas leves; ETag/Cache-Control; `data_as_of` em respostas de dados; documentação automática em `/docs` com exemplos.

---

# 6. MODELO DE DADOS

UUID como chaves primárias, `created_at`/`updated_at` onde fizer sentido, índices GIST nas geometrias (SRID 4326) e índices nas chaves estrangeiras e filtros.

**Núcleo:**
`users` · `regions` (boundary, is_proposed_study_area) · `districts` (código, nome, província, geometria; origem CENACARTA 2017) · `communities` · `chapters` (chapter_number 1–12, title, learning_objective, is_common, unlock_rule JSONB, topics JSONB, order, provisional) · `lessons` (chapter_id, region_id nullable, position, topic, title, text_simple, audio_text, learning_points JSONB, evidence JSONB, source, verified default false, is_synthetic, language, content_version) · `missions` = desafios (chapter_id, region_id nullable, position, mission_type, prompt_simple, configuration JSONB, answer_rules JSONB, learning_note, max_score) · `player_progress` (user_id, mission_id ou lesson_id, status, score, started_at, completed_at) · `achievements` · `user_achievements` · `region_content_status` (region_id, chapter_id, lessons_total, lessons_verified, missions_total, status)

**Dados e observação da Terra:**
`datasets` (source, product, variable, version, spatial_resolution, temporal_resolution, quality_notes, metadata JSONB, license, is_synthetic) · `geo_layers` (region_id, dataset_id, layer_type, format, crs, bbox, pixel_size, nodata, scale_factor, colormap, value_range, processing_version, file_size_bytes, asset_uri, time_start, time_end) · `indicators` (region_id, indicator_type, value, unit, observed_at, **dataset_id obrigatório**, is_synthetic) · `climatology` e `climate_profiles` (region_id, variable, period, stats JSONB, baseline_start, baseline_end, dataset_id, version, resolution, is_synthetic) · `ingestion_runs` (source, product, version, region_id, time_start, time_end, status, error, checksum, started_at, finished_at) · `region_source_coverage` (region_id, source, tile_id, computed_at)

**Agricultura e decisões:**
`crops` (code, name, parameters JSONB, source, verified) · `planting_windows` (crop_id, region_id, start_month, end_month, notes, source, verified) · `rotation_rules` (regras agronómicas, region, source, verified default false) · `district_crop_stats` (district_id, crop, area_ha, production_t, campaign, source, year) · `soil_units` (propriedades do mapa de solos INIA, ano 1995, geometria) · `campaigns` e `seasons` (época chuvosa/seca por região, parametrizado, com fonte) · `decisions` (user_id, mission_id, decision_type, input_data, result, dataset_versions JSONB) · `simulation_runs` (user_id, scenario_type, parameters, output, dataset_versions)

**IA:** `ai_interactions` (user_id nullable, decision_id, provider, language, latency_ms, used_fallback, created_at; sem texto pessoal) · `ml_models` (opcional, fase 12)

Relações: região → comunidades, distritos e camadas; capítulo → lições e missões; conteúdo comum (`region_id` nulo) ou regional; utilizador → progresso, decisões e simulações; **todo indicador identifica o dataset de origem**.

---

# 7. REGRAS CIENTÍFICAS (OBRIGATÓRIAS NO CÓDIGO E NAS RESPOSTAS)

1. O motor de decisões v1 usa **regras agronómicas transparentes e parametrizáveis**, sem IA/ML. Parâmetros em BD/seeds, nunca hardcoded na lógica.
2. **Nenhuma decisão depende de um único indicador** (ex.: só NDVI).
3. Toda resposta de decisão inclui `explanation` (porquê, em linguagem simples), `limitations`, `data_used` (dataset e versão), `risk_level` e `learning_note`.
4. Não tratar SMAP ou GRACE como se avaliassem parcelas individuais. Cada indicador expõe a resolução espacial e temporal, e a API devolve `resolution_warning` quando a resolução é grosseira para o uso pedido. Dados por distrito ou solo de 1995 nunca se apresentam como dados de parcela.
5. Separar sempre: **observado, derivado, previsão, simulação**. Cada resposta indica a categoria.
6. NDVI é indicador de vigor da vegetação, **nunca de produtividade**.
7. Dados fictícios têm `is_synthetic: true`, são documentados como tal e **nunca** são apresentados como reais. A API devolve esse campo.
8. Registar a versão do dataset que originou cada decisão e simulação.
9. **A rotação de culturas NÃO vem de satélite.** Vem de regras agronómicas validadas. Os dados apoiam apenas o momento e o risco. A rotação só pode propor culturas com área > 0 no distrito (`district_crop_stats`).
10. **Nenhum conteúdo agronómico ou climático é escrito de memória** (janelas de plantio, necessidades hídricas, rotações, calendários, descrições do clima de cada província). Tudo vem de dados ingeridos ou de fontes registadas (IIAM, MADER/serviços de extensão, FAO, INAM, calendários agrícolas oficiais) com campo `source` e `verified: false` até eu confirmar. Valores provisórios aparecem marcados "provisório, a validar". Pede-me as fontes em vez de preencher.
11. Os indicadores ajudam a interpretar condições mas **não são garantias de produtividade**. Evita mensagens e nomes de campos que sugiram certeza.

---

# 8. CONTEÚDO DOS CAPÍTULOS (LIÇÕES E DESAFIOS POR REGIÃO)

- Cada capítulo, em cada região, tem lições e depois desafios. Capítulos 1–2 comuns; 3–11 regionais; 12 final regional. O clima é apenas um tema (`topic`) entre vários.
- `mission_type` permitidos: `interpret_signal`, `choose_date`, `choose_crop`, `compare_areas`, `rotation_choice`, `replay_campaign`, `water_decision`, `field_observation_check`. A API valida a resposta contra `answer_rules` e devolve feedback; não implementa mecânicas visuais.
- Pontuação por qualidade da decisão e compreensão, nunca por velocidade.
- Origem do conteúdo: lições de clima, culturas e solos podem ser **geradas por script** a partir dos perfis e tabelas (e depois revistas por uma pessoa); lições de plantio, rotação e boas práticas vêm de fontes agronómicas; lições pedagógicas (leitura de dados, semáforo) são escritas pela equipa.
- Conteúdo em `seeds/content/{chapter}/{region}.json`, validado por schema. `scripts/validate_content.py` falha se faltar lição, desafio, fonte ou idioma.
- Estados: `draft → review → published`. Só se publica com `verified: true` e com o mínimo de lições (N) e desafios (M), configuráveis.
- Nenhuma comparação entre regiões sem evidência dos dois perfis.
- Desbloqueio de capítulos conforme `unlock_rule`.
- Cada lição/desafio tem `language` (`pt` desde o início; outras línguas como extensão).

---

# 9. EXPERIÊNCIA DO AGRICULTOR (PRINCÍPIOS DE API)

- Toda resposta orientada ao jogador inclui: `traffic_light` (favorable/caution/risk), `message_simple` (frase curta, linguagem do campo), `audio_text`, `why`, `learning_note` e `limitations`. Termos técnicos (NDVI, raster, anomalia) só em `technical_details` opcional.
- Pensar em telemóveis básicos e internet limitada: payloads pequenos, `compact=true`, cache, `data_as_of`, manifesto de conteúdo para descarga.
- O jogador compara o que observa no terreno com o que os dados mostram (`field-observation`): serve para ensinar a confiar na própria observação e perceber os limites do satélite.

---

# 10. DADOS: FONTES E INTEGRAÇÃO

## 10.1 Princípios
- Antes de implementar cada fonte, **confirma a documentação oficial atual** (endpoints, produtos, versões, autenticação, licença, resolução, latência) e regista-a em `docs/DATA_SOURCES.md` com a data de verificação. Não inventes nomes de produtos, variáveis ou parâmetros; se não puderes confirmar, diz-mo.
- Credenciais só por variáveis de ambiente (`EARTHDATA_TOKEN`, `USGS_USERNAME`, `USGS_TOKEN`).

## 10.2 Fontes NASA/USGS (ordem de implementação)
1. **NASA POWER**: API REST pública, sem login. Temperatura, chuva modelada, radiação. É reanálise/modelo, não medição local. Resolução grosseira.
2. **MODIS**: NDVI com filtro de qualidade (QA), compostos de 16 dias, 250 m (confirmar produto). Preferir recorte no servidor (AppEEARS) se a documentação o confirmar.
3. **GPM IMERG**: precipitação. Documentar a diferença Early/Late/Final e justificar a escolha.
4. **Landsat Collection 2 Level-2** (USGS): NDVI detalhado e cobertura da terra, máscara de nuvens, apenas datas-chave por região.
5. **SMAP**: humidade do solo, só contexto regional (~9 km). Avisar "não aplicável a parcelas".
6. **GRACE/GRACE-FO**: anomalia de água armazenada, só contexto regional; escala muito mais grosseira que as áreas de estudo; devolver `resolution_warning` sempre.
Uma fonte real bem integrada vale mais do que várias superficiais: POWER, MODIS e GPM são prioritárias; Landsat, SMAP e GRACE entram como camadas de contexto com avisos.

## 10.3 Contrato comum de ingestão (`scripts/ingestion/`)
`discover() → fetch() → clip() → qa_mask() → derive_indicators() → to_cog() → register()`. Cada execução fica em `ingestion_runs`; idempotente e com retry; cada indicador referencia dataset e versão; apagar originais após recorte.

## 10.4 AOI e cobertura
- `seeds/aoi/{region}.geojson` com buffer, marcadas "área de estudo proposta". Preferir os limites de distritos (CENACARTA) como base.
- `scripts/compute_coverage.py`: calcula por interseção com as grelhas oficiais quais as tiles MODIS (h/v) e path/row Landsat (WRS-2) que cobrem cada AOI. **Nunca hardcodar** estes valores. Guarda em `docs/COVERAGE.md` e `region_source_coverage`.

## 10.5 Climatologia e aconselhamento
- `scripts/compute_climatology.py` calcula o "normal" por região a partir de séries longas (confirma na documentação oficial os períodos disponíveis antes de fixar a base). Alimenta anomalias, `climate_profiles` e os módulos `advisory`.
- Início das chuvas, veranico (dias secos consecutivos) e stress térmico: regras parametrizáveis em BD (acumulado em N dias, veranico de M dias), nunca hardcoded.

## 10.6 Dados nacionais (Data Portal Moçambique / Data4Moz)
- Fonte: https://dataportal.co.mz/dados-espaciais (Agricultura, Solos, Limites Administrativos, Clima). Camadas úteis: limites de distritos (CENACARTA 2017), área e produção por cultura e por distrito (campanha 2023/2024, INE/MAAP), tipos de solo (INIA/IIAM, 1995).
- Antes de usar: ler Termos e condições, registar licença, fonte, ano, formato e resolução em `docs/DATA_SOURCES.md`. Não assumir que podemos redistribuir. Se uma camada estiver indisponível para download, regista-o e pede-me os dados.
- `scripts/import_national_layers.py` (idempotente): descarregar, filtrar pelos distritos das regiões, reprojetar para EPSG:4326, gravar com `source`, `year`, `license`.

## 10.7 Mapas e tiles
- `GET /tiles/{layer_id}/{z}/{x}/{y}.png` com `rio-tiler`, lendo COG do `StorageBackend`, com cache. Tilejson por camada.
- `map-config` por região: bbox, zoom mínimo/máximo, camadas, legendas com unidades, resolução, data e `is_synthetic`.
- Validar z/x/y e proteger contra path traversal.

---

# 11. MÓDULO DE IA (`modules/ai/`)

Duas responsabilidades separadas:
1. **`ExplanationProvider`** (explicar resultados): `explain()`, `hint()`, `health()`. Implementação obrigatória: `TemplateProvider` (modelos de texto parametrizados, sem IA externa), totalmente testada, em pt. Um LLM externo só se eu o pedir e indicar o provedor.
2. **`ModelInferenceProvider`**: `predict()`, `model_info()`, `health()`. Interface + `NullInferenceProvider` (devolve "indisponível"). `LocalModelProvider` (scikit-learn, joblib em `storage/models/`) só na fase opcional.

Regras:
- **MozBrain e Machamba IA (Cognivault) NÃO são para implementar.** Nada se sabe sobre APIs de inferência ou exportação. Só implementas um adaptador quando eu fornecer documentação oficial. Não inventes endpoints, formatos ou autenticação. (Nota: a Moz.com é uma API de SEO sem relação com o projeto.)
- A IA nunca acede a dados de satélite: recebe só contexto estruturado da API (indicadores, dataset, versão, resolução, categoria, `limitations`). Nunca dados pessoais.
- Validar respostas: sem garantias de produtividade, com limitações, tamanho máximo, idioma pedido. Em falha ou timeout, usar `TemplateProvider`.
- Qualquer previsão de modelo traz versão, features, métricas, `is_synthetic` e categoria "previsão"; nunca é a única base de uma decisão. Modelos treinados com dados sintéticos são "educativos, não validados".
- Testes sempre com mocks; nunca chamar serviços externos reais.

---

# 12. MÉTODO DE TRABALHO (CICLO OBRIGATÓRIO EM CADA PASSO)

1. **PLANO**: em 3 a 6 linhas, o que vais fazer e que ficheiros vais criar ou alterar.
2. **IMPLEMENTAR**: só o código desse passo.
3. **TESTES**: sucesso, validação, erros e permissões.
4. **EXECUTAR**: corre de facto `uv run alembic upgrade head` (se houver migrações), `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy app`.
5. **DIAGNOSTICAR**: se falhar, mostra o erro real, explica a causa-raiz em linguagem simples e só depois corrige.
6. **RETIFICAR E REPETIR** até tudo passar. Se não resolveres o mesmo erro em **5 tentativas**, pára, resume o que tentaste e pergunta-me.
7. **REGISTAR** em `docs/BUILD_LOG.md`: passo, o que foi feito, erros, correções, resultado dos testes. Atualiza também o documento de `docs/` afetado.
8. **COMMIT** (secção 13).
9. **RELATÓRIO** neste formato:

```
## Passo X.Y — [nome]
Estado: ✅ concluído / ❌ bloqueado
Ficheiros criados/alterados: ...
Testes: N passaram / N falharam
Lint e mypy: ok / erros
Erros encontrados e correções: ...
Como verificar manualmente: (curl ou URL do /docs)
Commit: <hash> <mensagem>
Próximo passo: ...
```

**Regras do ciclo:**
- Só avanças quando testes, ruff e mypy passam sem erros. Corre sempre a suíte completa (regressão) antes de fechar um passo.
- **Nunca apagues, ignores ou enfraqueças um teste para "fazer passar".** Corrige o código. Não uses `# type: ignore` ou `# noqa` sem justificação escrita.
- Não inventes endpoints, bibliotecas, parâmetros ou formatos. Em dúvida sobre APIs externas, confirma a documentação oficial.
- Ambiguidade que afete a arquitetura: pergunta. Caso contrário, escolhe a opção mais simples e regista em `docs/DECISIONS.md` (contexto, opções, escolha, motivo).
- Segredos só em `.env` (nunca no Git); mantém `.env.example`.
- Se faltar `DATABASE_URL` ou `TEST_DATABASE_URL`, ou a ligação falhar, **pára e pede-me os dados**. Não uses SQLite nem improvises outra BD.
- Cuidado com a base cloud: nunca corras comandos destrutivos (`drop`, `truncate`, `downgrade base`) na base de desenvolvimento sem eu confirmar. Na base de testes podes limpar.

---

# 13. GIT E COMMITS (CONVENTIONAL COMMITS, EM INGLÊS)

Formato: `type(scope): short description`. Tipos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `build`.
- Descrição em inglês, minúscula, imperativo, máx. 72 caracteres, sem ponto final.
- Um commit por passo concluído, só depois de testes, ruff e mypy passarem. Correções relevantes de erros em commits `fix` separados.
- Nunca commitar `.env`, `storage/`, rasters (`*.tif`, `*.tiff`), `__pycache__` ou ficheiros grandes (garante o `.gitignore` no passo 0.1).
- Trabalha no branch `dev`; `main` só recebe código quando eu confirmar o fim de uma fase. No fim de cada fase confirmada, cria a tag `phase-0`, `phase-1`, etc.
- Exemplos: `chore: init project structure and tooling`, `feat(auth): add user registration and login`, `fix(auth): handle duplicate email on register`, `feat(content): add lessons and missions schema`, `feat(ingestion): add nasa power ingestion`, `docs: update build log for phase 2`.

---

# 14. FASES E PASSOS

**Fase 0 — Fundação**
- 0.1 Estrutura do repositório, `pyproject.toml` com uv, ruff, mypy, pytest, `.gitignore`, README inicial, git com branches `main` e `dev`
- 0.2 `.env.example` (DATABASE_URL, TEST_DATABASE_URL, DATABASE_URL_DIRECT, JWT_SECRET, CORS_ORIGINS, STORAGE_PATH, EARTHDATA_TOKEN) e `scripts/check_env.py` (valida as duas bases e PostGIS)
- 0.3 `core/config.py`, `core/database.py` (com retry), `GET /health` (API, BD e PostGIS)
- 0.4 Alembic (ligação direta), primeira migração (extensão PostGIS), fixtures de teste

**Fase 1 — Autenticação**
- 1.1 `users` + migração · 1.2 registo/login com argon2 · 1.3 JWT access/refresh · 1.4 `/users/me` e permissões (`player`, `admin`)

**Fase 2 — Regiões e dados nacionais**
- 2.1 `regions`, `districts`, `communities` + migração (GIST)
- 2.2 Importação das camadas Data4Moz (limites de distritos) para as regiões confirmadas; AOI em `seeds/aoi/`; seed idempotente (Gaza, Zambézia, Tete; estrutura pronta para Maputo, que fica à espera da minha confirmação)
- 2.3 Endpoints de regiões, distritos, comunidades e mapa (GeoJSON)
- 2.4 `district_crop_stats` e `soil_units` importados com fonte, ano e licença registados

**Fase 3 — Sistema de jogo e conteúdo**
- 3.1 `chapters`, `lessons`, `missions`, `player_progress`, `achievements`, `user_achievements`, `region_content_status` + migração
- 3.2 Seed dos 12 capítulos (provisórios até eu fornecer a lista), com 1–2 comuns, 3–11 regionais, 12 final; `scripts/validate_content.py` e schema dos seeds de conteúdo
- 3.3 Endpoints de capítulos, lições e missões (conteúdo separado da região; filtro por `region_id`; desbloqueio)
- 3.4 `start`, `submit` e `complete` com progresso e pontuação (impedir submeter missão não iniciada ou já concluída); validação por `mission_type`
- 3.5 Progresso, conquistas e `content/manifest`

**Fase 4 — Observação da Terra**
- 4.1 `datasets`, `geo_layers`, `indicators`, `climatology`, `climate_profiles` + migração
- 4.2 Endpoints de datasets, layers, indicators, timeseries e metadata (resolução, versão, `is_synthetic`)
- 4.3 `StorageBackend` + `LocalStorage` (rasters em `storage/`, URI na BD, servir por endpoint protegido, proteção contra path traversal)
- 4.4 Seed de indicadores e perfis sintéticos (NDVI, precipitação, humidade, temperatura) marcados `is_synthetic`

**Fase 5 — Núcleo de decisão agrícola**
- 5.1 `crops`, `planting_windows`, `rotation_rules`, `campaigns`, `seasons` (seeds com `source` e `verified: false`)
- 5.2 Cálculo de anomalias e módulo `advisory` (season-status, rain-onset, dry-spell, heat-stress) com regras parametrizáveis
- 5.3 `POST /decisions/planting-date` e `/crop-selection`
- 5.4 `POST /decisions/land-comparison` (multi-indicador, com limitações e avisos de resolução)
- 5.5 `POST /decisions/crop-rotation` (regras agronómicas; só culturas presentes no distrito; sem satélite como critério)
- 5.6 `POST /simulations/irrigation` e `/scenarios`; `/simulations/season-replay` (1.ª fase sem qualquer dado posterior à data de corte: teste obrigatório)
- 5.7 `field-observation` (comparação observação local vs. indicadores)
- 5.8 Registo de decisões e simulações com versões de dataset

**Fase 6 — Contrato de ingestão, AOI e cobertura**
- 6.1 Estrutura `scripts/ingestion/` com o contrato comum e `ingestion_runs`
- 6.2 `scripts/compute_coverage.py` + `docs/COVERAGE.md` + `region_source_coverage`

**Fase 7 — Fontes reais (um passo por fonte, confirmando a documentação oficial antes)**
- 7.1 NASA POWER → indicadores · 7.2 MODIS NDVI (recortado, QA) · 7.3 GPM IMERG · 7.4 Landsat (datas-chave) · 7.5 SMAP (contexto) · 7.6 GRACE/GRACE-FO (contexto)
- 7.7 `compute_climatology.py` com dados reais; recalcular `climate_profiles`; gerar lições calculáveis (clima, culturas, solos) com `verified: false`
- 7.8 Versionamento de datasets e metadados de qualidade (resolução, data, nuvens, unidades, limitações)

**Fase 8 — Mapas e tiles**
- 8.1 Endpoint de tiles com rio-tiler + tilejson · 8.2 `map-config` com legendas e avisos de resolução

**Fase 9 — Módulo de IA**
- 9.1 Interfaces `ExplanationProvider` e `ModelInferenceProvider`, `TemplateProvider`, `NullInferenceProvider`
- 9.2 Endpoints `/ai/*`, validação de respostas, fallback, `ai_interactions`, testes com mocks
- (MozBrain/LLM externo: NÃO implementar sem documentação minha)

**Fase 10 — Admin, segurança e desempenho**
- 10.1 Endpoints admin (conteúdo, estados, `verified`, datasets, culturas, regras)
- 10.2 Rate limiting em memória · 10.3 Cache em memória com TTL (mapas, indicadores, perfis)
- 10.4 Tratamento global de erros com o formato único · 10.5 Logging estruturado (sem passwords, tokens ou dados pessoais)

**Fase 11 — Fecho**
- 11.1 `docs/openapi.json` revisto · 11.2 Cobertura ≥ 80% nos módulos `service`
- 11.3 README completo (configurar BD cloud, correr, testar, estrutura, decisões, limitações: dados sintéticos, suspensão da BD gratuita, disco efémero)
- 11.4 Teste ponta a ponta: registar jogador → escolher região → ler capítulo (lições) → iniciar desafio regional → obter indicadores/aconselhamento → submeter decisão → ver progresso

**Fase 12 — OPCIONAL (só se eu pedir): Laboratório de Modelos**
- `LocalModelProvider` com scikit-learn (decision_tree, random_forest, logistic_regression, knn), divisão treino/teste aleatória e temporal com aviso de fuga de dados, limites de tamanho e tempo, métricas, matriz de confusão, `is_synthetic`. Sem execução de código do jogador.

---

# 15. DOCUMENTAÇÃO (mantida ao longo do projeto, em `docs/`)

`ARCHITECTURE.md` (diagramas da secção 2) · `API.md` + `openapi.json` · `DB_SCHEMA.md` (com diagrama ER) · `DATA_SOURCES.md` (uma ficha por fonte: produto, versão, resolução, latência, acesso, licença, limitações, data de verificação) · `GEO_PIPELINE.md` · `TILES_AND_MAPS.md` e `COVERAGE.md` · `CONTENT_GUIDE.md` (modelo de capítulo, estados, verificação) · `AI_INTEGRATION.md` · `SCIENTIFIC_LIMITS.md` · `RUNBOOK.md` (ingestões, reprocessamento, falhas, espaço em disco) · `BUILD_LOG.md` · `DECISIONS.md`. Cada passo que altere comportamento atualiza o documento correspondente antes do commit.

---

# 16. COMO COMEÇAR

1. Confirma que percebeste o projeto em no máximo 10 linhas e lista as suposições.
2. Lista o que ainda preciso de te fornecer: `DATABASE_URL`, `TEST_DATABASE_URL` (e opcional `DATABASE_URL_DIRECT`) e em que ficheiro os colocar; lista oficial dos 12 capítulos; Maputo (Província ou Cidade e distrito); fontes agronómicas e calendários validados. Não esperes por estas respostas para o que não depende delas.
3. Executa o **Passo 0.1** seguindo o ciclo da secção 12.
4. No fim de cada **fase**, pára, apresenta o resumo (o que foi feito, erros principais, estado dos testes, decisões, pendências) e **espera a minha confirmação** antes de começar a seguinte.

---

# 17. CRITÉRIO DE CONCLUSÃO

- A API arranca com `uv run fastapi dev` ligada à base cloud, sem erros
- `uv run pytest` passa 100% dos testes; ruff e mypy sem erros
- O fluxo ponta a ponta do passo 11.4 funciona
- Todos os dados sintéticos estão marcados; nenhum conteúdo `verified: false` aparece publicado sem a marca "a validar"
- A arquitetura implementada corresponde à secção 2 (pipeline independente da API; rasters fora das tabelas)
- `docs/BUILD_LOG.md` documenta os erros e como foram resolvidos; o histórico Git segue Conventional Commits com tags por fase
