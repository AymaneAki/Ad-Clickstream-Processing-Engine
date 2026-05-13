import os
import json
import uuid
import random
from datetime import datetime, timedelta

NUM_RECORDS = 10_000_000

VIRAL_CAMPAIGNS   = ["camp_001", "camp_002", "camp_003"]
NORMAL_CAMPAIGNS  = [f"camp_{i:03d}" for i in range(4, 1001)]

EVENTS        = ["impression", "click",  "purchase"]
EVENT_WEIGHTS = [0.80,         0.15,     0.05]

REVENUE = {
    "impression": (0.001, 0.01),   # CPM 
    "click":      (0.10,  1.50),   # CPC
    "purchase":   (5.00,  80.00),  # CPA
}

DEVICES        = ["mobile", "desktop", "tablet"]
DEVICE_WEIGHTS = [0.65,     0.30,      0.05]     # mobile heavy

START_DATE = datetime.now() - timedelta(days=30)


def generate_timestamp():
    random_seconds = random.randint(0, 30 * 24 * 60 * 60)
    return (START_DATE + timedelta(seconds=random_seconds)).isoformat()


def generate_record():
    # skew: 95% of events go to only 3 campaigns out of 1000
    campaign_id = (
        random.choice(VIRAL_CAMPAIGNS)
        if random.random() <= 0.95
        else random.choice(NORMAL_CAMPAIGNS)
    )

    event_type  = random.choices(EVENTS, weights=EVENT_WEIGHTS, k=1)[0]
    low, high   = REVENUE[event_type]
    revenue_usd = round(random.uniform(low, high), 4)

    return {
        "event_id":    str(uuid.uuid4()),
        "timestamp":   generate_timestamp(),
        "user_id":     str(uuid.uuid4()),       
        "event_type":  event_type,
        "campaign_id": campaign_id,
        "device_type": random.choices(DEVICES, weights=DEVICE_WEIGHTS, k=1)[0],
        "revenue_usd": revenue_usd,
    }


def build_local_lake():
    os.makedirs("data/raw", exist_ok=True)
    output_file = "data/raw/clickstream_log_01.json"

    print(f"Generating {NUM_RECORDS} skewed records...")
    with open(output_file, "w") as f:
        for _ in range(NUM_RECORDS):
            f.write(json.dumps(generate_record()) + "\n")

    size_mb = os.path.getsize(output_file) / 1e6
    print(f"Done. Written to {output_file} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    build_local_lake()