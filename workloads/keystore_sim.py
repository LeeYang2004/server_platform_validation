# workloads/keystore_sim.py
import time
import random
from .base_workload import BaseWorkload

class KeystoreWorkload(BaseWorkload):
    """Simulates Memcached/Redis-style key-value access patterns."""

    def run(self) -> dict:
        store = {}
        hits = misses = writes = 0
        latencies = []
        deadline = time.time() + self.duration_sec

        # Pre-populate
        for i in range(1000):
            store[f"key:{i}"] = f"value:{random.randint(0, 99999)}"

        while time.time() < deadline:
            t0 = time.perf_counter()
            op = random.random()
            key = f"key:{random.randint(0, 1499)}"  # 25% miss rate intentional

            if op < 0.7:   # 70% GET
                val = store.get(key)
                if val: hits += 1
                else: misses += 1
            else:           # 30% SET
                store[key] = f"value:{random.randint(0, 99999)}"
                writes += 1

            latencies.append((time.perf_counter() - t0) * 1000)

        latencies.sort()
        n = len(latencies)
        return {
            "workload": "keystore",
            "cache_hit_rate": round(hits / (hits + misses) * 100, 1),
            "total_ops": hits + misses + writes,
            "latency_p50_ms": round(latencies[int(n * 0.50)], 4),
            "latency_p99_ms": round(latencies[int(n * 0.99)], 4),
        }