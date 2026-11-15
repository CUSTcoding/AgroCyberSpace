# AgroSight REST API Reference

The live OpenAPI specification of record is available at `/api/v1/openapi.json`. Interactive Swagger UI is served at `/api/v1/docs` and ReDoc at `/api/v1/redoc`.

---

## 1. Conventions & Base Paths

- **Base URL:** `http://localhost:8000/api/v1`
- **Root Health:** `http://localhost:8000/health` (also aliased at `/api/v1/health`)
- **Format:** All requests and responses use UTF-8 encoded JSON.
- **Identifiers:** All resource IDs are UUIDv4 strings unless specified otherwise.
- **Authentication:** Protected endpoints require an `Authorization: Bearer <access_token>` header issued by `/auth/login` or `/auth/register`.
- **Standard Error Schema:**
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable description.",
      "details": null
    }
  }
  ```

---

## 2. Authentication & User Management

### `POST /auth/register`
Create a new player account and receive access & refresh tokens.
- **Access:** Public
- **Request Body:**
  ```json
  {
    "email": "farmer@example.com",
    "password": "SecurePassword123!",
    "display_name": "Mateus",
    "preferred_language": "pt",
    "selected_region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "user": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "farmer@example.com",
      "display_name": "Mateus",
      "preferred_language": "pt",
      "role": "player",
      "selected_region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    },
    "tokens": {
      "access_token": "eyJhbGciOi...",
      "refresh_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 1800
    }
  }
  ```

### `POST /auth/login`
Authenticate with email and password.
- **Access:** Public
- **Request Body:** `{"email": "...", "password": "..."}`
- **Response (200 OK):** User details and JWT token pair.

### `POST /auth/refresh`
Rotate and refresh an expired access token using a valid refresh token.
- **Access:** Public
- **Request Body:** `{"refresh_token": "..."}`

### `GET /users/me`
Retrieve authenticated player profile.
- **Access:** Authenticated (Bearer Token)

### `PATCH /users/me`
Update allowed player profile fields (`display_name`, `preferred_language`, `selected_region_id`).
- **Access:** Authenticated (Bearer Token)

---

## 3. Study Regions & Geospatial Endpoints

### `GET /regions`
List agricultural study regions with pagination.
- **Query Params:** `limit` (default 20), `offset` (default 0)
- **Response:**
  ```json
  {
    "items": [
      {
        "id": "c1f7a28b-...",
        "code": "gaza",
        "name": "Gaza",
        "province": "Gaza",
        "description": "Chókwè irrigation perimeter and Limpopo River basin",
        "center_lat": -24.52,
        "center_lon": 33.00,
        "is_proposed_study_area": true
      }
    ],
    "total": 3,
    "limit": 20,
    "offset": 0
  }
  ```

### `GET /regions/{region_id}`
Retrieve complete metadata for a study region.

### `GET /regions/{region_id}/districts`
List administrative districts (CENACARTA 2017) located in this region.

### `GET /regions/{region_id}/communities`
List agricultural communities attached to the region's districts.

### `GET /regions/{region_id}/map`
Return region boundary as a valid GeoJSON Feature.

### `GET /regions/{region_id}/map-config`
Return spatial bounding box `[min_lon, min_lat, max_lon, max_lat]` and active layers for frontend map rendering.

### `GET /regions/{region_id}/indicators`
List district-level agricultural crop statistics (cultivated area `area_ha`, production `production_t`, campaign year).

---

## 4. Educational Game & Missions

### `GET /game/chapters`
Retrieve the 12 game chapters with unlock status for the authenticated player.
- **Access:** Authenticated
- **Query Params:** `region_id` (optional)

### `GET /game/chapters/{chapter_id}`
Retrieve chapter details including ordered lessons and authored challenge missions.
- **Access:** Authenticated

### `GET /game/lessons/{lesson_id}`
Read educational lesson text, audio script, learning points, and scientific provenance.
- **Access:** Public

### `POST /game/lessons/{lesson_id}/complete`
Mark a lesson as finished and update player progression.
- **Access:** Authenticated

### `POST /game/missions/{mission_id}/start`
Initiate an active challenge session.
- **Access:** Authenticated

### `POST /game/missions/{mission_id}/submit`
Submit player decision (`{"choice": "..."}`) and receive authored score and pedagogical feedback.
- **Access:** Authenticated
- **Response:**
  ```json
  {
    "score": 100,
    "max_score": 100,
    "is_recommended": true,
    "learning_note": "Aguardar maior humidade do solo reduz drasticamente o risco de perda da sementeira."
  }
  ```

### `GET /game/progress`
Retrieve paginated player completion history and scores.

### `GET /game/achievements`
List the badge and achievement catalogue alongside player unlock timestamps.

### `GET /content/manifest`
Retrieve verified content IDs and hash signatures for offline client validation.

---

## 5. Deterministic AI Assistance

### `POST /ai/hint`
Generate an agronomic hint for an active field observation or challenge.
- **Access:** Public
- **Request Body:**
  ```json
  {
    "category": "meteorology",
    "source": "NASA POWER / CENACARTA",
    "dataset_version": "v2.0",
    "limitations": "Regional satellite gridded data is contextual, not local parcel truth.",
    "language": "pt",
    "resolution_warning": "Dados de satélite em grelha representam o contexto regional."
  }
  ```
- **Response:**
  ```json
  {
    "explanation": "Os registos meteorológicos mostram variabilidade nas chuvas. Avalia a humidade antes de semear.",
    "language": "pt",
    "category": "meteorology",
    "source": "NASA POWER / CENACARTA",
    "dataset_version": "v2.0",
    "limitations": "Regional satellite gridded data is contextual, not local parcel truth.",
    "resolution_warning": "Dados de satélite em grelha representam o contexto regional."
  }
  ```

### `GET /ai/health`
Verify status of the template explanation engine.

---

## 6. Earth Observation & NASA POWER

### `GET /earth-observation/datasets`
List persisted satellite and reanalysis dataset metadata entries.

### `GET /earth-observation/timeseries`
Query persisted daily meteorological time series for a region.
- **Query Params:**
  - `region_id`: Target region UUID
  - `indicator_type`: Metric code (e.g., `PRECTOTCORR`, `T2M`)
  - `start`: Start date (`YYYY-MM-DD`)
  - `end`: End date (`YYYY-MM-DD`)
  - `limit`, `offset`: Pagination parameters
