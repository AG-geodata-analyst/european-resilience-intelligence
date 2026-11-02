-- Initialised by the PostGIS image on first container start.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- used later for duplicate-event text matching
