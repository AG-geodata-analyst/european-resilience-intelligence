# European Resilience Intelligence (ERI)

**Baltic Resilience Intelligence (BRI) — v0.1 "Baltic Evidence Monitor"**

A continuously operating, geospatial decision-support platform for monitoring *publicly reported* disruptive events, assessing essential-service continuity, and evaluating regional resilience across the Baltic states, with a scalable path to Europe.

> **Status:** MVP (Release 1) - Live ingestion from Cloudflare Radar and CERT-EU, PostGIS spatial database, and a Streamlit dashboard.

## What the platform answers
1. What disruptive incidents have been **publicly reported**?
2. Which regions and essential-service sectors are affected?
3. How reliable and recent is the available evidence?
4. Which services may be affected by a disruption in another sector?
5. How could a region improve continuity under different disruption scenarios?

## What the platform is not
- It is **not** a map of the probability that a region will be attacked.
- It is **not** an official emergency-warning service.
- It does **not** publish precise critical-infrastructure locations, exploitable vulnerabilities, or tactical recommendations.
- It does **not** treat "no reported incidents" as "safe".

## Key Features
- **Automated Ingestion**: Modular `SourceConnector` architecture (JSON API for Cloudflare Radar, XML/RSS for CERT-EU).
- **Spatial Database**: PostgreSQL + PostGIS with NUTS 2024 boundaries and Census 2021 grid population data.
- **Idempotency**: SHA-256 payload hashing and unique constraints prevent duplicate events.
- **Interactive Dashboard**: Streamlit application showing a geospatial map of recent reports.
- **Scenario Simulator**: NetworkX-based graph analysis showing cascading failures across essential services.

## Quickstart
```bash
cp .env.example .env          # then edit credentials
python3 -m venv .venv-eri
source .venv-eri/bin/activate
pip install -e ".[dev]"
docker compose up -d          # Start PostGIS
pytest tests/unit/ -q         # Run tests
streamlit run dashboard/app.py # Launch UI
```

## Documentation
- [`docs/PROJECT_SCOPE.md`](docs/PROJECT_SCOPE.md) — what is in and out of scope
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — analytical framework and evidence rules
- [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) — current scope and known limitations

## Licence
MIT
