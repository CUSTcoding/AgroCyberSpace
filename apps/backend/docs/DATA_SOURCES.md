# AgroSight Fair Space — Data Sources & Metadata Sheets

Comprehensive registry of Earth Observation sources and national open agricultural datasets.
All backend ingestion and API endpoints comply with the scientific constraints and citations documented here.

---

## 1. NASA POWER Daily API

- **Identifier:** `nasa_power_daily`
- **Official Documentation:** https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- **Regional Endpoint:** `https://power.larc.nasa.gov/api/temporal/daily/regional`
- **Verification Date:** 2026-11-15
- **Access & Format:** REST/HTTPS; JSON, CSV, ASCII, and NetCDF formats supported for points and bounding boxes. Public service; no API key required for standard queries.
- **Request Parameters:** Latitude/longitude bounds, `start`/`end` dates, `parameters`, `community`, `format`; `time-standard` accepts `UTC` or `LST` (daily service defaults to LST).
- **Key Limit:** Regional bounding-box requests allow one meteorological parameter per submission. The regional grid is nominally 0.5° x 0.5°; returned data reflects the native resolution of each sensor/reanalysis product.
- **Documented Temporal Coverage:** Daily UTC and LST data from 1981 to Near Real Time.
- **Limitations:** Gridded regional meteorological and solar reanalysis data, **not** local weather station observations or individual parcel measurements. Latency varies by product. Repeated calls to identical spatial bounds are rate-limited; ingestion is scheduled, audited, and idempotent.
- **License / Attribution:** NASA Open Data Policy. Attribution: "NASA Prediction Of Worldwide Energy Resources (POWER) Project".
- **Backend Implementation:**
  - `scripts/ingestion/ingest_power.py` performs manual/scheduled ingestion.
  - `scripts/ingestion/nasa_power.py` validates and normalizes regional GeoJSON features.
  - Daily values are persisted per grid point (lon/lat) and observation date in `indicators`, linked to `datasets` and audited in `ingestion_runs`.
  - The API exposes cached data via `/api/v1/earth-observation/datasets`, `/indicators`, `/timeseries`, and `/metadata/{dataset_id}`. User requests never query NASA upstream directly.

---

## 2. National Boundary Data: Administrative Districts (CENACARTA 2017)

- **Identifier:** `national_cenacarta_districts_2017`
- **Layer Name:** Administrative District Boundaries (CENACARTA, 2017)
- **Official Source:** CENACARTA (National Cartography and Remote Sensing Center) / Data Portal Mozambique (Data4Moz).
- **Reference URL:** https://dataportal.co.mz/dados-espaciais
- **Reference Year:** 2017
- **Verification Date:** 2026-11-15
- **Coordinate Reference System (CRS):** WGS 84 (EPSG:4326)
- **Format:** GeoJSON Polygons / MultiPolygons
- **Spatial Coverage:** Mozambique National (162 administrative districts across 11 provinces)
- **Key Attributes:**
  - `CodDistrit`: Administrative district code (e.g., `0202`)
  - `Distrito`: District name (e.g., Chókwè, Mocuba, Angónia)
  - `CodProvinc`: Province code
  - `Provincia`: Province name (e.g., Gaza, Zambézia, Tete)
  - `geometry`: Polygon or MultiPolygon with administrative boundaries
- **License / Terms:** Open public geospatial data provided by CENACARTA. Mandatory attribution: "CENACARTA 2017".
- **Scientific Constraints:**
  - Represents 2017 administrative cartography.
  - Designated as proposed study areas (`is_proposed_study_area = True`) rather than ground-verified farm boundaries.
  - When external portals are unreachable, the API uses verified canonical seed GeoJSON files in `seeds/aoi/`.

---

## 3. Confirmed Proposed Study Areas (AOI)

| Region | Code | Study District / Valley | Province | Status |
|---|---|---|---|---|
| **Gaza** | `gaza` | Chókwè & Limpopo River Basin | Gaza | Confirmed |
| **Zambézia** | `zambezia` | Mocuba & Licungo River Basin | Zambézia | Confirmed |
| **Tete** | `tete` | Angónia & Zambezi River Basin | Tete | Confirmed |
| **Maputo** | `maputo` | *To be determined (Province vs. City)* | Maputo | *Pending confirmation* |

---

## 4. National Data: District Crop Statistics (INE / MADER CAP 2023/2024)

- **Identifier:** `national_district_crop_stats_2023_2024`
- **Layer / Table:** District Agricultural Statistics (Cultivated Area & Production)
- **Official Source:** INE (National Statistics Institute) / MADER (Ministry of Agriculture and Rural Development) — Agricultural Census (CAP) 2023/2024 via Data4Moz.
- **Reference URL:** https://dataportal.co.mz/dados-espaciais
- **Agricultural Campaign:** 2023/2024 (Harvest Year 2023)
- **Verification Date:** 2026-11-15
- **Format:** Tabular georeferenced data by district (`district_id`, `crop`, `area_ha`, `production_t`)
- **Spatial Coverage:** Priority study districts in Gaza, Zambézia, and Tete.
- **Scientific Constraints:**
  - **Crop rotation recommendations do NOT come from satellites.** They derive from verified agronomic practices and confirmed local presence.
  - Crop rotation advice can only recommend crops with cultivated area strictly greater than zero (`area_ha > 0`) in the selected district (`district_crop_stats`).
  - District aggregates must never be presented as parcel-level evidence.

---

## 5. National Data: National Soil Map (INIA / IIAM 1995)

- **Identifier:** `national_soil_units_inia_1995`
- **Layer Name:** Soil Map of Mozambique (Scale 1:1,000,000)
- **Official Source:** INIA (National Agronomic Research Institute) / IIAM (Mozambique Agricultural Research Institute), 1995.
- **Reference URL:** https://dataportal.co.mz/dados-espaciais
- **Reference Year:** 1995
- **Verification Date:** 2026-11-15
- **Coordinate Reference System (CRS):** WGS 84 (EPSG:4326)
- **Format:** Vector polygons with agronomic attributes in JSONB (drainage, texture, depth, natural fertility).
- **Scientific Constraints:**
  - Represents regional pedological soil classification from 1995; **never** presented as recent soil tests or parcel-level reality.
  - Models must explicitly retain `year: 1995` and citation `INIA/IIAM 1995`.
