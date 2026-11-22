"""
scheduler.metrics
------------------
Turns a (timeline, processes) result from any algorithm into human
readable tables and summary KPIs.
"""

import pandas as pd


def process_table(procs):
    """Per-process breakdown: arrival/burst/priority + the 4 classic metrics."""
    rows = []
    for p in sorted(procs, key=lambda x: x.pid):
        rows.append(
            {
                "PID": p.pid,
                "Arrival": p.arrival,
                "Burst": p.burst,
                "Priority": p.priority,
                "Completion": p.completion,
                "Turnaround": p.turnaround,
                "Waiting": p.waiting,
                "Response": p.response,
            }
        )
    return pd.DataFrame(rows)


def compute_metrics(procs, timeline):
    """Summary KPIs for one algorithm run."""
    n = len(procs)
    if n == 0 or not timeline:
        return {
            "Average Waiting Time": 0,
            "Average Turnaround Time": 0,
            "Average Response Time": 0,
            "Throughput (proc/unit time)": 0,
            "CPU Utilization (%)": 0,
            "Context Switches": 0,
            "Makespan": 0,
        }

    total_burst = sum(p.burst for p in procs)
    start_time = min(seg["start"] for seg in timeline)
    end_time = max(seg["end"] for seg in timeline)
    makespan = max(end_time - start_time, 1)

    avg_wt = sum(p.waiting for p in procs) / n
    avg_tat = sum(p.turnaround for p in procs) / n
    avg_rt = sum(p.response for p in procs) / n
    throughput = n / makespan
    utilization = min(total_burst / makespan * 100, 100.0)

    # context switch = every time the running pid changes in the timeline
    switches = 0
    for a, b in zip(timeline, timeline[1:]):
        if a["pid"] != b["pid"]:
            switches += 1

    return {
        "Average Waiting Time": round(avg_wt, 2),
        "Average Turnaround Time": round(avg_tat, 2),
        "Average Response Time": round(avg_rt, 2),
        "Throughput (proc/unit time)": round(throughput, 4),
        "CPU Utilization (%)": round(utilization, 2),
        "Context Switches": switches,
        "Makespan": makespan,
    }
