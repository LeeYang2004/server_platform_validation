from workloads.db_sim import DatabaseWorkload

def test_db_workload_runs():
    wl = DatabaseWorkload(duration_sec=1)
    result = wl.timed_run()

    assert "ops_per_sec" in result
    assert result["ops_per_sec"] > 0