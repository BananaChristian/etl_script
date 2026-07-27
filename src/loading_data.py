import os
from dotenv import load_dotenv
import pandas as pd
from connect import get_engine

load_dotenv()

data_dir = os.getenv("data_dir")
engine = get_engine()

files_to_tables = {
        "Subscribers.csv": "subscriber",
        "AirtimeSales.csv": "airtimesales",
        "Calls.csv": "calls",
        "SMS.csv": "sms",
        "FibreSubscriptions.csv": "fibresubscriptions",
        "InternetBundleSales.csv": "internetbundlesales",
}

for file_name, table_name in files files_to_tables.items():
    file_path =  os.path.join(data_dir,filename)
    df = pd.read_csv(file_path)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table_name}")
