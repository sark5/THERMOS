import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)
from app.firms.client import FIRMSClient
from app.firms.parser import parse_firms_csv
from app.utils.validation import ( validate_coordinates,validate_frp,validate_required_columns,validate_numeric_fields,normalize_confidence)
from app.utils.normalization import normalize
from app.utils.deduplication import remove_duplicates
from app.firms.ingestion import insert_events

def main():
    print("THERMOS FIRMS")
    client=FIRMSClient()
    raw_data=client.get_area_data(
        source="VIIRS_NOAA21_NRT",
        area="68,6,97,36",
        days=1
    )
    df=parse_firms_csv(
        raw_data
    )
    validate_required_columns(df)
    df=validate_coordinates(df)
    df = validate_numeric_fields(df)
    df = normalize_confidence(df)
    df=validate_frp(df)
    df=normalize(df)
    df=df.dropna(subset=["acquired_at"])
    df=remove_duplicates(df)
    print()
    print(f"Final valid records: "
          f"{len(df)}")
    inserted,skipped,errors=insert_events(df)
    print("INGESTION")
    print(f"Inserted : {inserted}")
    print(f"Skipped : {skipped}")
    print(f"Errors : {errors}")
if __name__=="__main__":
    main()

