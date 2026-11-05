-- T3.1 invalid geometries
SELECT count(*) AS invalid_geoms FROM regions WHERE NOT ST_IsValid(geom);

-- T3.2 pinned NUTS edition
SELECT DISTINCT nuts_version FROM regions;

-- T3.3 region prefix matches country_code
SELECT count(*) AS mismatched_prefixes
FROM regions WHERE left(region_code, 2) <> country_code;

-- T3.4 event precision vs region NUTS level
SELECT count(*) AS precision_violations
FROM events e
JOIN regions r ON r.region_code = e.region_code
WHERE (e.geographic_precision = 'country' AND r.nuts_level <> 0)
   OR (e.geographic_precision = 'nuts1'   AND r.nuts_level <> 1)
   OR (e.geographic_precision = 'nuts2'   AND r.nuts_level <> 2)
   OR (e.geographic_precision = 'nuts3'   AND r.nuts_level <> 3);

-- T3.5 grid cells within Baltic bbox
SELECT count(*) AS outside_bbox
FROM population_grid
WHERE NOT ST_Within(
    geom,
    ST_Transform(ST_MakeEnvelope(19.0, 53.0, 29.0, 60.0, 4326), 3035)
);

-- T3.6 grid cells with derived country_code
SELECT count(*) AS orphan_cells FROM population_grid WHERE country_code IS NULL;
