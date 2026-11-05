-- Population per NUTS3 region (grid aggregation)
SELECT r.region_code, r.region_name, r.country_code,
       ROUND(SUM(g.population_total)) AS population_from_grid
FROM regions r
LEFT JOIN population_grid g
       ON ST_Intersects(r.geom::geography, g.geom::geography)
WHERE r.nuts_level = 3
GROUP BY r.region_code, r.region_name, r.country_code
ORDER BY r.country_code, r.region_code;

-- Unique events per region (empty until ingestion exists)
SELECT r.region_code, count(e.event_id) AS events
FROM regions r
LEFT JOIN events e ON e.region_code = r.region_code
GROUP BY r.region_code
ORDER BY events DESC;

-- Events per month
SELECT date_trunc('month', occurred_at) AS month, count(*)
FROM events
GROUP BY 1 ORDER BY 1;

-- Regions with no grid cells and no events (insufficient evidence)
SELECT r.region_code, r.region_name
FROM regions r
LEFT JOIN population_grid g ON ST_Intersects(r.geom::geography, g.geom::geography)
LEFT JOIN events e ON e.region_code = r.region_code
WHERE g.grid_id IS NULL AND e.event_id IS NULL;
