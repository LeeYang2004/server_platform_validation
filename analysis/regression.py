import yaml
from pathlib import Path

# Default performance thresholds used when no config file is provided
DEFAULT_THRESHOLDS = {
    "cpu_max_pct": 95.0, # Maximum allowed CPU utilization percentage
    "latency_p99_ms": 50.0, # Maximum allowed 99th percentile latency in milliseconds
    "cache_hit_rate_min": 60.0, # Minimum acceptable cache hit rate percentage
}

def load_thresholds(config_path: str = "config.yaml") -> dict:
    """
    Load threshold values from configuration file
    - Falls back to DEFAULT_THRESHOLDS if file does not exist
    """
    # Check whether the config file exists
    if Path(config_path).exists():
        with open(config_path) as f:
            
            # Parse YAML safely into Python dictionary
            # Retrieve "thresholds" section
            return yaml.safe_load(f).get(
                "thresholds",
                DEFAULT_THRESHOLDS, # Use DEFAULT_THRESHOLDS if section is missing
            )
    return DEFAULT_THRESHOLDS

def check_regressions(metrics: dict, thresholds: dict = None) -> list[dict]:
    """
    Compare collected benchmark metrics against thresholds
    - Returns a list of regression findings.
    - Each finding: {field, value, threshold, severity}
    """
    # Use provided thresholds if available, otherwise load thresholds from config file/defaults
    thresholds = thresholds or load_thresholds()

    # Store all regression findings in a list
    findings = []

    # Define all validation rules
    checks = [
        ("cpu_max_pct",      metrics.get("cpu_max_pct", 0),         thresholds["cpu_max_pct"],         "gt",  "HIGH"),
        ("latency_p99_ms",   metrics.get("latency_p99_ms", 0),      thresholds["latency_p99_ms"],      "gt",  "MEDIUM"),
        ("cache_hit_rate",   metrics.get("cache_hit_rate", 100),     thresholds["cache_hit_rate_min"],  "lt",  "MEDIUM"),
    ]

     # Iterate through all validation rules
    for field, value, threshold, direction, severity in checks:
        
        # Determine whether regression condition is met
        triggered = (
            direction == "gt" and value > threshold
        ) or (
            direction == "lt" and value < threshold
        )

        if triggered:
            # Record regression details
            findings.append({
                "field": field, 
                "value": value,
                "threshold": threshold, 
                "severity": severity
            })

    return findings