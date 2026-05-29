import os
import oracledb
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_DIR = os.getenv("WALLET_DIR")

def initialize_database():
    print("🔌 Connecting to Oracle Autonomous Database via mTLS...")
    try:
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            config_dir=WALLET_DIR,
            wallet_location=WALLET_DIR,
            wallet_password=DB_PASSWORD # Sometimes required depending on wallet type
        )
        cursor = connection.cursor()
        print("✅ Connection Successful!")

        tables = {
            "BRONZE_AD_CLICKS": """
                CREATE TABLE bronze_ad_clicks (
                    ingestion_id VARCHAR2(50) DEFAULT sys_guid() PRIMARY KEY,
                    raw_payload CLOB,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "BRONZE_CONVERSIONS": """
                CREATE TABLE bronze_conversions (
                    ingestion_id VARCHAR2(50) DEFAULT sys_guid() PRIMARY KEY,
                    raw_payload CLOB,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }

        for table_name, ddl in tables.items():
            print(f"🏗️ Building table: {table_name}...")
            try:
                # Drop table if it already exists for a clean slate
                cursor.execute(f"DROP TABLE {table_name}")
            except oracledb.DatabaseError as e:
                pass # Table didn't exist yet, which is fine
                
            cursor.execute(ddl)
            print(f"✅ {table_name} created successfully.")

        connection.commit()
        cursor.close()
        connection.close()
        print("🚀 Database Bronze Layer initialization complete.")

    except Exception as e:
        print(f"❌ Failed to connect or execute: {e}")

if __name__ == "__main__":
    initialize_database()
