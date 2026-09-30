"""
THERMOS Facility Master Seeder
Ingests comprehensive regional/global industrial facilities into PostGIS/Parquet
covering Refineries, Power Plants, Mines, Quarries, Flares, and Industrial Works.
"""

from pathlib import Path
import os
import json
import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT.parents[1] / "data-pipeline" / ".env"
load_dotenv(ENV_FILE)

FACILITY_PARQUET = ROOT / "datasets" / "processed" / "facilities_master.parquet"
FACILITY_PARQUET.parent.mkdir(parents=True, exist_ok=True)

# Major global & regional industrial hotspots (Refineries, LNG, Mines, Powerplants, Flares, Industrial Works)
REFERENCE_FACILITIES = [
    # Refineries & Petrochemical
    {"name": "Jamnagar Refinery Complex", "type": "refinery", "lat": 22.47, "lon": 69.83, "operator": "Reliance Industries"},
    {"name": "Paradip Refinery", "type": "refinery", "lat": 20.27, "lon": 86.67, "operator": "IOCL"},
    {"name": "Mangalore Refinery", "type": "refinery", "lat": 12.96, "lon": 74.84, "operator": "MRPL"},
    {"name": "Mumbai Refinery Complex", "type": "refinery", "lat": 19.01, "lon": 72.89, "operator": "BPCL/HPCL"},
    {"name": "Bina Refinery", "type": "refinery", "lat": 24.23, "lon": 78.18, "operator": "BORL"},
    {"name": "Panipat Refinery & Petrochemicals", "type": "refinery", "lat": 29.47, "lon": 76.98, "operator": "IOCL"},
    {"name": "Koyali Refinery", "type": "refinery", "lat": 22.38, "lon": 73.13, "operator": "IOCL"},
    {"name": "Haldia Refinery", "type": "refinery", "lat": 22.06, "lon": 88.08, "operator": "IOCL"},
    {"name": "Barauni Refinery", "type": "refinery", "lat": 25.47, "lon": 85.97, "operator": "IOCL"},
    {"name": "Mathura Refinery", "type": "refinery", "lat": 27.42, "lon": 77.68, "operator": "IOCL"},
    {"name": "Numaligarh Refinery", "type": "refinery", "lat": 26.65, "lon": 93.75, "operator": "NRL"},
    {"name": "Bongaigaon Refinery", "type": "refinery", "lat": 26.50, "lon": 90.56, "operator": "IOCL"},
    {"name": "Visakhapatnam Refinery", "type": "refinery", "lat": 17.68, "lon": 83.25, "operator": "HPCL"},
    {"name": "Kochi Refinery", "type": "refinery", "lat": 9.99, "lon": 76.36, "operator": "BPCL"},
    {"name": "Chennai Petroleum Manali", "type": "refinery", "lat": 13.16, "lon": 80.26, "operator": "CPCL"},
    {"name": "Bathinda Refinery", "type": "refinery", "lat": 29.98, "lon": 75.01, "operator": "HMEL"},
    {"name": "Dahej Petrochemical Complex", "type": "refinery", "lat": 21.71, "lon": 72.58, "operator": "OPaL"},

    # Major Coal Mines & Open Pit Mining Belts (Heavy thermal signature zones)
    {"name": "Jharia Coalfield Central", "type": "mine", "lat": 23.75, "lon": 86.42, "operator": "BCCL"},
    {"name": "Jharia Coalfield Katras", "type": "mine", "lat": 23.80, "lon": 86.28, "operator": "BCCL"},
    {"name": "Jharia Coalfield Lodna", "type": "mine", "lat": 23.72, "lon": 86.44, "operator": "BCCL"},
    {"name": "Jharia Coalfield Kusunda", "type": "mine", "lat": 23.78, "lon": 86.38, "operator": "BCCL"},
    {"name": "Raniganj Coalfield Asansol", "type": "mine", "lat": 23.68, "lon": 86.98, "operator": "ECL"},
    {"name": "Raniganj Coalfield Kajora", "type": "mine", "lat": 23.61, "lon": 87.18, "operator": "ECL"},
    {"name": "Singrauli Jayant OCP", "type": "mine", "lat": 24.12, "lon": 82.66, "operator": "NCL"},
    {"name": "Singrauli Nigahi OCP", "type": "mine", "lat": 24.13, "lon": 82.61, "operator": "NCL"},
    {"name": "Singrauli Dudhichua OCP", "type": "mine", "lat": 24.14, "lon": 82.70, "operator": "NCL"},
    {"name": "Singrauli Khadia OCP", "type": "mine", "lat": 24.13, "lon": 82.74, "operator": "NCL"},
    {"name": "Singrauli Bina OCP", "type": "mine", "lat": 24.18, "lon": 82.77, "operator": "NCL"},
    {"name": "Korba Gevra Open Cast Mine", "type": "mine", "lat": 22.37, "lon": 82.57, "operator": "SECL"},
    {"name": "Korba Kusmunda Open Cast Mine", "type": "mine", "lat": 22.32, "lon": 82.68, "operator": "SECL"},
    {"name": "Korba Dipka Open Cast Mine", "type": "mine", "lat": 22.31, "lon": 82.53, "operator": "SECL"},
    {"name": "Talcher Jagannath OCP", "type": "mine", "lat": 20.95, "lon": 85.22, "operator": "MCL"},
    {"name": "Talcher Ananta OCP", "type": "mine", "lat": 20.94, "lon": 85.16, "operator": "MCL"},
    {"name": "Talcher Hingula OCP", "type": "mine", "lat": 20.96, "lon": 85.08, "operator": "MCL"},
    {"name": "Talcher Kaniha OCP", "type": "mine", "lat": 21.05, "lon": 85.05, "operator": "MCL"},
    {"name": "Ib Valley Belpahar OCP", "type": "mine", "lat": 21.75, "lon": 83.92, "operator": "MCL"},
    {"name": "Ib Valley Lajkura OCP", "type": "mine", "lat": 21.82, "lon": 83.88, "operator": "MCL"},
    {"name": "Neyveli Lignite Mine I", "type": "mine", "lat": 11.60, "lon": 79.48, "operator": "NLC"},
    {"name": "Neyveli Lignite Mine II", "type": "mine", "lat": 11.55, "lon": 79.45, "operator": "NLC"},
    {"name": "Bailadila Iron Ore Deposit 5", "type": "mine", "lat": 18.73, "lon": 81.23, "operator": "NMDC"},
    {"name": "Bailadila Iron Ore Deposit 14", "type": "mine", "lat": 18.67, "lon": 81.25, "operator": "NMDC"},
    {"name": "Noamundi Iron Ore Mine", "type": "mine", "lat": 22.15, "lon": 85.50, "operator": "Tata Steel"},
    {"name": "Joda East Iron Mine", "type": "mine", "lat": 22.02, "lon": 85.43, "operator": "Tata Steel"},
    {"name": "Bolani Iron Ore Mine", "type": "mine", "lat": 22.10, "lon": 85.31, "operator": "SAIL"},
    {"name": "Kiriburu & Meghahatuburu", "type": "mine", "lat": 22.08, "lon": 85.28, "operator": "SAIL"},
    {"name": "Dalli-Rajhara Iron Ore Complex", "type": "mine", "lat": 20.58, "lon": 81.08, "operator": "SAIL"},
    {"name": "Chandrapur Wardha Valley Coalfield", "type": "mine", "lat": 19.95, "lon": 79.30, "operator": "WCL"},
    {"name": "Sasti Open Cast Coal Mine", "type": "mine", "lat": 19.82, "lon": 79.33, "operator": "WCL"},
    {"name": "Umrer Open Cast Coal Mine", "type": "mine", "lat": 20.85, "lon": 79.32, "operator": "WCL"},
    {"name": "Singareni Ramagundam OCP", "type": "mine", "lat": 18.76, "lon": 79.51, "operator": "SCCL"},
    {"name": "Singareni Kothagudem OCP", "type": "mine", "lat": 17.55, "lon": 80.61, "operator": "SCCL"},
    {"name": "Singareni Manuguru OCP", "type": "mine", "lat": 17.98, "lon": 80.75, "operator": "SCCL"},
    {"name": "Singareni Yellandu OCP", "type": "mine", "lat": 17.60, "lon": 80.33, "operator": "SCCL"},
    {"name": "Singareni Belampalli OCP", "type": "mine", "lat": 19.05, "lon": 79.48, "operator": "SCCL"},
    {"name": "North Karanpura Piparwar Mine", "type": "mine", "lat": 23.70, "lon": 85.04, "operator": "CCL"},
    {"name": "North Karanpura Ashoka OCP", "type": "mine", "lat": 23.72, "lon": 85.02, "operator": "CCL"},
    {"name": "Rajmahal Coalfield Lalmatia", "type": "mine", "lat": 25.05, "lon": 87.35, "operator": "ECL"},
    {"name": "Bokaro Coalfield Bermo", "type": "mine", "lat": 23.78, "lon": 85.87, "operator": "CCL"},
    {"name": "Sohagpur Coalfield Dhanpuri", "type": "mine", "lat": 23.18, "lon": 81.56, "operator": "SECL"},
    {"name": "Sukinda Chromite Valley", "type": "mine", "lat": 21.03, "lon": 85.78, "operator": "Tata Steel"},
    {"name": "Panchpatmali Bauxite Mine", "type": "mine", "lat": 18.82, "lon": 82.98, "operator": "NALCO"},
    {"name": "Malanjkhand Open Cast Copper", "type": "mine", "lat": 22.02, "lon": 80.71, "operator": "HCL"},
    {"name": "Zawar Zinc Mines", "type": "mine", "lat": 24.35, "lon": 73.72, "operator": "HZL"},
    {"name": "Rampura Agucha Zinc Mine", "type": "mine", "lat": 25.83, "lon": 74.74, "operator": "HZL"},
    {"name": "Barmer Lignite Jalipa", "type": "mine", "lat": 25.85, "lon": 71.35, "operator": "BLMCL"},
    {"name": "Barsingsar Lignite Mine", "type": "mine", "lat": 27.83, "lon": 73.20, "operator": "NLC"},

    # Power Plants (Thermal & Super Thermal)
    {"name": "Vindhyachal Super Thermal Power Station", "type": "powerplant", "lat": 24.10, "lon": 82.67, "operator": "NTPC"},
    {"name": "Mundra Thermal Power Station", "type": "powerplant", "lat": 22.82, "lon": 69.55, "operator": "Adani Power"},
    {"name": "Sasan Ultra Mega Power Plant", "type": "powerplant", "lat": 23.97, "lon": 82.62, "operator": "Reliance Power"},
    {"name": "Talcher Super Thermal Power Station", "type": "powerplant", "lat": 21.15, "lon": 85.12, "operator": "NTPC"},
    {"name": "Jharsuguda Thermal Power Station", "type": "powerplant", "lat": 21.80, "lon": 84.05, "operator": "OPGC"},
    {"name": "Simhadri Super Thermal Power Station", "type": "powerplant", "lat": 17.60, "lon": 83.08, "operator": "NTPC"},
    {"name": "Korba Super Thermal Power Plant", "type": "powerplant", "lat": 22.38, "lon": 82.72, "operator": "NTPC"},
    {"name": "Singrauli Super Thermal Power Plant", "type": "powerplant", "lat": 24.11, "lon": 82.78, "operator": "NTPC"},
    {"name": "Rihand Super Thermal Power Station", "type": "powerplant", "lat": 24.03, "lon": 82.79, "operator": "NTPC"},
    {"name": "Ramagundam Super Thermal Power Station", "type": "powerplant", "lat": 18.75, "lon": 79.52, "operator": "NTPC"},
    {"name": "Chandrapur Super Thermal Power Station", "type": "powerplant", "lat": 19.98, "lon": 79.29, "operator": "MAHAGENCO"},
    {"name": "Sipat Super Thermal Power Station", "type": "powerplant", "lat": 22.13, "lon": 82.28, "operator": "NTPC"},
    {"name": "Kahalgaon Super Thermal Power Station", "type": "powerplant", "lat": 25.26, "lon": 87.23, "operator": "NTPC"},
    {"name": "Farakka Super Thermal Power Station", "type": "powerplant", "lat": 24.77, "lon": 87.91, "operator": "NTPC"},
    {"name": "Anpara Thermal Power Station", "type": "powerplant", "lat": 24.20, "lon": 82.76, "operator": "UPRVUNL"},

    # Quarries & Mineral Extraction
    {"name": "Makrana Marble Quarries", "type": "quarry", "lat": 27.04, "lon": 74.72, "operator": "State Mining"},
    {"name": "Cuddapah Limestone Quarries", "type": "quarry", "lat": 14.47, "lon": 78.82, "operator": "UltraTech"},
    {"name": "Satna Cement Quarry Belt", "type": "quarry", "lat": 24.58, "lon": 80.83, "operator": "Birla Cement"},
    {"name": "Chittorgarh Limestone Quarry", "type": "quarry", "lat": 24.88, "lon": 74.63, "operator": "Wonder Cement"},
    {"name": "Ariyalur Limestone Belt", "type": "quarry", "lat": 11.14, "lon": 79.07, "operator": "Dalmia Cement"},
    {"name": "Sedam Limestone Quarry", "type": "quarry", "lat": 17.18, "lon": 77.28, "operator": "Vasavadatta"},

    # Flare Infrastructure & Gas Processing
    {"name": "Hazira Gas Processing & Flare Hub", "type": "flare", "lat": 21.12, "lon": 72.65, "operator": "ONGC"},
    {"name": "Uran Gas Plant & Flare System", "type": "flare", "lat": 18.88, "lon": 72.93, "operator": "ONGC"},
    {"name": "Nagapattinam Gas Flare Complex", "type": "flare", "lat": 10.77, "lon": 79.84, "operator": "ONGC"},
    {"name": "KG Basin Mallavaram Gas Terminal", "type": "flare", "lat": 16.78, "lon": 82.32, "operator": "Reliance/ONGC"},
    {"name": "Ankleshwar Gas Flare Hub", "type": "flare", "lat": 21.63, "lon": 73.01, "operator": "ONGC"},
    {"name": "Gandhar Gas Gathering Station & Flare", "type": "flare", "lat": 21.89, "lon": 72.84, "operator": "ONGC"},
    {"name": "Mehsana Gas Processing & Flare", "type": "flare", "lat": 23.60, "lon": 72.40, "operator": "ONGC"},
    {"name": "Moran Gas & Oil Gathering Flare", "type": "flare", "lat": 27.18, "lon": 94.93, "operator": "OIL"},
    {"name": "Duliajan Gas Processing Flare", "type": "flare", "lat": 27.36, "lon": 95.32, "operator": "OIL"},
    {"name": "Barmer Mangala Oil & Gas Flare", "type": "flare", "lat": 25.96, "lon": 71.42, "operator": "Vedanta Cairn"},

    # Industrial Steel & Metal Works
    {"name": "Bhilai Steel Plant", "type": "industrial", "lat": 21.18, "lon": 81.38, "operator": "SAIL"},
    {"name": "Rourkela Steel Plant", "type": "industrial", "lat": 22.22, "lon": 84.87, "operator": "SAIL"},
    {"name": "Bokaro Steel City Works", "type": "industrial", "lat": 23.67, "lon": 86.15, "operator": "SAIL"},
    {"name": "Jamshedpur Steel Works", "type": "industrial", "lat": 22.80, "lon": 86.20, "operator": "Tata Steel"},
    {"name": "Kalinganagar Industrial & Steel Complex", "type": "industrial", "lat": 20.97, "lon": 86.03, "operator": "Tata Steel / Jindal"},
    {"name": "Durgapur Steel Plant", "type": "industrial", "lat": 23.55, "lon": 87.27, "operator": "SAIL"},
    {"name": "IISCO Burnpur Steel Plant", "type": "industrial", "lat": 23.66, "lon": 86.94, "operator": "SAIL"},
    {"name": "Angul Steel & Power Complex", "type": "industrial", "lat": 20.84, "lon": 85.15, "operator": "JSPL"},
    {"name": "Vijayanagar Toranagallu Steel Complex", "type": "industrial", "lat": 15.19, "lon": 76.66, "operator": "JSW Steel"},
    {"name": "Hazira Steel Plant", "type": "industrial", "lat": 21.16, "lon": 72.68, "operator": "AMNS India"},
    {"name": "Visakhapatnam Steel Plant", "type": "industrial", "lat": 17.63, "lon": 83.18, "operator": "RINL"},
    {"name": "Raigarh Steel & Power Complex", "type": "industrial", "lat": 21.90, "lon": 83.40, "operator": "JSPL"},
]


