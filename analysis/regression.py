# analysis/regression.py
import yaml
from pathlib import Path

DEFAULT_THRESHOLDS = {
    "cpu_max_pct": 95.0,
    "latency_p99_ms": 50.0,
    "cache_hit_rate_min": 60.0,
}

def load_thresholds(config_path: str = "config.yaml") -> dict:
    if Path(config_path).exists():
        with open(config_path) as f:
            return yaml.safe_load(f).get("thresholds", DEFAULT_THRESHOLDS)
    return DEFAULT_THRESHOLDS

def check_regressions(metrics: dict, thresholds: dict = None) -> list[dict]:
    """
    Returns a list of regression findings.
    Each finding: {field, value, threshold, severity}
    """
    thresholds = thresholds or load_thresholds()
    findings = []

    checks = [
        ("cpu_max_pct",      metrics.get("cpu_max_pct", 0),         thresholds["cpu_max_pct"],         "gt",  "HIGH"),
        ("latency_p99_ms",   metrics.get("latency_p99_ms", 0),      thresholds["latency_p99_ms"],      "gt",  "MEDIUM"),
        ("cache_hit_rate",   metrics.get("cache_hit_rate", 100),     thresholds["cache_hit_rate_min"],  "lt",  "MEDIUM"),
    ]

    for field, value, threshold, direction, severity in checks:
        triggered = (direction == "gt" and value > threshold) or \
                    (direction == "lt" and value < threshold)
        if triggered:
            findings.append({
                "field": field, "value": value,
                "threshold": threshold, "severity": severity
            })

    return findings