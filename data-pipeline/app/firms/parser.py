from io import StringIO
import pandas as pd
def parse_firms_csv(
        csv_data:str
) ->pd.DataFrame:
    df=pd.read_csv(
        StringIO(csv_data)
    )
    print(f"Parsed {len(df)} FIRMS records")
    print()
    print("Columns recieved.")
    print(list(df.columns))
    return df