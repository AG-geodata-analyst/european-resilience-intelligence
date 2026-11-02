# Acceptance Criteria and Test Gates

Testing is a formal part of each phase. A portfolio project should show why a data
product can fail, not only that it runs.

## Test gates

| Gate | Focus | Key requirement |
| --- | --- | --- |
| **T1** | Ingestion | Every connector has automated tests with fixtures, including simulated API failures, malformed payloads, duplicates, format changes and rate limits |
| **T2** | Event quality | No event is marked verified without the required evidence; duplicate reports never become duplicate incidents |
| **T3** | Geospatial | Valid geometries, correct NUTS edition, correct projections; country-only events are never rendered as points; boundary changes do not silently corrupt history |
| **T4** | Indicators | Every displayed indicator has a definition, lineage and calculation method; no-data regions show *insufficient evidence* |
| **T5** | Machine learning | ML beats a defined baseline, errors and limitations documented; near-duplicates kept out of both train and test splits |
| **T6** | Simulation | Results traceable to input parameters and clearly marked simulated; same seed reproduces same output |
| **T7** | Operational & security | Stale data is treated as failure; credentials protected; no sensitive infrastructure or personal data exposed; licence and API terms respected |

## Baltic v1 minimum criteria

| Area | Criterion |
| --- | --- |
| Geographic coverage | Estonia, Latvia, Lithuania |
| Geographic reference | Official administrative boundaries and identifiers |
| Sources | ≥ 4 usable documented integrations of different types |
| Data engineering | Automated Airflow pipelines with retries and incremental processing |
| Database | PostgreSQL/PostGIS with documented schema |
| Event handling | Normalisation, provenance, deduplication |
| Data quality | Automated validation and source-freshness monitoring |
| Analytics | Documented regional indicators |
| Map | Interactive Baltic map with date and category filters |
| Resilience | ≥ 3 reproducible hypothetical disruption scenarios |
| Testing | Unit, integration, data-quality, geospatial, scenario |
| ML | ≥ 1 model validated against a baseline, *if included* |
| Deployment | Public demo or reproducible local deployment |
| Documentation | Architecture, data dictionary, methodology, limitations, test report |

Incident counts, model accuracy and real-world impact are **not** success criteria —
they depend on available evidence and cannot be guaranteed.

## Release gates

| Release | Gate |
| --- | --- |
| **R0** Foundation | Repeatable ingestion, traceable provenance, correct geography, zero duplicates in fixtures |
| **R1** Baltic Monitor | Validated connectors, documented indicators, tested quality, confirmed/unverified/simulated clearly separated |
| **R2** Resilience | Reproducible simulations, reviewed assumptions, sensitivity tests, modelled ≠ observed |
| **R3** Intelligent Monitoring | Improvement over baselines, documented errors, acceptable false positives, model can abstain |
| **R4** European Expansion | Per-country source validation, equivalent definitions, multilingual evaluation, no misleading comparisons |
