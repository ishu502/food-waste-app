import pandas as pd
import sqlite3
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "food_waste.db"

# CSV files and table names mapping
csv_files = {
    "providers": DATA_DIR / "providers_data.csv",
    "receivers": DATA_DIR / "receivers_data.csv",
    "food_listings": DATA_DIR / "food_listings_data.csv",
    "claims": DATA_DIR / "claims_data.csv"
}

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")

# Drop tables if they already exist (for rebuild purposes)
for table in csv_files.keys():
    conn.execute(f"DROP TABLE IF EXISTS {table}")

# Function to create table dynamically based on CSV columns
def create_table_from_df(table_name, df):
    col_defs = []
    for col in df.columns:
        if col.endswith("_ID"):
            col_defs.append(f"{col} INTEGER")
        else:
            col_defs.append(f"{col} TEXT")
    schema = f"CREATE TABLE {table_name} ({', '.join(col_defs)})"
    conn.execute(schema)

# Read CSVs, create matching tables, and insert data
for table_name, file_path in csv_files.items():
    df = pd.read_csv(file_path)
    create_table_from_df(table_name, df)
    df.to_sql(table_name, conn, if_exists="append", index=False)

# Commit & close
conn.commit()
conn.close()

print(f"Database created successfully at: {DB_PATH}")
