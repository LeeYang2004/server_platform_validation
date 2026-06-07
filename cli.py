# cli.py
import click
import json
from workloads.db_sim import DatabaseWorkload
from workloads.keystore_sim import KeystoreWorkload
from monitor.collector import MetricsCollector
from analysis.regression import check_regressions
from reporter.html_report import generate_report

WORKLOADS = {
    "db":       DatabaseWorkload,
    "keystore": KeystoreWorkload,
}

@click.command()
@click.option("--workload", type=click.Choice(["db", "keystore", "all"]), default="all")
@click.option("--duration", default=30, help="Seconds per workload")
@click.option("--output", default="reports/report.html")
def run(workload, duration, output):
    """Run ServerBench validation suite."""
    targets = list(WORKLOADS.items()) if workload == "all" else [(workload, WORKLOADS[workload])]
    
    all_results = []
    for name, WorkloadClass in targets:
        click.echo(f"\n▶ Running {name} workload ({duration}s)...")
        
        collector = MetricsCollector()
        collector.start()
        
        wl = WorkloadClass(duration_sec=duration)
        wl_metrics = wl.timed_run()
        
        collector.stop()
        sys_metrics = collector.summary()
        
        combined = {**wl_metrics, **sys_metrics}
        regressions = check_regressions(combined)
        
        status = "❌ FAIL" if regressions else "✅ PASS"
        click.echo(f"  {status} | ops/sec: {combined.get('ops_per_sec', 'N/A')} | CPU max: {combined.get('cpu_max_pct')}%")
        
        all_results.append({
            "name": name,
            "metrics": combined,
            "regressions": regressions,
            "status": "FAIL" if regressions else "PASS"
        })

    generate_report(all_results, output)
    click.echo(f"\n📊 Report saved to {output}")

if __name__ == "__main__":
    run()