import sqlite3
import time
import random
import string
from .base_workload import BaseWorkload

class DatabaseWorkload(BaseWorkload):
    """Simulates OLTP-style database load (INSERT/SELECT mix)."""

    def run(self) -> dict:
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, data TEXT, value REAL)")
        
        latencies = []
        ops = 0
        deadline = time.time() + self.duration_sec

        while time.time() < deadline:
            t0 = time.perf_counter()
            if ops % 3 == 0:  # 1-in-3 are reads
                conn.execute("SELECT * FROM records ORDER BY RANDOM() LIMIT 10").fetchall()
            else:
                data = ''.join(random.choices(string.ascii_letters, k=32))
                conn.execute("INSERT INTO records (data, value) VALUES (?, ?)",
                             (data, random.uniform(0, 1000)))
            latencies.append((time.perf_counter() - t0) * 1000)  # ms
            ops += 1

        conn.close()
        latencies.sort()
        n = len(latencies)
        return {
            "workload": "database",
            "total_ops": ops,
            "ops_per_sec": round(ops / self.duration_sec, 1),
            "latency_p50_ms": round(latencies[int(n * 0.50)], 3),
            "latency_p95_ms": round(latencies[int(n * 0.95)], 3),
            "latency_p99_ms": round(latencies[int(n * 0.99)], 3),
        }