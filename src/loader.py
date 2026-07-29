import os
from dotenv import load_dotenv
import pandas as pd
from connector import get_engine
import logger as lg

load_dotenv()

files_to_tables = {
        "Subscribers.csv": "subscriber",
        "AirtimeSales.csv": "airtimesales",
        "Calls.csv": "calls",
        "SMS.csv": "sms",
        "FibreSubscriptions.csv": "fibresubscriptions",
        "InternetBundleSales.csv": "internetbundlesales",
        "MSISDN.csv": "msisdn",
}


def load(data_dir=None):
    data_dir = data_dir or os.getenv("data_dir")
    engine = get_engine()
 
    for file_name, table_name in FILES_TO_TABLES.items():
        file_path = os.path.join(data_dir, file_name)
 
        if not os.path.exists(file_path):
            lg.log_warn(f"Skipped '{table_name}': file not found at {file_path}")
            continue
 
        df = pd.read_csv(file_path)
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        lg.log_ok(f"Loaded {len(df)} rows into '{table_name}'")
 
 
def main():
    load()

if __name__ == "__main__":
    main()
