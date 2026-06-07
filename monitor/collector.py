# monitor/collector.py
import psutil
import threading
import time
from dataclasses import dataclass, field
from typing import List

@dataclass
class Sample:
    timestamp: float
    cpu_percent: float
    mem_used_gb: float
    cpu_freq_mhz: float

class MetricsCollector:
    """Samples system metrics in a background thread during workload execution."""

    def __init__(self, interval_sec: float = 0.5):
        self.interval = interval_sec
        self.samples: List[Sample] = []
        self._stop_event = threading.Event()

    def start(self):
        self._thread = threading.Thread(target=self._collect, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

    def _collect(self):
        while not self._stop_event.is_set():
            freq = psutil.cpu_freq()
            self.samples.append(Sample(
                timestamp=time.time(),
                cpu_percent=psutil.cpu_percent(interval=None),
                mem_used_gb=psutil.virtual_memory().used / 1e9,
                cpu_freq_mhz=freq.current if freq else 0.0,
            ))
            time.sleep(self.interval)

    def summary(self) -> dict:
        if not self.samples:
            return {}
        cpu = [s.cpu_percent for s in self.samples]
        mem = [s.mem_used_gb for s in self.samples]
        return {
            "cpu_avg_pct": round(sum(cpu) / len(cpu), 1),
            "cpu_max_pct": round(max(cpu), 1),
            "mem_avg_gb":  round(sum(mem) / len(mem), 2),
            "mem_peak_gb": round(max(mem), 2),
            "samples_collected": len(self.samples),
        }