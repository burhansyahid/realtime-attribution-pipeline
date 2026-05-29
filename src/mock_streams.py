import json
import time
import random
import uuid
from kafka import KafkaProducer
from faker import Faker

fake = Faker()

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

AD_NETWORKS = ["Google Search", "Meta Ads", "TikTok Ads", "LinkedIn B2B"]
CAMPAIGNS = ["Summer_Sale", "Retargeting_V1", "Lookalike_Audience", "Brand_Awareness"]

# Memory pool to ensure conversions match actual ad clicks
active_users = []

print("🚀 Starting Synthetic Data Streams. Press Ctrl+C to stop.")

try:
    while True:
        # 1. Generate an Ad Click
        user_cookie = f"usr_{uuid.uuid4().hex[:8]}"
        active_users.append(user_cookie)

        # Keep the memory pool manageable to prevent memory leaks
        if len(active_users) > 500:
            active_users.pop(0)

        click_event = {
            "click_id": f"clk_{uuid.uuid4().hex[:8]}",
            "user_cookie_id": user_cookie,
            "ad_network": random.choice(AD_NETWORKS),
            "campaign_name": random.choice(CAMPAIGNS),
            "cost_per_click": round(random.uniform(0.50, 4.50), 2),
            "timestamp": int(time.time())
        }

        # Send to the 'ad_clicks' Kafka topic
        producer.send('ad_clicks', value=click_event)
        print(f"🖱️  [CLICK] {click_event['ad_network']} - User: {user_cookie} - Cost: ${click_event['cost_per_click']}")

        # 2. Simulate a Conversion (15% chance a recent user buys something)
        if random.random() < 0.15 and len(active_users) > 0:
            buyer_cookie = random.choice(active_users)
            conversion_event = {
                "order_id": f"ord_{uuid.uuid4().hex[:8]}",
                "user_cookie_id": buyer_cookie,
                "revenue_usd": round(random.uniform(20.0, 250.0), 2),
                "timestamp": int(time.time())
            }
            
            # Send to the 'conversions' Kafka topic
            producer.send('conversions', value=conversion_event)
            print(f"💰 [CONVERSION] Revenue: ${conversion_event['revenue_usd']} - User: {buyer_cookie}")

        # Sleep to simulate real-world, unpredictable web traffic
        time.sleep(random.uniform(0.2, 1.5))

except KeyboardInterrupt:
    print("\n🛑 Stopping streams. Flushing data to Kafka...")
    producer.flush()
    producer.close()
    print("Safely shut down.")
