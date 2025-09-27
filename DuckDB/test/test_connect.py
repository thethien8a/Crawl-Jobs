import duckdb
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

def show_schemas(con):
    # 1) Liệt kê schemas (dùng information_schema thay SHOW SCHEMAS)
    print("Schemas:")
    print(con.execute("SELECT schema_name FROM information_schema.schemata;").fetchall())

def show_tables(con, schema_name):
    # 2) Liệt kê tables trong schema os.getenv("DUCKDB_STAGING_SCHEMA")
    print(f"Tables in {os.getenv('DUCKDB_STAGING_SCHEMA')}:")
    print(con.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{schema_name}';
    """).fetchall())

def remove_schema(con, schema_name):
    con.execute(f"DROP SCHEMA IF EXISTS {schema_name}")

def remove_table(con, schema_name, table_name):
    con.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name}")

def truncate_table(con, schema_name, table_name):
    con.execute(f"TRUNCATE TABLE {schema_name}.{table_name}")

def spacing():
    print()
    print("--------------------------------")
    print()
    
def main():
    con = duckdb.connect(os.getenv("DUCKDB_PATH"))
    show_schemas(con)
    con.close()
    
    
if __name__ == "__main__":
    main()