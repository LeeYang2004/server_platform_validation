import time
from abc import ABC, abstractmethod

class BaseWorkload(ABC):
    """
    Base class for every workload type
    """

    # Initialize workload configuration
    def __init__(self, duration_sec: int = 30):
        self.duration_sec = duration_sec # How long the workload should run
        self.results = {} # Store workload results

    @abstractmethod
    def run(self) -> dict:
        """
        Execute the workload and return metrics.
        """
        pass

    def timed_run(self) -> dict:
        """
        Measures execution time automatically
        """

        # Capture start time
        start = time.time()
        self.results = self.run() # Execute workload-specific implementation
        self.results["duration_sec"] = round(time.time() - start, 2) # Record actual execution duration

        # Return complete results
        return self.results