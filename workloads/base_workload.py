from abc import ABC, abstractmethod
import time

class BaseWorkload(ABC):
    def __init__(self, duration_sec: int = 30):
        self.duration_sec = duration_sec
        self.results = {}

    @abstractmethod
    def run(self) -> dict:
        """Execute the workload and return metrics."""
        pass

    def timed_run(self) -> dict:
        start = time.time()
        self.results = self.run()
        self.results["duration_sec"] = round(time.time() - start, 2)
        return self.results