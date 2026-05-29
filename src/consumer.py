import os
import json
import oracledb
from dotenv import load_dotenv
from kafka import KafkaConsumer

# Load Oracle credentials
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")
WALLET_DIR = os.getenv("WALLET_DIR")

def get_db_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
        config_dir=WALLET_DIR,
        wallet_location=WALLET_DIR,
        wallet_password=DB_PASSWORD
    )

def start_consumer():
    print("🔌 Connecting to Oracle Database...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("✅ Database Connected.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    print("🎧 Starting Kafka Consumer. Listening for data...")
    # Initialize Kafka Consumer
    consumer = KafkaConsumer(
        'ad_clicks',
        'conversions',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',  # Start reading new messages
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    try:
        # This is an infinite loop that waits for new data to arrive
        for message in consumer:
            topic = message.topic
            
            # Convert the Python dictionary back to a JSON string for Oracle's CLOB column
            payload_string = json.dumps(message.value) 
            
            # Route the data to the correct Oracle table based on the Kafka topic
            if topic == 'ad_clicks':
                sql = "INSERT INTO bronze_ad_clicks (raw_payload) VALUES (:1)"
            elif topic == 'conversions':
                sql = "INSERT INTO bronze_conversions (raw_payload) VALUES (:1)"
                
            cursor.execute(sql, [payload_string])
            conn.commit()
            
            print(f"💾 [INSERT] Saved 1 record to BRONZE_{topic.upper()}.")

    except KeyboardInterrupt:
        print("\n🛑 Stopping Consumer...")
    finally:
        cursor.close()
        conn.close()
        consumer.close()
        print("Safely shut down.")

if __name__ == "__main__":
    start_consumer()
