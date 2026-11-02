# Analytical Methodology

## 1. Core distinction

The platform reports **observed and reported evidence**, not threat probability.

| Concept | What the platform shows |
| --- | --- |
| Observed incidents | Publicly reported, classified, deduplicated events |
| Threat activity | Trends in reported activity, with source coverage shown |
| Service disruption | Reported interruptions and system-level disruption indicators |
| Regional exposure | Aggregated population and socioeconomic context |
| Resilience | Available preparedness and continuity indicators |
| Data confidence | Evidence quality, completeness, provenance, freshness |
| Future scenarios | Simulated consequences of hypothetical disruptions |

## 2. The three dates

Never conflated, always stored separately:

| Field | Meaning |
| --- | --- |
| `occurred_at` | When the incident happened |
| `published_at` | When the source published it |
| `ingested_at` | When the platform collected it |

This prevents the classic error of treating a newly published article about an old
event as a new incident.

## 3. Six analytical dimensions

Kept separate on purpose — they measure different things and must not be collapsed
into a single score.

| # | Dimension | Example variables |
| --- | --- | --- |
| 1 | Reported Incident Activity | Unique events, distinct sources, category, recency, published severity, verification status |
| 2 | Essential-Service Disruption | Outages, duration, affected population, connectivity anomalies |
| 3 | Regional Exposure | Population, density, age distribution, urban/rural split |
| 4 | Essential-Service Dependency | Documented sector-to-sector relationships |
| 5 | Resilience & Preparedness | Warning channels, published guidance, continuity arrangements |
| 6 | Data Confidence | Last update, source count/type, coverage, verification, missing-data %, observed/estimated/simulated |

## 4. Verification levels

Every event carries exactly one:

| Level | Meaning |
| --- | --- |
| `reported` | Single source, not independently corroborated |
| `corroborated` | Two or more independent sources agree |
| `verified` | An official/authoritative source confirms |
| `unconfirmed` | Source describes a possible event without confirmation |
| `retracted` | Source corrected or withdrew the report |
| `disputed` | Sources conflict |

## 5. Geographic precision levels

Stored explicitly on every event; never inferred upward.

`country` · `nuts1` · `nuts2` · `nuts3` · `municipality` · `unknown`

If an official report identifies only the country, the event stays at country level.

## 6. Deduplication

Three articles about one electricity disruption = **one incident with three sources**.

Initial approach is rule-based: similar dates, overlapping geography, same category,
text similarity, shared official source references. Embedding-based matching is added
only if it demonstrably beats the baseline on a labelled set.

## 7. Indicator rules

- Every indicator has a documented definition, lineage and calculation method.
- No region defaults to "safe" or "low threat" when data is missing.
- Raw incident counts are **never** compared across countries without accounting for
  differences in reporting practice and source coverage.
- Composite indices, if ever built, are labelled *decision-support indicators* and are
  tested with sensitivity analysis — never described as validated probabilities.

## 8. Simulation rules

- Deterministic rule-based model first; Monte Carlo only where input distributions are
  defensible.
- All parameters are visible and editable.
- Results identify which inputs were measured and which were assumed.
- Synthetic results are never presented as proof of real-world effectiveness.
- Identical inputs and seed must reproduce identical outputs.

## 9. Versioning

Indicator definitions are versioned. When a calculation changes, previous results remain
attributable to the version that produced them.
