import pandas as pd
def remove_duplicates(df:pd.DataFrame)->pd.DataFrame:
    before=len(df)
    df=df.drop_duplicates(subset=["event_id"])
    after=len(df)
    print(f"Duplicates removed: "f"{before-after}")
    return df