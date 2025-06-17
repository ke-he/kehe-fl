import csv
import os
from datetime import datetime

class DataStorage:
    def __init__(self, fields, directory="logs"):
        self.fields = fields
        self.directory = os.path.expanduser(directory)
        os.makedirs(self.directory, exist_ok=True)

    def _get_daily_filepath(self):
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return os.path.join(self.directory, f"{date_str}.csv")

    def save(self, data: dict):
        if not all(field in data for field in self.fields):
            raise ValueError("Missing fields in data: expected " + ", ".join(self.fields))

        filepath = self._get_daily_filepath()
        write_header = not os.path.isfile(filepath)

        with open(filepath, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.fields)
            if write_header:
                writer.writeheader()
            writer.writerow(data)