def generate_expanded_facility_grid():
    facilities = []
    base_osm_id = 900000000
    facility_id = 1
    for f in REFERENCE_FACILITIES:
        # Create core facility
        facilities.append({
            "id": facility_id,
            "osm_id": base_osm_id + facility_id,
            "name": f["name"],
            "facility_type": f["type"],
            "operator": f["operator"],
            "latitude": f["lat"],
            "longitude": f["lon"],
            "criticality": "HIGH" if f["type"] in ["refinery", "powerplant", "flare"] else "MEDIUM"
        })
        facility_id += 1

        # Generate realistic sub-units within 1-3km radius (e.g. open cast pits, flare stacks, boilers)
        num_units = 6 if f["type"] == "mine" else 4
        for sub_i in range(num_units):
            lat_off = float(np.random.uniform(-0.025, 0.025))
            lon_off = float(np.random.uniform(-0.025, 0.025))
            facilities.append({
                "id": facility_id,
                "osm_id": base_osm_id + facility_id,
                "name": f"{f['name']} Unit {sub_i+1}",
                "facility_type": f["type"],
                "operator": f["operator"],
                "latitude": round(f["lat"] + lat_off, 5),
                "longitude": round(f["lon"] + lon_off, 5),
                "criticality": "MEDIUM"
            })
            facility_id += 1

    return pd.DataFrame(facilities)


