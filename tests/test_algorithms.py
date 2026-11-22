"""
Minimal sanity tests -- run with:  python -m pytest tests/
(or just `python tests/test_algorithms.py` which runs a plain assert-based check)

These don't require pytest to be installed; they double as a quick
self-check script for the MCA project demo / viva.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scheduler.process import Process
from scheduler.algorithms import fcfs, sjf, srtf, priority_np, priority_p, round_robin, mlfq
from scheduler.metrics import compute_metrics


def sample_processes():
    return [
        Process("P1", arrival=0, burst=6, priority=2),
        Process("P2", arrival=1, burst=4, priority=1),
        Process("P3", arrival=2, burst=9, priority=3),
        Process("P4", arrival=3, burst=5, priority=2),
    ]


def check_all_completed(procs, n_expected):
    assert len(procs) == n_expected, "process count mismatch"
    for p in procs:
        assert p.remaining == 0, f"{p.pid} never finished"
        assert p.completion > 0, f"{p.pid} has no completion time"
        assert p.turnaround == p.completion - p.arrival
        assert p.waiting == p.turnaround - p.burst


def test_fcfs():
    timeline, procs = fcfs(sample_processes())
    check_all_completed(procs, 4)


def test_sjf():
    timeline, procs = sjf(sample_processes())
    check_all_completed(procs, 4)


def test_srtf():
    timeline, procs = srtf(sample_processes())
    check_all_completed(procs, 4)


def test_priority_np():
    timeline, procs = priority_np(sample_processes())
    check_all_completed(procs, 4)


def test_priority_p():
    timeline, procs = priority_p(sample_processes())
    check_all_completed(procs, 4)


def test_round_robin():
    timeline, procs = round_robin(sample_processes(), quantum=3)
    check_all_completed(procs, 4)


def test_mlfq():
    timeline, procs = mlfq(sample_processes(), quantums=(2, 4, 8))
    check_all_completed(procs, 4)


def test_metrics_sane():
    timeline, procs = fcfs(sample_processes())
    m = compute_metrics(procs, timeline)
    assert m["Average Waiting Time"] >= 0
    assert m["CPU Utilization (%)"] <= 100


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        t()
        passed += 1
        print(f"  [OK] {t.__name__}")
    print(f"\n{passed}/{len(tests)} tests passed.")
