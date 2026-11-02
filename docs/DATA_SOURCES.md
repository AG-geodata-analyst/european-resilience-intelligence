# Data Source Catalogue

Work Package 2 deliverable. Human-readable companion to
[`config/sources.yaml`](../config/sources.yaml), which is the machine-readable
version consumed by the ingestion layer.

**Last reviewed:** 2026-11-02
**Status:** feasibility assessment — no connector is implemented yet.

> **Verification note.** The access-model descriptions below were drafted from
> source documentation and must be re-checked against the live pages before any
> connector is written. A public portfolio repository should not contain an
> unverified claim about a national authority's data-access model.

## Initial source priority

The first release is buildable with these source families alone:

1. **GISCO + population grid** — geospatial foundation
2. **Cloudflare Radar** — first automated service-disruption source
3. **National CERT public reports** (EE, LV, LT) — cyber incident context
4. **ENTSO-E / Elering** — aggregate electricity-system indicators
5. **Copernicus EMS** — all-hazards emergency mapping

That is already enough for a credible first release.

## Geographic and population data

| Source | Use | Access | Role |
| --- | --- | --- | --- |
| Eurostat GISCO NUTS | Country and regional boundaries | Download/API | Core |
| Eurostat 2021 population grid | Population context at 1 km² | Download (EPSG:3035) | Core |
| Eurostat census statistics | Age groups, socioeconomic attributes | Download/API | Additional |

The 2021 grid provides an EU-wide 1 km² representation that is reusable when
expanding beyond the Baltics. Note: grid aggregates cannot be attributed to
individual events.

## Cybersecurity and threat reporting

| Source | Coverage | Initial use |
| --- | --- | --- |
| CERT-EE / RIA | Estonia | Public advisories and reporting |
| CERT.LV | Latvia | Public advisories and incident reports |
| NKSC | Lithuania | Public cybersecurity reports and statistics |
| ENISA | EU | Threat landscape, sector analysis, methodology |

The three national CERTs have **different data-access models**, and none of
them offers an openly downloadable live incident database.

- **CERT-EE** describes its role as monitoring incidents and coordinating
  response. The public RIA page describes the reporting environment primarily
  as a channel for authorities and service providers to submit detailed
  information.
- **CERT.LV** publishes quarterly activity reviews with incident counts.
  Useful historical evidence, but periodic — not a real-time feed.
- **NKSC** publishes national aggregate statistics. Useful, but limited
  regional resolution.

**Implementation decision:** begin with automated checking of public notices
plus structured manual import of published statistics. The platform does not
have access to confidential CERT incident records and will never claim to.

## Internet connectivity and outages

| Source | Coverage | Access |
| --- | --- | --- |
| Cloudflare Radar | Global | REST API, bearer token |

A promising candidate for the first automated service-disruption source.
Cloudflare documents an outage endpoint returning recent Internet outages and
anomalies, including dates, affected locations and reported causes where
available.

**Precision warning:** an Internet outage is not automatically a cyberattack.
It could result from maintenance, technical failure, natural hazards,
government restrictions, or other causes. The platform preserves the reported
attribution and never invents one.

## Electricity-system information

| Source | Coverage | Access |
| --- | --- | --- |
| ENTSO-E Transparency Platform | EU | REST API, registration required |
| Elering | Estonia | Web + historical archive |

Used **as an aggregate system-condition signal only**. Changes in national
load, generation or cross-border flows do not by themselves demonstrate that
consumers experienced a local electricity outage.

**Warning:** Elering's Estfeed Datahub is not a general-purpose public
open-data feed. It has eligibility and contract requirements for metering-data
access. The public project is not built on access we do not have.

## Natural and other emergencies

| Source | Coverage | Access |
| --- | --- | --- |
| Copernicus EMS (Mapping) | Global | REST API |

Supports programmatic discovery of current and historical activations and
access to vector/raster products. Enables floods, wildfires, storms and other
emergencies to be included. Important because civilian resilience must account
for natural and man-made disruptions, not treat every event as hostile.

## Emergency warning systems

The BEREC public-warning-systems database documents the alerting channels (SMS,
cell broadcast, sirens) each European country uses. It is a **reference
dataset, not a live alert stream**. For the Baltic MVP we create a small
curated reference table for each country, linking to the official public
information page.

## Deferred sources

Not part of the v0.1 promise:

- Water service interruptions
- Drone incidents
- Sabotage reports
- Transport interruptions

These are not standardised across the Baltic states. A category is added only
after we have identified an attributable, usable and legally reusable data
source. A manually curated, source-linked record is preferable to a large
quantity of unreliable news-derived data.

## Source onboarding checklist

For every new source (and every new country in later releases):

1. Find official national CERT and civil-protection sources.
2. Identify open APIs, RSS feeds or downloadable datasets.
3. **Check data-use licenses and API terms.**
4. Determine the available geographical resolution.
5. Translate or normalize local terminology.
6. Test the event classifier on the country's language.
7. Evaluate publication delays and historical availability.
8. Add the source to the coverage matrix in
   [`config/sources.yaml`](../config/sources.yaml).

## Licensing and terms — do not skip

Before any connector is written:

- Confirm the source's license permits redistribution of derived data.
- Confirm the API's terms permit automated polling at the intended frequency.
- Record both in `source_registry` when the schema is created.
- If a source's terms are unclear, treat it as `deferred` until resolved.
