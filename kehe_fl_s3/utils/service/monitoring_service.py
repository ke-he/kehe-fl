import time
import threading
import psutil
import csv
import os
import json
from datetime import datetime

from kehe_fl_s3.utils.common.project_constants import ProjectConstants


class MonitoringService:
    def __init__(self, directory=ProjectConstants.MONITORING_DIRECTORY + "/s3", interval=ProjectConstants.MONITORING_INTERVAL):
        self.directory = directory
        self.interval = interval
        self._running = False
        self._thread = None
        self._cpu = []
        self._mem = []
        self._bytes_sent = []
        self._bytes_recv = []
        self._start_net = None
        self._start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(self.directory, exist_ok=True)

        self._base_filename = f"run_at_{self._start_time}"
        self.raw_path = os.path.join(self.directory, f"{self._base_filename}.csv")
        self.summary_path = os.path.join(self.directory, f"{self._base_filename}_summary.json")

    def start(self):
        self._running = True
        self._cpu = []
        self._mem = []
        self._bytes_sent = []
        self._bytes_recv = []
        net = psutil.net_io_counters()
        self._start_net = (net.bytes_sent, net.bytes_recv)
        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._thread.start()

        with open(self.raw_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'cpu_percent', 'mem_mb', 'bytes_sent', 'bytes_recv'])

    def _monitor(self):
        while self._running:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().used / (1024 * 1024) # Convert to MB
            net = psutil.net_io_counters()
            bytes_sent = net.bytes_sent
            bytes_recv = net.bytes_recv

            self._cpu.append(cpu)
            self._mem.append(mem)
            self._bytes_sent.append(bytes_sent)
            self._bytes_recv.append(bytes_recv)

            with open(self.raw_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, cpu, mem, bytes_sent, bytes_recv])
            time.sleep(self.interval)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

        net = psutil.net_io_counters()
        net_sent_total = net.bytes_sent - self._start_net[0] if self._start_net else 0
        net_recv_total = net.bytes_recv - self._start_net[1] if self._start_net else 0

        summary = {
            "cpu_avg": sum(self._cpu) / len(self._cpu) if self._cpu else 0,
            "cpu_max": max(self._cpu) if self._cpu else 0,
            "cpu_min": min(self._cpu) if self._cpu else 0,
            "mem_avg": sum(self._mem) / len(self._mem) if self._mem else 0,
            "mem_max": max(self._mem) if self._mem else 0,
            "mem_min": min(self._mem) if self._mem else 0,
            "net_sent_total": net_sent_total,
            "net_recv_total": net_recv_total,
            "duration_s": len(self._cpu) * self.interval
        }

        with open(self.summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"[MonitoringService] Monitoring stopped. Summary: {summary}")
        print(f"Raw data saved to {self.raw_path}")
        print(f"Summary saved to {self.summary_path}")
        return summary
