-- sql/schemas/01_core_tables.sql
BEGIN;

CREATE TABLE IF NOT EXISTS source_registry (
    source_id          TEXT PRIMARY KEY,
    name               TEXT NOT NULL,
    url                TEXT,
    source_type        TEXT NOT NULL,          -- api | web_notice | download | reference
    license            TEXT,
    access_method      TEXT,
    update_frequency   TEXT,
    geographic_precision TEXT,                 -- country | nuts1 | nuts2 | nuts3 | point | unknown
    limitations        TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS regions (
    region_code        TEXT PRIMARY KEY,       -- e.g. EE00, EE001, LV00, LT01
    region_name        TEXT NOT NULL,
    nuts_level         SMALLINT NOT NULL CHECK (nuts_level BETWEEN 0 AND 3),
    country_code       CHAR(2) NOT NULL,
    nuts_version       TEXT NOT NULL,          -- pinned: '2024'
    geom               GEOMETRY(MultiPolygon, 4326) NOT NULL,
    area_km2           NUMERIC,
    population_total   BIGINT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_regions_geom       ON regions USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_regions_country    ON regions (country_code);
CREATE INDEX IF NOT EXISTS idx_regions_nuts_level ON regions (nuts_level);

-- Population grid kept as a separate table; never joined to events as a point.
CREATE TABLE IF NOT EXISTS population_grid (
    grid_id            BIGSERIAL PRIMARY KEY,
    cell_code          TEXT UNIQUE,            -- source grid cell id if present
    population_total   INTEGER,
    population_male    INTEGER,
    population_female  INTEGER,
    pop_age_lt15       INTEGER,
    pop_age_15_64      INTEGER,
    pop_age_ge65       INTEGER,
    country_code       CHAR(2),                -- derived by spatial join, documented as derived
    geom               GEOMETRY(Polygon, 3035) NOT NULL   -- source CRS preserved
);

CREATE INDEX IF NOT EXISTS idx_popgrid_geom_3035 ON population_grid USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_popgrid_country    ON population_grid (country_code);

CREATE TABLE IF NOT EXISTS events (
    event_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type            TEXT NOT NULL,
    event_category        TEXT NOT NULL,
    affected_sector       TEXT,
    country_code          CHAR(2),
    region_code           TEXT REFERENCES regions(region_code),
    geographic_precision  TEXT NOT NULL CHECK (geographic_precision IN
                              ('country','nuts1','nuts2','nuts3','municipality','unknown')),
    occurred_at           TIMESTAMPTZ,
    published_at          TIMESTAMPTZ,
    ingested_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    event_status          TEXT,
    severity_reported     TEXT,
    source_confidence     NUMERIC,
    extraction_confidence NUMERIC,
    verification_status   TEXT NOT NULL DEFAULT 'reported'
                              CHECK (verification_status IN
                              ('reported','corroborated','verified','unconfirmed','retracted','disputed')),
    duplicate_cluster_id  TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_region     ON events (region_code);
CREATE INDEX IF NOT EXISTS idx_events_country    ON events (country_code);
CREATE INDEX IF NOT EXISTS idx_events_occurred   ON events (occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_published  ON events (published_at);

CREATE TABLE IF NOT EXISTS event_sources (
    event_id        UUID NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    source_id       TEXT NOT NULL REFERENCES source_registry(source_id),
    source_reference TEXT NOT NULL,
    raw_document_id  UUID,
    PRIMARY KEY (event_id, source_id, source_reference)
);

CREATE TABLE IF NOT EXISTS event_regions (
    event_id         UUID NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    region_code      TEXT NOT NULL REFERENCES regions(region_code),
    precision_level  TEXT NOT NULL CHECK (precision_level IN
                         ('country','nuts1','nuts2','nuts3','municipality','unknown')),
    is_primary       BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (event_id, region_code)
);

COMMIT;
