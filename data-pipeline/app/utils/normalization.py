import hashlib
import pandas as pd
def generate_event_id(
        row
)->str:
    value=(
        f"{row.get('satellite','')}|"
        f"{row.get('latitude','')}|"
        f"{row.get('longitude','')}|"
        f"{row.get('acq_date','')}|"
        f"{row.get('acq_time','')}"
    )
    digest=hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()
    return(
        "THM-"
        +digest[:24].upper()
    )
def normalize_dates(df:pd.DataFrame)->pd.DataFrame:
    df=df.copy()
    df["acq_time"]=(df["acq_time"].astype(str).str.zfill(4))
    df["acquired_at"]=pd.to_datetime(
        df["acq_date"].astype(str)
        +" "
        +df["acq_time"].str[:2]
        +":"
        +df["acq_time"].str[2:]
        +":00",
        utc=True,
        errors="coerce"
    )
    return df
def normalize(
        df:pd.DataFrame
)->pd.DataFrame:
    df=df.copy()
    df["event_id"]=df.apply(
        generate_event_id,
        axis=1
    )
    df=normalize_dates(df)
    return df