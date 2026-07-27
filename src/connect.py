from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

#db details
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
db_name =os.getenv("db_name")


def get_engine(): 
    connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    return engine