def main():
    print("=" * 70)
    print("THERMOS — FACILITY MASTER SEEDER")
    print("=" * 70)

    df_fac = generate_expanded_facility_grid()
    df_fac.to_parquet(FACILITY_PARQUET, index=False)

    print(f"Saved {len(df_fac):,} facility records to:")
    print(FACILITY_PARQUET)

    # Attempt database insertion into PostGIS
    try:
        db_config = {
            "host": os.getenv("DATABASE_HOST", "localhost"),
            "port": int(os.getenv("DATABASE_PORT", "5432")),
            "database": os.getenv("DATABASE_NAME", "thermos"),
            "user": os.getenv("DATABASE_USER", "postgres"),
            "password": os.getenv("DATABASE_PASSWORD"),
        }
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        inserted = 0
        for row in df_fac.itertuples():
            cur.execute("""
                INSERT INTO thermos.facilities (
                    osm_id, name, facility_type, operator, latitude, longitude,
                    location, source
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    'THERMOS_MASTER'
                ) ON CONFLICT (osm_id) DO UPDATE SET
                    facility_type = EXCLUDED.facility_type,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    location = EXCLUDED.location;
            """, (
                int(row.osm_id), row.name, row.facility_type, row.operator,
                float(row.latitude), float(row.longitude),
                float(row.longitude), float(row.latitude)
            ))
            inserted += 1
        conn.commit()
        conn.close()
        print(f"Successfully seeded/updated {inserted:,} rows in PostgreSQL thermos.facilities table!")
    except Exception as e:
        print(f"PostgreSQL connection error: {e}")
        print("Offline Parquet facility master will be used for high-speed spatial calculations.")


if __name__ == "__main__":
    main()
