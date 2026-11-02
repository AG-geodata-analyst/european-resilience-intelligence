# European Resilience Intelligence (ERI)

**Baltic Resilience Intelligence (BRI) — v0.1 "Baltic Evidence Monitor"**

A continuously operating, geospatial decision-support platform for monitoring *publicly
reported* disruptive events, assessing essential-service continuity, and evaluating
regional resilience across the Baltic states, with a scalable path to Europe.

> **Status:** pre-alpha. Repository scaffold and analytical framework only.
> No data ingestion is implemented yet.

---

## What the platform answers

1. What disruptive incidents have been **publicly reported**?
2. Which regions and essential-service sectors are affected?
3. How reliable and recent is the available evidence?
4. Which services may be affected by a disruption in another sector?
5. How could a region improve continuity under different disruption scenarios?

## What the platform is not

- It is **not** a map of the probability that a region will be attacked.
- It is **not** an official emergency-warning service.
- It does **not** publish precise critical-infrastructure locations, exploitable
  vulnerabilities, or tactical recommendations.
- It does **not** treat "no reported incidents" as "safe".

Public incident reporting is incomplete and uneven. An increase in reports may reflect
more incidents, better reporting, or increased attention. Every map layer therefore ships
with a **data-confidence and source-coverage** indicator.

## Design principles

| Principle | Consequence |
| --- | --- |
| Evidence before modelling | Build a trustworthy pipeline first, analytics second, ML last |
| Three dates, never conflated | `occurred_at` ≠ `published_at` ≠ `ingested_at` |
| Never manufacture precision | Country-level reports stay country-level |
| Provenance is mandatory | Every derived event traces back to a preserved raw record |
| Simulations are labelled | Synthetic output never mixes with observed data |
| Comparable or silent | Cross-country rankings require comparable coverage |

## Repository layout

```
config/      source registry, taxonomy, indicator and geography definitions
dags/        Airflow DAGs (added in a later work package)
src/         ingestion, processing, geospatial, indicators, simulation, api
models/      trained models and evaluation reports
dashboard/   Streamlit prototype, later FastAPI + MapLibre frontend
sql/         schemas, migrations, analytical queries
tests/       unit, integration, data-quality, geospatial, model, scenario
docs/        scope, methodology, taxonomy, sources, acceptance criteria
scripts/     bootstrap, historical backfill, demo-data generation
```

## Quickstart

```bash
cp .env.example .env          # then edit credentials
make venv && source .venv/bin/activate
make install-dev
make db-up                    # PostGIS on :5432, Adminer on :8080
make test
```

## Documentation

- [`docs/PROJECT_SCOPE.md`](docs/PROJECT_SCOPE.md) — what is in and out of scope
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — analytical framework and evidence rules
- [`docs/EVENT_TAXONOMY.md`](docs/EVENT_TAXONOMY.md) — event and sector classification
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — source catalogue and feasibility
- [`docs/ACCEPTANCE_CRITERIA.md`](docs/ACCEPTANCE_CRITERIA.md) — test gates and release criteria

## Disclaimer

This platform provides public-source monitoring and regional resilience analysis.
It is not an official emergency-warning service. For immediate safety information,
follow the relevant national authorities.

## Licence

MIT — see [`LICENSE`](LICENSE).
