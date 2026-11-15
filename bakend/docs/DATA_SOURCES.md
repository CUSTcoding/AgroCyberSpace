# AgroSight Fair Space — Fichas de Fontes de Dados e Metadados

Registo rigoroso de fontes de dados de observação da terra e dados nacionais abertos.
Toda a integração no backend deve respeitar as informações e limitações aqui descritas.

---

## 1. Dados Nacionais: Limite de Distritos (CENACARTA 2017)

- **Identificador:** `national_cenacarta_districts_2017`
- **Nome da Camada:** Limite de Distritos (CENACARTA, 2017)
- **Fonte Oficial:** CENACARTA (Centro Nacional de Cartografia e Teledeteção) / Plataforma Data Portal Moçambique (Data4Moz).
- **URL de Referência:** https://dataportal.co.mz/dados-espaciais
- **Ano de Referência:** 2017
- **Data de Verificação da Documentação:** 2026-11-15
- **Sistema de Coordenadas de Referência (CRS):** WGS 84 (EPSG:4326)
- **Formato:** Shapefile / GeoJSON (Polígonos)
- **Cobertura Espacial:** Nacional (162 distritos em 11 províncias de Moçambique)
- **Atributos Principais:**
  - `CodDistrit`: Código administrativo do distrito (ex.: 0202)
  - `Distrito`: Nome do distrito (ex.: Chókwè, Mocuba, Angónia)
  - `CodProvinc`: Código da província
  - `Provincia`: Nome da província (ex.: Gaza, Zambézia, Tete, Maputo)
  - `geometry`: Polígono ou MultiPolígono com limites do distrito
- **Licença / Termos de Uso:**
  - Dados públicos abertos disponibilizados pelo CENACARTA e harmonizados pelo Data4Moz para planeamento e investigação.
  - Atribuição obrigatória da fonte original (CENACARTA 2017).
- **Limitações e Regras Científicas:**
  - Trata-se de divisões administrativas com base cartográfica de 2017.
  - Para efeitos do projeto AgroSight Fair Space, as áreas de estudo são designadas como "áreas de estudo propostas" (`is_proposed_study_area = True`) e não como limites agrícolas validados em campo.
  - Na ausência de conectividade de rede com o portal externo, a API utiliza os ficheiros canónicos de AOI persistidos em `seeds/aoi/`.

---

## 2. Áreas de Estudo Propostas (AOI) Confirmadas

| Região | Código | Distrito / Vale de Estudo | Província | Estado |
|---|---|---|---|---|
| **Gaza** | `gaza` | Chókwè e vale do Limpopo | Gaza | Confirmado |
| **Zambézia** | `zambezia` | Mocuba e vale do Licungo | Zambézia | Confirmado |
| **Tete** | `tete` | Angónia e áreas selecionadas do vale do Zambeze | Tete | Confirmado |
| **Maputo** | `maputo` | *A definir (Província vs. Cidade e distrito)* | Maputo | **PENDENTE DE CONFIRMAÇÃO** |

---

## 3. Dados Nacionais: Estatísticas Agrícolas Distritais (INE / MADER CAP 2023/2024)

- **Identificador:** `national_district_crop_stats_2023_2024`
- **Nome da Camada / Tabela:** Estatísticas Agrícolas Distritais (Área e Produção)
- **Fonte Oficial:** INE (Instituto Nacional de Estatística) / MADER (Ministério da Agricultura e Desenvolvimento Rural) — Censo Agro-Pecuário (CAP) 2023/2024, compilado e harmonizado via Data4Moz.
- **URL de Referência:** https://dataportal.co.mz/dados-espaciais (Agricultura)
- **Ano de Referência / Campanha:** Campanha Agrícola 2023/2024 (ano 2023)
- **Data de Verificação da Documentação:** 2026-11-15
- **Formato:** Dados tabulares georreferenciados por distrito (`district_id`, `crop`, `area_ha`, `production_t`)
- **Cobertura Espacial:** Distritos de estudo prioritários de Gaza, Zambézia e Tete.
- **Licença / Termos de Uso:**
  - Dados oficiais públicos abertos do Sistema Estatístico Nacional de Moçambique (INE).
  - Atribuição obrigatória: "INE/MADER - Censo Agro-Pecuário 2023/2024 via Data4Moz".
- **Regras Científicas do Backend (Regra 9 do prompt):**
  - **A rotação de culturas NÃO vem de satélite.** Vem de regras agronómicas validadas.
  - A recomendação e validação de rotação de culturas só pode propor culturas com área cultivada estritamente maior que zero (`area_ha > 0`) no distrito selecionado (`district_crop_stats`).
  - Dados por distrito nunca são tratados nem apresentados como dados a nível de parcela individual.

---

## 4. Dados Nacionais: Carta Nacional de Solos (INIA / IIAM 1995)

- **Identificador:** `national_soil_units_inia_1995`
- **Nome da Camada:** Carta de Solos de Moçambique (Escala 1:1.000.000)
- **Fonte Oficial:** INIA (Instituto Nacional de Investigação Agronómica) / IIAM (Instituto de Investigação Agrária de Moçambique), 1995.
- **URL de Referência:** https://dataportal.co.mz/dados-espaciais (Solos)
- **Ano de Referência:** 1995
- **Data de Verificação da Documentação:** 2026-11-15
- **Sistema de Coordenadas de Referência (CRS):** WGS 84 (EPSG:4326)
- **Formato:** Polígonos vetoriais com atributos agronómicos em JSONB (drenagem, textura, profundidade, fertilidade)
- **Licença / Termos de Uso:**
  - Dados públicos de investigação agrária para fins educativos e planeamento territorial.
  - Atribuição obrigatória: "INIA/IIAM 1995".
- **Regras Científicas do Backend (Regra 4 e 10 do prompt):**
  - Dados de solo de 1995 representam a classificação pedológica geral regional e **nunca** se apresentam como dados de amostragem recente ou de parcela individual.
  - Todo o modelo pedológico expõe `year: 1995` e a fonte `INIA/IIAM 1995`.

