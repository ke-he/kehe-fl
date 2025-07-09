import csv
import json
import os
import time

from kehe_fl_s3.utils.common.adafruit_scd_30 import AdafruitSCD30
from kehe_fl_s3.utils.common.data_storage import DataStorage

class DataCollectionService:
    def __init__(self, fields, path: str, interval: int):
        self.sensor = AdafruitSCD30()
        self.storage = DataStorage(fields=fields, directory=path)
        self.path = path
        self.interval = interval
        self._running = False

    def start(self):
        print("[DataCollectionService] Starting data collection...")
        self._running = True
        while self._running:
            data = self.sensor.read()
            if data:
                co2, temperature, humidity = data
                self.storage.save({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "co2": co2,
                    "temperature": temperature,
                    "humidity": humidity
                })
            time.sleep(self.interval)

    def stop(self):
        print("[DataCollectionService] Stopping data collection...")
        self._running = False

    def check_data_count(self):
        print("[DataCollectionService] Checking data count...")
        files = os.listdir(self.path)
        count = 0
        for file in files:
            if file.endswith(".csv"):
                with open(os.path.join(self.path, file), 'r') as f:
                    reader = csv.reader(f)
                    count += sum(1 for _ in reader) - 1
        return count

    def get_training_data_json(self):
        data = []
        files = os.listdir(self.path)
        for file in files:
            if file.endswith(".csv"):
                with open(os.path.join(self.path, file), 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            data.append({
                                "co2": float(row["co2"]),
                                "temperature": float(row["temperature"])
                            })
                        except Exception:
                            continue
        return json.dumps(data)
