# Event Taxonomy

Internal analytical categories. Assignment to a category does **not** imply intent,
actor attribution or hostile origin.

## Categories

```
CYBER
    Ransomware
    DDoS
    Data breach
    Service disruption
    Other reported cyber incident

DIGITAL_INFRASTRUCTURE
    Internet outage
    Telecommunications disruption
    Digital service interruption

ENERGY
    Electricity interruption
    Generation disruption
    System stress observation

WATER
    Water service interruption

TRANSPORT
    Airport disruption
    Rail disruption
    Road disruption
    Port disruption

PHYSICAL_DISRUPTION
    Officially reported infrastructure incident
    Drone-related disruption
    Other publicly reported incident

NATURAL_HAZARD
    Flood
    Storm
    Wildfire
    Other emergency event
```

## Sector mapping

| Sector | Primary observation types |
| --- | --- |
| Electricity | Outages, duration, affected population, aggregate system stress |
| Telecommunications | Internet outages, connectivity anomalies |
| Water | Officially reported interruptions |
| Transport | Publicly reported service interruptions |
| Healthcare | Aggregate service disruption reports |
| Digital services | Publicly confirmed disruption of essential online services |

## Attribution rules

1. Preserve the **reported** cause. Never infer one.
2. `Internet outage` ≠ `cyberattack` — outages may result from maintenance, technical
   failure, natural hazards or government restrictions.
3. `System stress observation` (aggregate load/generation signal) ≠ consumer outage.
4. An event may have a confirmed category and an unknown cause; that is a valid state.

## Excluded at v0.1

Water outages, drone incidents, sabotage reports and transport interruptions are added
only once an attributable, usable, legally reusable source exists. A curated,
source-linked record beats a large volume of unreliable news-derived data.
