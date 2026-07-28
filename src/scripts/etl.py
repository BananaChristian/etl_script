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

def validate_msisdn(msisdn_column, df, strict_utel_only=False) -> pd.DataFrame:
    if msisdn_column not in df.columns:
        return df

    # Clean format (strip floats, non-digits, country code 256, and leading 0)
    sdf = df[msisdn_column].astype(str).str.replace(r"\.0$", "", regex=True)
    sdf = sdf.str.replace(r"\D", "", regex=True)
    sdf = sdf.str.replace(r"^256", "", regex=True)
    sdf = sdf.str.replace(r"^0", "", regex=True)

    # Check general 9-digit phone length
    is_valid_len = sdf.str.len() == 9

    # Only restrict to UTEL prefixes IF this is an originating/UTEL-owned number
    if strict_utel_only:
        utel_prefixes = ("71", "74")  # Official UTEL prefixes
        is_valid_prefix = sdf.str.startswith(utel_prefixes)
        is_valid = is_valid_len & is_valid_prefix
    else:
        # Off-net / Recipient numbers just need to be structurally valid phone numbers
        is_valid = is_valid_len

    invalid_count = (~is_valid).sum()
    df[msisdn_column] = sdf.where(is_valid, None)

    if invalid_count > 0:
        lg.log_warn(
            f"Column '{msisdn_column}': Flagged '{invalid_count}' invalid MSISDN(s) as invalid"
        )
    else:
        lg.log_ok(f"Validated MSISDN column '{msisdn_column}'")

    return df

def validate_amount(amount_column,df):
    if amount_column not in df.columns:
        return df
    
    is_valid= df[amount_column] > 0
    invalid_count = (~is_valid).sum()

    df[amount_column] = df[amount_column].where(is_valid,None)

    if invalid_count > 0:
        lg.log_warn(f"Column '{amount_column}: Flagged '{invalid_count}' negative/zero amount(s) as invalid")

    return df

def extract_msisdn_and_trim_subscriber(cleaned_dfs):
    sub_key = None
    for k in cleaned_dfs.keys():
        if k.lower() in ["subscribers", "subscriber"]:
            sub_key = k
            break

    if not sub_key:
        return

    sub_df = cleaned_dfs[sub_key]

    msisdn_col = next(
        (c for c in sub_df.columns if "msisdn" in c.lower()), None
    )

    if msisdn_col and "SubscriberID" in sub_df.columns:  
        lg.log_info("Creating  MSISDN table from Subscribers...")

        msisdn_columns = ["MSISDN", "SubscriberID"] 
        msisdn_df = sub_df[[msisdn_col, "SubscriberID"]].copy() 
        msisdn_df.columns = msisdn_columns

        if "ActivationDate" in sub_df.columns:
            msisdn_df["ActivationDate"] = sub_df["ActivationDate"]
        else:
            msisdn_df["ActivationDate"] = "2026-01-01"

        msisdn_df["Status"] = "Active"

        # Deduplicate MSISDN primary key
        msisdn_df = msisdn_df.drop_duplicates(subset=["MSISDN"])
        cleaned_dfs["MSISDN"] = msisdn_df
        lg.log_ok(
            f"Created 'MSISDN' table with {len(msisdn_df)} unique records"
        )

        erd_subscriber_cols = [
            c
            for c in ["SubscriberID", "SubscriberName", "Gender", "Region"]  
            if c in sub_df.columns
        ]
        cleaned_dfs[sub_key] = sub_df[erd_subscriber_cols].drop_duplicates(
            subset=["SubscriberID"]
        )
        lg.log_ok(f"Trimmed '{sub_key}' table ")


def transform(dataframes):
    cleaned_dfs = {}

    for name, df in dataframes.items():
        lg.log_info(f"Processing dataset: {name}")
        initial_rows = len(df)

        for col in df.columns:
            if "date" in col.lower() or "timestamp" in col.lower():
                standardize_date(col, df)
    
            if "msisdn" in col.lower() or "phone" in col.lower():
            # Only enforce UTEL ownership on sender/originator columns
                is_originator = any(
                    kw in col.lower() for kw in ["calling", "source", "subscriber"]
                ) or name.lower() == "subscribers"
        
                df = validate_msisdn(col, df, strict_utel_only=is_originator)

            if "amount" in col.lower() or "fee" in col.lower() or "charge" in col.lower():
                validate_amount(col,df)

        # Drop missing values
        df = df.dropna()

        # Drop duplicates
        df = df.drop_duplicates(keep="first")

        cleaned_dfs[name] = df
        lg.log_ok(
            f"Finished {name}: {initial_rows} -> {len(df)} rows "
            f"({initial_rows - len(df)} rows removed)"
        )

    extract_msisdn_and_trim_subscriber(cleaned_dfs)

    return cleaned_dfs

def store(cleaned):
    for name,df in cleaned.items():
        output_path=CLEAN_DIR/f"{name}.csv"
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

