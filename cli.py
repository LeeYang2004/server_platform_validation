import click
from workloads.db_sim import DatabaseWorkload
from workloads.keystore_sim import KeystoreWorkload
from monitor.collector import MetricsCollector
from analysis.regression import check_regressions
from reporter.html_report import generate_report

# Map CLI workload names to workload classes
WORKLOADS = {   
    "db": DatabaseWorkload, # Database benchmark
    "keystore": KeystoreWorkload, # Key-value store benchmark
}

# Register Click command
@click.command()

# Workload selection option
@click.option("--workload", type=click.Choice(["db", "keystore", "all"]), default="all")

# Duration option
@click.option("--duration", default=30, help="Seconds per workload")

# Output report location
@click.option("--output", default="reports/report.html")

def run(workload, duration, output):
    """
    Run ServerBench validation suite.
    """
    # STEP 1: Run every workload if all is selected, otherwise just the specified one
    targets = list(WORKLOADS.items()) if workload == "all" else [(workload, WORKLOADS[workload])]
    
    # Store results from all workloads
    all_results = []

    # Execute each workload
    for name, WorkloadClass in targets:

        # Display progress
        click.echo(f"\nRunning {name} workload ({duration}s)...")
        
        # STEP 2: Create metrics collector
        collector = MetricsCollector()

        # Start background monitoring thread
        collector.start()
        
        # Create workload instance
        wl = WorkloadClass(duration_sec=duration)

        # STEP 3: Run workload and calculate workload metrics
        wl_metrics = wl.timed_run()
        
        # STEP 4:Stop system monitoring
        collector.stop()

        # Generate CPU/RAM summary
        sys_metrics = collector.summary()
        
        # STEP 5: Merge workload metrics and system metrics
        combined = {**wl_metrics, **sys_metrics}

        # STEP 6: Detect performance regressions
        regressions = check_regressions(combined)
        
        # Determine final status
        # If PASS = No performance thresholds exceeded
        status = "FAIL" if regressions else "PASS"

        # STEP 7: Print quick summary
        click.echo(f"  {status} | ops/sec: {combined.get('ops_per_sec', 'N/A')} | CPU max: {combined.get('cpu_max_pct')}%")
        
        # Save workload results
        all_results.append({
            "name": name,
            "metrics": combined,
            "regressions": regressions,
            "status": "FAIL" if regressions else "PASS"
        })

    # Generate HTML report
    generate_report(all_results, output)

    # Display report location
    click.echo(f"\nReport saved to {output}")

if __name__ == "__main__":
    run()