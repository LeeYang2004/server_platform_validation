import time
import random
from .base_workload import BaseWorkload

class KeystoreWorkload(BaseWorkload):
    """
    Simulates Memcached/Redis-style key-value access patterns.
    """
    def run(self) -> dict:

        # In-memory key-value store
        store = {}

        # Metrics counters
        hits = misses = writes = 0

        # Track operation latency
        latencies = []

        # Workload stop time
        deadline = time.time() + self.duration_sec

        # Preload cache
        for i in range(1000):
            store[f"key:{i}"] = f"value:{random.randint(0, 99999)}"

        while time.time() < deadline:

            # Start latency measurement
            t0 = time.perf_counter()

            # Randomly select operation
            op = random.random()

            # Generate key
            key = f"key:{random.randint(0, 1499)}"  # 25% miss rate intentional

            # GET request
            if op < 0.7: # 70% GET
                val = store.get(key)
                if val: hits += 1
                else: misses += 1
            
            # SET request
            else: # 30% SET
                store[key] = f"value:{random.randint(0, 99999)}"
                writes += 1

            # Record latency
            latencies.append((time.perf_counter() - t0) * 1000)

        # Prepare percentile calculation
        latencies.sort()
        n = len(latencies)

        # Return benchmark results
        return {
            "workload": "keystore",
            "cache_hit_rate": round(hits / (hits + misses) * 100, 1),
            "total_ops": hits + misses + writes,
            "latency_p50_ms": round(latencies[int(n * 0.50)], 4),
            "latency_p99_ms": round(latencies[int(n * 0.99)], 4),
        }