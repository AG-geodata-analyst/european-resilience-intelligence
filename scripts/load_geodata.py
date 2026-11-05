#!/usr/bin/env python3
"""Load Baltic NUTS 2024 boundaries and the Census 2021 population grid into PostGIS.

Idempotent: re-running truncates and reloads the two geospatial tables.
Does not touch events, event_sources or event_regions.
"""
from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path

import geopandas as gpd
from shapely.geometry import MultiPolygon
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

BALTIC = {"EE", "LV", "LT"}
NUTS_VERSION = "2024"

NUTS_PATH = Path("data/raw/NUTS_RG_10M_2024_4326.geojson")
GRID_PATH = Path("data/raw/census_grid/ESTAT_Census_2021_V2.gpkg")  # adjust after Step 2.2
GRID_LAYER = None  # None = first layer, or set explicitly


def get_engine() -> Engine:
    user = os.getenv("POSTGRES_USER", "bri")
    pw = os.getenv("POSTGRES_PASSWORD", "change_me")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "bri")
    return create_engine(f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{db}")


def load_regions(engine: Engine) -> None:
    if not NUTS_PATH.exists():
        raise FileNotFoundError(f"Missing {NUTS_PATH}. Run Step 2.1 first.")

    gdf = gpd.read_file(NUTS_PATH)
    # GISCO column names: NUTS_ID, NAME_LATN, LEVL_CODE, CNTR_CODE
    required = {"NUTS_ID", "NAME_LATN", "LEVL_CODE", "CNTR_CODE", "geometry"}
    missing = required - set(gdf.columns)
    if missing:
        raise ValueError(f"NUTS file missing columns: {missing}. Got: {list(gdf.columns)}")

    gdf = gdf[gdf["CNTR_CODE"].isin(BALTIC)].copy()
    gdf = gdf.rename(columns={
        "NUTS_ID": "region_code",
        "NAME_LATN": "region_name",
        "LEVL_CODE": "nuts_level",
        "CNTR_CODE": "country_code",
    })

    # Guarantee MultiPolygon to match the schema
    gdf["geometry"] = gdf["geometry"].apply(
        lambda g: g if isinstance(g, MultiPolygon) else MultiPolygon([g]) if g is not None else None
    )
    gdf = gdf[gdf.geometry.notna()].to_crs(4326)
    gdf["nuts_version"] = NUTS_VERSION

    # Area in km² using an equal-area CRS, stored as an attribute
    gdf["area_km2"] = gdf.to_crs(3035).area / 1_000_000

    gdf = gdf.rename_geometry("geom")

    keep = ["region_code", "region_name", "nuts_level", "country_code",
            "nuts_version", "area_km2", "geom"]

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE regions CASCADE;"))
        gdf[keep].to_postgis(
            "regions", conn, if_exists="append", index=False,
            dtype={"geom": "GEOMETRY(MultiPolygon, 4326)"},
        )

    print(f"Loaded {len(gdf)} NUTS regions for {sorted(BALTIC)} (NUTS {NUTS_VERSION}).")


def load_population_grid(engine: Engine) -> None:
    if not GRID_PATH.exists():
        raise FileNotFoundError(f"Missing {GRID_PATH}. Run Step 2.2 first.")

    kwargs = {"layer": GRID_LAYER} if GRID_LAYER else {}
    gdf = gpd.read_file(GRID_PATH, **kwargs)

    # Column names vary slightly by release; map defensively.
    rename = {
        "T": "population_total",
        "M": "population_male",
        "F": "population_female",
        "Y_LT15": "pop_age_lt15",
        "Y_1564": "pop_age_15_64",
        "Y_GE65": "pop_age_ge65",
        "GRD_ID": "cell_code",
    }
    gdf = gdf.rename(columns={k: v for k, v in rename.items() if k in gdf.columns})

    # Derive country_code by spatial intersection with Baltic NUTS0 polygons.
    nuts = gpd.read_file(NUTS_PATH)
    nuts0 = nuts[(nuts["CNTR_CODE"].isin(BALTIC)) & (nuts["LEVL_CODE"] == 0)].to_crs(3035)
    gdf = gdf.to_crs(3035)
    joined = gpd.sjoin(gdf, nuts0[["CNTR_CODE", "geometry"]], how="inner", predicate="intersects")
    joined = joined.drop_duplicates(subset=["cell_code"] if "cell_code" in joined.columns else None)
    joined = joined.rename(columns={"CNTR_CODE": "country_code"})

    joined = joined.rename_geometry("geom")

    # Census columns arrive as float64 (NaN for empty cells); cast to
    # pandas nullable Int64 so Postgres receives integers or NULL.
    int_cols = ["population_total", "population_male", "population_female",
                "pop_age_lt15", "pop_age_15_64", "pop_age_ge65"]
    for c in int_cols:
        if c in joined.columns:
            # Census 2021 uses large negative sentinels (-1, -99999) to mark
            # confidential / unavailable age detail. Mask them to NULL so
            # aggregations ignore them; population totals have no sentinels.
            s = joined[c].where(joined[c] >= 0)
            joined[c] = s.round().astype("Int64")

    keep = [c for c in ["cell_code", "population_total", "population_male",
                        "population_female", "pop_age_lt15", "pop_age_15_64",
                        "pop_age_ge65", "country_code", "geom"] if c in joined.columns]

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE population_grid;"))
        joined[keep].to_postgis(
            "population_grid", conn, if_exists="append", index=False,
            dtype={"geom": "GEOMETRY(Polygon, 3035)"},
        )

    print(f"Loaded {len(joined)} population grid cells for {sorted(BALTIC)} (EPSG:3035).")


if __name__ == "__main__":
    engine = get_engine()
    load_regions(engine)
    load_population_grid(engine)
