import pandas as pd
import logger as lg
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT= CURRENT_FILE.parent.parent.parent

RAW_DIR= PROJECT_ROOT/"raw"
CLEAN_DIR= PROJECT_ROOT/"clean"

def ensure_dirs():
    if not CLEAN_DIR.exists():
        CLEAN_DIR.mkdir()
        lg.log_ok(f"Created clean directory at {CLEAN_DIR}")

def load():
    raw_dfs={}
    csv_files= list(RAW_DIR.glob("*.csv"))
    if not csv_files:
        lg.log_warn(f"No CSV files found in {RAW_DIR}")
        return raw_dfs

    for file_path in csv_files:
        dataset_name= file_path.stem
        df= pd.read_csv(file_path)
        raw_dfs[dataset_name]= df
        lg.log_ok(f"Loaded {dataset_name} ({len(raw_dfs[dataset_name])} rows)")

    return raw_dfs

def standardize_date(date_column, df):
    df[date_column]= pd.to_datetime(df[date_column],format="mixed",errors="coerce")
    df[date_column]= df[date_column].dt.strftime("%Y-%m-%d")
    lg.log_ok(f"Standardized date column '{date_column}'")

def validate_msisdn(msisdn_column,df):
    df[msisdn_column]= df[msisdn_column].astype(str)
    df[msisdn_column]=df[msisdn_column].str.replace(r"\D","", regex=True)
    df[msisdn_column]= df[msisdn_column].str[-9:]
    lg.log_ok(f"Validated MSISDN column '{msisdn_column}'")

def transform(dataframes):
    cleaned_dfs ={}

    for name,df in dataframes.items():
        lg.log_info(f"Processing dataset: {name}")
        initial_rows=len(df)

        #Drop all missing values
        df=df.dropna()

        #Drop all duplicates but keep the first occurence
        df=df.drop_duplicates(keep="first")

        for col in df.columns:
            if "date" in col.lower() or "timestamp" in col.lower():
                standardize_date(col,df)
            if "msisdn" in col.lower() or "phone" in col.lower():
                validate_msisdn(col,df)
        
        cleaned_dfs[name] =df
        lg.log_ok(
            f"Finished {name}: {initial_rows} -> {len(df)} rows "
            f"({initial_rows - len(df)} rows removed)"
        )


    return cleaned_dfs

def store(cleaned):
    for name,df in cleaned.items():
        output_path=CLEAN_DIR/f"cleaned_{name}.csv"
        df.to_csv(output_path,index=False)
        lg.log_ok(f"Saved cleaned file to {output_path}")


def main():
    ensure_dirs()
    raw= load()
    if raw:
        cleaned= transform(raw)
        store(cleaned)



if __name__ == "__main__":
    main()




