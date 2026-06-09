import psutil
import threading
import time
from dataclasses import dataclass, field
from typing import List

# Represents a single metrics snapshot collected at a point in time
@dataclass
class Sample:
    timestamp: float # Unix timestamp when the sample was captured
    cpu_percent: float # CPU utilization percentage at sampling time
    mem_used_gb: float # Memory currently used by the system
    cpu_freq_mhz: float # Current CPU frequency in MHz

class MetricsCollector:
    """
    Samples system metrics in a background thread during workload execution.
    """

    # Configure sampling interval
    def __init__(self, interval_sec: float = 0.5):
        self.interval = interval_sec # Number of seconds between metric samples
        self.samples: List[Sample] = [] # Store all collected metric snapshots
        self._stop_event = threading.Event() # Thread-safe flag used to stop collection

     # Start collecting metrics in a separate thread
    def start(self):
        self._thread = threading.Thread(target=self._collect, daemon=True) # Create daemon thread
        self._thread.start()  # Start background collection process

    # Stop metric collection safely
    def stop(self):
        self._stop_event.set() # Signal collector loop to stop
        self._thread.join() # Wait until background thread finishes

    # Internal worker function executed by the thread
    def _collect(self):

         # Continue collecting until stop signal received
        while not self._stop_event.is_set():

            # Retrieve current CPU frequency information
            freq = psutil.cpu_freq()

             # Create and store a metrics snapshot
            self.samples.append(Sample(
                timestamp=time.time(),
                cpu_percent=psutil.cpu_percent(interval=None),
                mem_used_gb=psutil.virtual_memory().used / 1e9,
                cpu_freq_mhz=freq.current if freq else 0.0,
            ))

            # Wait until next sampling cycle
            time.sleep(self.interval)

    def summary(self) -> dict:
        """
        Generate summarized statistics from all collected samples
        """
        # Return empty result if nothing was collected
        if not self.samples:
            return {}
        
        # Extract CPU values from every sample
        cpu = [s.cpu_percent for s in self.samples]

        # Extract memory values from every sample
        mem = [s.mem_used_gb for s in self.samples]

        # Return aggregated metrics
        return {
            "cpu_avg_pct": round(sum(cpu) / len(cpu), 1),
            "cpu_max_pct": round(max(cpu), 1),
            "mem_avg_gb":  round(sum(mem) / len(mem), 2),
            "mem_peak_gb": round(max(mem), 2),
            "samples_collected": len(self.samples),
        }