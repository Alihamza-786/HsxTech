import os
from dotenv import load_dotenv
load_dotenv(override=True)

def db_url():
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"