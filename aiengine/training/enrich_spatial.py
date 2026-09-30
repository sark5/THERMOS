"""
THERMOS Spatial Enrichment Engine
Computes granular multi-category spatial proximity, density, and facility attribution
across all thermal events/sources.
"""

from pathlib import Path
import os
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "datasets" / "processed" / "firms_master.parquet"
OUTPUT = ROOT / "datasets" / "processed" / "firms_spatial_enriched.parquet"
FACILITY_PARQUET = ROOT / "datasets" / "processed" / "facilities_master.parquet"

ENV_FILE = ROOT.parents[1] / "data-pipeline" / ".env"
load_dotenv(ENV_FILE)

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", "5432")),
    "database": os.getenv("DATABASE_NAME", "thermos"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD"),
}


def load_facilities():
    # Attempt DB fetch first
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = "SELECT id, osm_id, name, facility_type, operator, latitude, longitude FROM thermos.facilities WHERE location IS NOT NULL;"
        df_fac = pd.read_sql_query(query, conn)
        conn.close()
        if len(df_fac) > 0:
            print(f"Loaded {len(df_fac):,} facilities from PostgreSQL PostGIS.")
            return df_fac
    except Exception:
        pass

    # Fallback to Parquet facility master
    if FACILITY_PARQUET.exists():
        df_fac = pd.read_parquet(FACILITY_PARQUET)
        print(f"Loaded {len(df_fac):,} facilities from Parquet facility master.")
        return df_fac

    # Generate via seeder if missing
    from seed_facility_master import generate_expanded_facility_grid
    df_fac = generate_expanded_facility_grid()
    print(f"Generated {len(df_fac):,} reference facilities.")
    return df_fac


def latlon_to_cartesian(lat, lon):
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    R = 6371.0  # Earth radius in km
    x = R * np.cos(lat_rad) * np.cos(lon_rad)
    y = R * np.cos(lat_rad) * np.sin(lon_rad)
    z = R * np.sin(lat_rad)
    return np.column_stack([x, y, z])


def enrich_spatial_vectorized(df_events, df_fac):
    print("Building spatial k-d trees for multi-category distance indexing...")
    event_coords = latlon_to_cartesian(df_events["latitude"].values, df_events["longitude"].values)
    fac_coords = latlon_to_cartesian(df_fac["latitude"].values, df_fac["longitude"].values)

    all_tree = cKDTree(fac_coords)
    dist_all, idx_all = all_tree.query(event_coords, k=1)

    df_events["facility_id"] = df_fac["id"].values[idx_all]
    df_events["facility_name"] = df_fac["name"].values[idx_all]
    df_events["facility_type"] = df_fac["facility_type"].values[idx_all]
    df_events["distance_to_facility"] = dist_all

    # Category-specific distances (refinery, powerplant, mine, quarry, flare)
    categories = ["refinery", "powerplant", "mine", "quarry", "flare"]

    for cat in categories:
        mask = df_fac["facility_type"].str.lower() == cat
        col_name = f"distance_to_{cat}"
        if mask.sum() > 0:
            cat_tree = cKDTree(fac_coords[mask])
            dist_cat, _ = cat_tree.query(event_coords, k=1)
            df_events[col_name] = dist_cat
        else:
            df_events[col_name] = 999.0

    # Inside facility boundary heuristic (within 0.5 km of known footprint)
    df_events["inside_facility_boundary"] = df_events["distance_to_facility"] <= 0.5

    # Density & count within 500m and 1km
    counts_500m = all_tree.query_ball_point(event_coords, r=0.5, return_length=True)
    counts_1km = all_tree.query_ball_point(event_coords, r=1.0, return_length=True)

    df_events["nearest_facility_count_500m"] = counts_500m
    df_events["nearest_facility_count_1km"] = counts_1km
    df_events["industrial_facility_density"] = counts_1km / (np.pi * 1.0**2)

    # Context indicators
    df_events["industrial_context"] = np.where(df_events["distance_to_facility"] <= 3.0, 1.0, 0.0)
    df_events["mining_context"] = np.where(df_events["distance_to_mine"] <= 3.0, 1.0, 0.0)

    return df_events


def main():
    print("=" * 70)
    print("THERMOS — SPATIAL ENRICHMENT ENGINE")
    print("=" * 70)

    if not INPUT.exists():
        raise FileNotFoundError(f"Input dataset not found: {INPUT}")

    print(f"\nLoading input observations from {INPUT}...")
    df = pd.read_parquet(INPUT)
    print(f"Input rows: {len(df):,}")

    df_fac = load_facilities()
    merged = enrich_spatial_vectorized(df, df_fac)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(OUTPUT, index=False)

    print("\n" + "=" * 70)
    print("SPATIAL ENRICHMENT COMPLETE")
    print("=" * 70)
    print(f"Saved enriched parquet to: {OUTPUT}")
    print(f"Matched facility rows: {merged['facility_id'].notna().sum():,}")
    print(f"Mean distance to nearest facility: {merged['distance_to_facility'].mean():.2f} km")
    print("\nFacility Type Distribution:")
    print(merged["facility_type"].value_counts().to_string())


if __name__ == "__main__":
    main()