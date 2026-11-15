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
