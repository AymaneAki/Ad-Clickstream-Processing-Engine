from pathlib import Path
from datetime import datetime, timedelta
import random 
import uuid
import math
import json


class ClickStreamGenerator:

    def __init__(self, output_dir: str, nbr_campaigns: int=1000, skewed_campaigns: int=3, start_date: datetime=None):
        self.nbr_campaigns = nbr_campaigns
        self.skewed_campaigns = skewed_campaigns
        
        self.start_date = start_date or datetime.now()
        
        self.viral_campaigns = [f"camp_{i:03d}" for i in range(1, self.skewed_campaigns + 1)]
        self.NORMAL_CAMPAIGNS = [f"camp_{i:03d}" for i in range(self.skewed_campaigns + 1, self.nbr_campaigns + 1)]
        
        self.EVENTS = ["impression", "click", "purchase"]
        self.EVENT_WEIGHTS = [0.80, 0.15, 0.05]
        self.REVENUE = {
            "impression": (0.001, 0.01),   # CPM 
            "click":      (0.10,  1.50),   # CPC
            "purchase":   (5.00,  80.00),  # CPA
        }
        self.DEVICES = ["mobile", "desktop", "tablet"]
        self.DEVICE_WEIGHTS = [0.65, 0.30, 0.05] 

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_timestamp(self):
        random_seconds = random.randint(0, 30 * 24 * 60 * 60)
        return (self.start_date + timedelta(seconds=random_seconds)).isoformat()

    def _gen_single_record(self):
        campaign_id = (random.choice(self.viral_campaigns) if random.random() <= 0.95
                       else random.choice(self.NORMAL_CAMPAIGNS))

        event_type = random.choices(self.EVENTS, weights=self.EVENT_WEIGHTS, k=1)[0]
        low, high = self.REVENUE[event_type]
        revenue_usd = round(random.uniform(low, high), 4)

        return {
            "event_id":    str(uuid.uuid4()),
            "timestamp":   self._generate_timestamp(),
            "user_id":     str(uuid.uuid4()),       
            "event_type":  event_type,
            "campaign_id": campaign_id,
            "device_type": random.choices(self.DEVICES, weights=self.DEVICE_WEIGHTS, k=1)[0],
            "revenue_usd": revenue_usd,
        }

    def gen_batch(self, batch_size: int):
        return [self._gen_single_record() for _ in range(batch_size)] 
    

    def generate_chunked_data(self, total_records: int, batch_size: int = 100_000) -> None:
        """
        Writes synthetic data to disk in chunked JSONL files.
        Maintains fixed memory usage regardless of total_records.
        """
        num_files = math.ceil(total_records / batch_size)
        records_generated = 0
        
        for file_idx in range(num_files):
            # Format file names like: clickstream_part_0000.jsonl
            file_name = self.output_dir / f"clickstream_part_{file_idx:04d}.jsonl"
            
            # Handle the last batch which might be smaller than batch_size
            current_batch_size = min(batch_size, total_records - records_generated)
            
            # 1. Generate the batch in RAM (memory usage spikes here, but is capped)
            batch = self.gen_batch(current_batch_size)
            
            # 2. Flush to disk immediately
            with open(file_name, 'w', encoding='utf-8') as f:
                for record in batch:
                    f.write(json.dumps(record) + '\n')
            
            # 3. Batch is overwritten on the next loop, freeing RAM
            records_generated += current_batch_size
            
            # Interview tip: Always add lightweight logging for long-running scripts
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Wrote {current_batch_size} "
                  f"records to {file_name.name} | Total: {records_generated}/{total_records}")

if __name__ == "__main__":
    # Simulate a raw data lake layer (Bronze layer)
    generator = ClickStreamGenerator(output_dir="./data/raw")    
    generator.generate_chunked_data(total_records=5_000_000, batch_size=100_000)