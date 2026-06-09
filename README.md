# ServerBench
Automated Server Benchmarking & Regression Testing Framework

# Key Features
* Simulates multiple server workloads (OLTP-style database + key-value store)
* Collects real-time system metrics (CPU, memory, frequency)
* Computes performance metrics (latency percentiles, throughput)
* Detects performance regressions using configurable thresholds
* Generates HTML reports for CI visibility
* Fully CI/CD compatible via GitHub Actions

   # Architecture
   1. Workload Layer: Simulate `DatabaseWorkload` and `KeystoreWorkload`
   2. Monitoring Layer: Capture `CPU utilization (%)`, `Memory usage (GB)`, `CPU frequency (MHz)`
   3. Regression Analysis Layer: Compare runtime metrics against predefined thresholds
   4. Reporting Layer: Generate an HTML report

# CLI Usage
Run all workloads
```bash
python cli.py --workload all --duration 30
```
Run db/keystore workloads
```bash
python cli.py --workload db/keystore --duration 30
```
Output report location: `reports/report.html`

# Example Output
```bash
Running db workload (30s)...
PASS | ops/sec: 2105.1 | CPU max: 43.7%

Running keystore workload (30s)...
PASS | ops/sec: N/A | CPU max: 26.7%

Report saved to reports/report.html
```

# CI Integration (GitHub Actions)
1. Install dependencies
2. Run unit tests (pytest)
3. Execute benchmark workloads
4. Collect system metrics
5. Run regression checks
6. Upload HTML report as artifact