# Project Limitations

This document honestly outlines the current limitations of the Baltic Resilience Intelligence (BRI) v0.1 MVP.

## 1. Geospatial Scope
- **NUTS coverage**: Only Estonia, Latvia, and Lithuania (NUTS 0-3) are loaded. An event from outside these countries (e.g., EU-wide CERT advisories) will not plot on the map because it lacks a matching NUTS region in the database.
- **Precision**: We only plot at the country level (`geographic_precision='country'`). The system intentionally prevents manufacturing false precision.

## 2. Data Sources & Ingestion
- **CERT-EU Feed**: The `cert_eu.py` connector uses the EU-level feed. We have not yet implemented dedicated national CERT connectors.
- **Airflow**: The DAG is defined but is not currently running in production. The ingestion is executed manually or via local scripts.
- **Historical Data**: We only fetch the last 7 to 30 days. There is no historical backfill yet.

## 3. Machine Learning & Analytics
- **No ML yet**: The event classification and deduplication pipelines are currently rule-based.
- **Scenario Simulator**: The simulator uses a static, manually seeded dependency graph. It does not yet dynamically calculate the duration of cascading failures or the population affected using the Census grid.

## 4. CI/CD
- The GitHub Actions pipeline (`ci.yml`) runs `ruff` and `pytest` on the unit tests. It does not spin up a PostGIS container, so the integration tests are skipped in CI.
