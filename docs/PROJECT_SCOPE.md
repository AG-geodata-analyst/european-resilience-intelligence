# Project Scope — BRI v0.1

## 1. Purpose

Build a documented, reproducible evidence pipeline and decision-support application that
monitors publicly reported disruptive events and assesses essential-service continuity
across Estonia, Latvia and Lithuania.

## 2. Questions in scope

| # | Question | Output |
| --- | --- | --- |
| 1 | What disruptive incidents have been publicly reported? | Normalised, deduplicated event records |
| 2 | Which regions and sectors are affected? | Event-to-region and event-to-sector association |
| 3 | How reliable and recent is the evidence? | Confidence, provenance and freshness indicators |
| 4 | Which services may be affected by a disruption elsewhere? | Sector dependency graph |
| 5 | How could a region improve continuity? | Scenario simulation and intervention comparison |

## 3. Geographic scope

**v0.1 (Baltic):** Estonia (EE), Latvia (LV), Lithuania (LT).

Two analytical levels:

- **Country** — comparison of public reporting trends.
- **Administrative region** — NUTS, used for population context, verified regional
  disruptions and resilience indicators *when the source supports that resolution*.

Expansion beyond the Baltics is blocked until the Baltic version passes the
acceptance gates in `ACCEPTANCE_CRITERIA.md`.

## 4. Out of scope for v0.1

- Attack-probability prediction or any composite "threat score".
- Precise critical-infrastructure locations, vulnerabilities or targeting analysis.
- Real-time emergency alerting or any operational emergency-response function.
- Automated ingestion of water, drone, sabotage or transport incidents.
- Full European coverage.
- Personal data collection beyond what is published by official sources.

## 5. Analytical commitments

1. **No attack-probability claim.** The platform analyses reported events and resilience
   context; it simulates hypothetical service disruptions.
2. **No default-safe classification.** A region with no observations is displayed as
   *insufficient evidence*, never as low risk.
3. **No manufactured precision.** Country-level reports are never mapped to a point.
4. **No invented attribution.** An internet outage is not a cyberattack until a source says so.
5. **No silent simulation.** Synthetic output is always labelled as simulated.

## 6. v0.1 definition of done

BRI v0.1 "Baltic Evidence Monitor" must:

1. Collect public incident and disruption information from selected sources.
2. Preserve source provenance and publication timestamps.
3. Normalise and deduplicate the information.
4. Associate evidence with the correct Baltic administrative region.
5. Present results on an interactive map with source freshness and data confidence.

Explicitly excluded from v0.1: ML models, scenario engine, European map.

## 7. Policy context

The design follows the EU Critical Entities Resilience (CER) framework and NIS2, which
take an all-hazards approach to essential-service resilience. Natural and man-made
disruptions are treated in the same analytical framework; no event is assumed hostile
by category alone.
