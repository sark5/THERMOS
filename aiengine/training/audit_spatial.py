from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATASET = (
	ROOT
	/ "datasets"
	/ "processed"
	/ "firms_spatial_enriched.parquet"
)

SPATIAL_COLUMNS = [
	"facility_id",
	"distance_to_facility",
	"inside_facility_boundary",
	"industrial_context",
	"mining_context",
]


def main():
	if not DATASET.exists():
		raise FileNotFoundError(
			f"Spatial dataset not found: {DATASET}\n"
			"Run enrich_spatial.py first."
		)

	df = pd.read_parquet(DATASET)

	print("=" * 70)
	print("THERMOS - SPATIAL DATASET AUDIT")
	print("=" * 70)

	print(f"\nRows: {len(df):,}")
	print(f"Columns: {len(df.columns)}")

	missing_columns = [
		column
		for column in SPATIAL_COLUMNS
		if column not in df.columns
	]

	if missing_columns:
		raise ValueError(
			"Spatial columns missing from dataset: "
			+ ", ".join(missing_columns)
		)

	matched = df["facility_id"].notna()
	print(f"\nFacility matches: {matched.sum():,}")
	print(f"Facility unmatched: {(~matched).sum():,}")

	print("\nSpatial column missing percentage:")
	print(
		df[SPATIAL_COLUMNS]
		.isna()
		.mean()
		.mul(100)
		.round(2)
		.to_string()
	)

	print("\nFacility types:")
	if "facility_type" in df.columns:
		print(
			df["facility_type"]
			.value_counts(dropna=False)
			.head(20)
			.to_string()
		)
	else:
		print("facility_type column is missing")

	print("\nDistance statistics:")
	print(df["distance_to_facility"].describe().to_string())

	print("\n" + "=" * 70)
	print("SPATIAL AUDIT COMPLETE")
	print("=" * 70)


if __name__ == "__main__":
	main()
