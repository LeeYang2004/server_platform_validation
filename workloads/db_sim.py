import sqlite3
import time
import random
import string
from .base_workload import BaseWorkload

class DatabaseWorkload(BaseWorkload):
    """
    Simulates OLTP-style database load (INSERT/SELECT mix).
    """
    def run(self) -> dict:

        # Create temporary in-memory database
        conn = sqlite3.connect(":memory:")

        # Create test table
        conn.execute(
            """
            CREATE TABLE records (
                id INTEGER PRIMARY KEY, 
                data TEXT, 
                value REAL
            )
            """
        )
        
        # Store latency of every operation
        latencies = []

        # Count operations performed
        ops = 0

        # Calculate workload end time
        deadline = time.time() + self.duration_sec

        # Continue until duration expires
        while time.time() < deadline:

            # High precision timer
            t0 = time.perf_counter()

            if ops % 3 == 0:  # 1-in-3 are reads
                # Random row retrieval
                conn.execute(
                    """
                    SELECT *
                    FROM records
                    ORDER BY RANDOM()
                    LIMIT 10
                    """
                ).fetchall()
            else:
                # Generate random text payload
                data = ''.join(
                    random.choices(
                        string.ascii_letters,
                        k=32
                    )
                )
                # Insert new record
                conn.execute(
                    """
                    INSERT INTO records
                    (data, value)
                    VALUES (?, ?)
                    """,
                    (
                        data,
                        random.uniform(0, 1000)
                    )
                )
            
            # Measure operation latency in milliseconds
            latencies.append((time.perf_counter() - t0) * 1000)
            ops += 1

        # Close database
        conn.close()

        # Sort for percentile calculation
        latencies.sort()

         # Total samples
        n = len(latencies)

        # Return benchmark metrics
        return {
            "workload": "database",
            "total_ops": ops,
            "ops_per_sec": round(ops / self.duration_sec, 1),
            "latency_p50_ms": round(latencies[int(n * 0.50)], 3),
            "latency_p95_ms": round(latencies[int(n * 0.95)], 3),
            "latency_p99_ms": round(latencies[int(n * 0.99)], 3),
        }