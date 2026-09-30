from pathlib import Path
import pandas as pd
from firms_schema import validate_schema
def audit_file(file_path:str):
    path=Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"File does not esist: {path}"
        )
    df=pd.read_csv(path)
    schema_result=validate_schema(df.columns)
    report={
        "file":str(path),
        "rows":int(len(df)),
        "columns":int(len(df.columns)),
        "missing_values":{},
        "duplicate_rows":int(df.duplicated().sum()),
        "schema_valid":schema_result["valid"],
        "missing_optional_columns":schema_result["missing_optional"],
    }
    for column in df.columns:
        missing_count=int(df[column].isna().sum())
        if missing_count >0:
            report["missing_values"][column]=missing_count
    return report
def print_report(report):
    print("FIRMS DATA QUALITY REPORT")
    print(f"File:{report['file']}")
    print(f"Rows:{report['rows']}")
    print(f"Columns:{report['columns']}")
    print(f"Duplicate rows: "
          f"{report['duplicate_rows']}")
    if report["missing_values"]:
        print("Missing Values: ")
        for column,count in(report['missing_values'].items()):
            print(f"{column}:{count}")
    else:
        print("Missing Values: None")
    if report["missing_optional_columns"]:
        print("Missing Optional Columns: ")
        for column in report["missing_optional_columns"]:
            print(f"{column}")
    else:
        print("Missing Optional Columns: None")