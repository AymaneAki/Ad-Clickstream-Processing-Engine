import os
import json
import uuid
import random
from datetime import datetime, timedelta

NUM_RECORDS = 500_000
VIRAL_CAMPAIGNS = ["camp_001", "camp_002", "camp_003"]
NORMAL_CAMPAIGNS = [f"camp_{i:03d}" for i in range(4, 1001)] 

EVENTS = ["impression", "click", "purchase"]
EVENT_WEIGHTS = [0.80, 0.15, 0.05]
START_DATE = datetime.now() - timedelta(days=30)

def generate_timestamp():
    random_seconds = random.randint(0, 30 * 24 * 60 * 60)
    return (START_DATE + timedelta(seconds=random_seconds)).isoformat()

def generate_record():
    r = random.uniform(0.00, 1.00)
    
    # Skew trap: 95% probability to select from a 3-item list
    if r <= 0.95:
        camp = random.choice(VIRAL_CAMPAIGNS)
    else: 
        camp = random.choice(NORMAL_CAMPAIGNS)

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": generate_timestamp(),
        "user_id": random.randint(1, 1_000_000),
        "event_type": random.choices(EVENTS, weights=EVENT_WEIGHTS, k=1)[0],
        "campaign_id": camp 
    }

def build_local_lake():
    os.makedirs("data/raw", exist_ok=True)
    
    output_file = "data/raw/clickstream_log_01.json"
    
    print(f"Generating {NUM_RECORDS} skewed records...")
    with open(output_file, 'w') as f:
        for _ in range(NUM_RECORDS):
            record = generate_record()
            f.write(json.dumps(record) + '\n')
            
    print(f"Data generation complete. Payload written to {output_file}")

if __name__ == "__main__":
    build_local_lake()
