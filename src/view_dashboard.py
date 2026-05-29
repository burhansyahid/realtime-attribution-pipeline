import os
import oracledb
from dotenv import load_dotenv

# Load Oracle credentials
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_DIR = os.getenv("WALLET_DIR")

def view_gold_layer():
    print("📊 Fetching Campaign Performance Dashboard...\n")
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN,
            config_dir=WALLET_DIR,
            wallet_location=WALLET_DIR,
            wallet_password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Query the Gold table we just built with dbt
        cursor.execute("""
            SELECT campaign_name, total_clicks, total_spend, total_conversions, total_revenue, roas 
            FROM gold_campaign_performance 
            ORDER BY total_revenue DESC
        """)
        
        # Print a nice table header
        print(f"{'CAMPAIGN NAME':<25} | {'CLICKS':<8} | {'SPEND':<10} | {'CONV.':<7} | {'REVENUE':<10} | {'ROAS':<5}")
        print("-" * 80)
        
        # Print the rows
        for row in cursor:
            spend = float(row[2]) if row[2] else 0.0
            revenue = float(row[4]) if row[4] else 0.0
            roas = float(row[5]) if row[5] else 0.0
            print(f"{row[0]:<25} | {row[1]:<8} | ${spend:<9.2f} | {row[3]:<7} | ${revenue:<9.2f} | {roas:<5.2f}")
            
    except Exception as e:
        print(f"❌ Error fetching dashboard: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    view_gold_layer()
