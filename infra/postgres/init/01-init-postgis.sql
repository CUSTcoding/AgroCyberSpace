-- ==============================================================================
-- AGROSPACE — POSTGIS & PERSISTENCE INITIALIZATION
-- ==============================================================================

-- Enable spatial and UUID extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schema for AgroSpace domain
CREATE SCHEMA IF NOT EXISTS agro;

-- 1. Farmers / Utilizadores das Machambas
CREATE TABLE IF NOT EXISTS agro.farmers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255),
    province VARCHAR(100) DEFAULT 'Manica',
    district VARCHAR(100) DEFAULT 'Sussundenga',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Machambas (Propriedades Agrícolas com Geometria Geoespacial PostGIS)
CREATE TABLE IF NOT EXISTS agro.machambas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farmer_id UUID REFERENCES agro.farmers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    crop_type VARCHAR(100) NOT NULL, -- Ex: Milho, Mandioca, Soja, Gergelim
    soil_classification VARCHAR(100), -- Ex: Ferralsols, Arenosols, Nitisols
    geom GEOMETRY(Polygon, 4326) NOT NULL, -- Coordenadas WGS84 EPSG:4326
    centroid GEOMETRY(Point, 4326) GENERATED ALWAYS AS (ST_Centroid(geom)) STORED,
    area_hectares NUMERIC(10, 4) GENERATED ALWAYS AS (ST_Area(geom::geography) / 10000.0) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Spatial GiST index for ultra-fast spatial search (e.g. ST_Contains, ST_Intersects)
CREATE INDEX IF NOT EXISTS idx_machambas_geom ON agro.machambas USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_machambas_centroid ON agro.machambas USING GIST (centroid);

-- 3. Observações de Satélite da NASA (SMAP, GPM, Landsat, MODIS)
CREATE TABLE IF NOT EXISTS agro.satellite_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machamba_id UUID REFERENCES agro.machambas(id) ON DELETE CASCADE,
    source_mission VARCHAR(50) NOT NULL, -- NASA_SMAP, NASA_GPM, NASA_POWER, LANDSAT_8_9
    observation_date DATE NOT NULL,
    soil_moisture_m3 NUMERIC(6, 4),      -- SMAP L3/L4 (m3/m3)
    precipitation_mm NUMERIC(8, 2),      -- GPM IMERG Daily (mm)
    ndvi_mean NUMERIC(5, 4),             -- Normalized Difference Vegetation Index (-1 to 1)
    evapotranspiration_mm NUMERIC(8, 2), -- NASA POWER / MODIS
    surface_temp_celsius NUMERIC(5, 2),  -- LST Land Surface Temperature
    raw_payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sat_obs_machamba_date ON agro.satellite_observations(machamba_id, observation_date DESC);

-- 4. Missões e Recomendações dos AI Agents
CREATE TABLE IF NOT EXISTS agro.missions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machamba_id UUID REFERENCES agro.machambas(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    objective TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED, ARCHIVED
    mcp_tools_invoked JSONB DEFAULT '[]'::jsonb,
    agent_reasoning TEXT,
    actionable_advice JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_missions_machamba ON agro.missions(machamba_id);
