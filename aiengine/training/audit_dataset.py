from pathlib import Path
import pandas as pd
BASE_DIR=Path(__file__).resolve().parent
DATASET=(BASE_DIR /
         "datasets" /
         "processed" /
         "firms_cleaned.parquet")
def main():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )
    df=pd.read_parquet(DATASET)
    print("Real FIRMS dataset audit")
    print(f"Rows:{len(df)}")
    print("\nColumns:")
    for column in df.columns:
        print(f"{column}")
    print("\nSatellite distribution:")
    print(df["satellite"].value_counts(dropna=False))
    print("\nConfidence distribution:")
    print(df["confidence"].value_counts(dropna=False))
    print("Day/Night distribution")
    print(df["daynight"].value_counts(dropna=False))
    if "type" in df.columns:
        print("FIRMS Type distribution")
        print(df["type"].value_counts(dropna=False))
        print("\nDate range: ")
        print(df['acquired_at'].min(),"->",df["acquired_at"].max())
        print("\nFRP statistics:")
        print(df["frp"].describe())
if __name__=="__main__":
    main()