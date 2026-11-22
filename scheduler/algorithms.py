"""
scheduler.algorithms
---------------------
Every CPU scheduling algorithm implemented for this project.

Each function has the SAME contract:

    timeline, processes = algorithm(list_of_Process, **params)

- `timeline` is a list of dicts: {"pid": str, "start": int, "end": int, ["level": int]}
  describing exactly what ran on the CPU and when (a Gantt chart source).
- `processes` is the (deep-copied, now-completed) list of Process objects
  with completion / turnaround / waiting / response filled in.

Deep-copying the input list means the caller's original process set is
never mutated, so the same processes can be fed into every algorithm for
a fair side-by-side comparison.
"""

import copy
from collections import deque


def _reset(processes):
    return copy.deepcopy(processes)


# --------------------------------------------------------------------------
# 1. First Come First Served
# --------------------------------------------------------------------------
def fcfs(processes):
    procs = sorted(_reset(processes), key=lambda p: (p.arrival, p.pid))
    time = 0
    timeline = []
    for p in procs:
        if time < p.arrival:
            time = p.arrival
        start = time
        p.response = start - p.arrival
        p.start_time = start
        end = start + p.burst
        timeline.append({"pid": p.pid, "start": start, "end": end})
        p.completion = end
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst
        p.remaining = 0
        time = end
    return timeline, procs


# --------------------------------------------------------------------------
# 2. Shortest Job First (non-preemptive)
# --------------------------------------------------------------------------
def sjf(processes):
    procs = _reset(processes)
    n = len(procs)
    done = [False] * n
    time = 0
    completed = 0
    timeline = []

    while completed < n:
        idx = -1
        best_burst = None
        for i, p in enumerate(procs):
            if not done[i] and p.arrival <= time:
                if best_burst is None or p.burst < best_burst or (
                    p.burst == best_burst and p.arrival < procs[idx].arrival
                ):
                    best_burst = p.burst
                    idx = i
        if idx == -1:
            time = min(p.arrival for i, p in enumerate(procs) if not done[i])
            continue

        p = procs[idx]
        start = time
        p.response = start - p.arrival
        p.start_time = start
        end = start + p.burst
        timeline.append({"pid": p.pid, "start": start, "end": end})
        p.completion = end
        p.turnaround = end - p.arrival
        p.waiting = p.turnaround - p.burst
        p.remaining = 0
        time = end
        done[idx] = True
        completed += 1
    return timeline, procs


# --------------------------------------------------------------------------
# 3. Shortest Remaining Time First (preemptive SJF)
# --------------------------------------------------------------------------
def srtf(processes):
    procs = _reset(processes)
    n = len(procs)
    time = 0
    completed = 0
    timeline = []
    running_pid = None
    seg_start = None
    guard = sum(p.burst for p in procs) + max(p.arrival for p in procs) + 5

    while completed < n and time < guard:
        avail = [p for p in procs if p.arrival <= time and p.remaining > 0]
        if not avail:
            if running_pid is not None:
                timeline.append({"pid": running_pid, "start": seg_start, "end": time})
                running_pid = None
            time += 1
            continue

        p = min(avail, key=lambda x: (x.remaining, x.arrival))
        if p.response == -1:
            p.response = time - p.arrival
        if running_pid != p.pid:
            if running_pid is not None:
                timeline.append({"pid": running_pid, "start": seg_start, "end": time})
            seg_start = time
            running_pid = p.pid

        p.remaining -= 1
        time += 1
        if p.remaining == 0:
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            completed += 1
            timeline.append({"pid": running_pid, "start": seg_start, "end": time})
            running_pid = None
    return timeline, procs


# --------------------------------------------------------------------------
# 4. Priority Scheduling (non-preemptive) - lower number = higher priority
# --------------------------------------------------------------------------
def priority_np(processes):
    procs = _reset(processes)
    n = len(procs)
    done = [False] * n
    time = 0
    completed = 0
    timeline = []

    while completed < n:
        idx = -1
        best_priority = None
        for i, p in enumerate(procs):
            if not done[i] and p.arrival <= time:
                if best_priority is None or p.priority < best_priority or (
                    p.priority == best_priority and p.arrival < procs[idx].arrival
                ):
                    best_priority = p.priority
                    idx = i
        if idx == -1:
            time = min(p.arrival for i, p in enumerate(procs) if not done[i])
            continue

        p = procs[idx]
        start = time
        p.response = start - p.arrival
        p.start_time = start
        end = start + p.burst
        timeline.append({"pid": p.pid, "start": start, "end": end})
        p.completion = end
        p.turnaround = end - p.arrival
        p.waiting = p.turnaround - p.burst
        p.remaining = 0
        time = end
        done[idx] = True
        completed += 1
    return timeline, procs


# --------------------------------------------------------------------------
# 5. Priority Scheduling (preemptive)
# --------------------------------------------------------------------------
def priority_p(processes):
    procs = _reset(processes)
    n = len(procs)
    time = 0
    completed = 0
    timeline = []
    running_pid = None
    seg_start = None
    guard = sum(p.burst for p in procs) + max(p.arrival for p in procs) + 5

    while completed < n and time < guard:
        avail = [p for p in procs if p.arrival <= time and p.remaining > 0]
        if not avail:
            if running_pid is not None:
                timeline.append({"pid": running_pid, "start": seg_start, "end": time})
                running_pid = None
            time += 1
            continue

        p = min(avail, key=lambda x: (x.priority, x.arrival))
        if p.response == -1:
            p.response = time - p.arrival
        if running_pid != p.pid:
            if running_pid is not None:
                timeline.append({"pid": running_pid, "start": seg_start, "end": time})
            seg_start = time
            running_pid = p.pid

        p.remaining -= 1
        time += 1
        if p.remaining == 0:
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            completed += 1
            timeline.append({"pid": running_pid, "start": seg_start, "end": time})
            running_pid = None
    return timeline, procs


# --------------------------------------------------------------------------
# 6. Round Robin
# --------------------------------------------------------------------------
def round_robin(processes, quantum=2):
    procs_sorted = sorted(_reset(processes), key=lambda p: (p.arrival, p.pid))
    n = len(procs_sorted)
    time = 0
    i = 0
    queue = deque()
    timeline = []
    completed = 0

    def admit(upto):
        nonlocal i
        while i < n and procs_sorted[i].arrival <= upto:
            queue.append(procs_sorted[i])
            i += 1

    time = procs_sorted[0].arrival if n else 0
    admit(time)

    while completed < n:
        if not queue:
            time = procs_sorted[i].arrival
            admit(time)
            continue

        p = queue.popleft()
        if p.response == -1:
            p.response = time - p.arrival
        run = min(quantum, p.remaining)
        start = time
        time += run
        p.remaining -= run
        timeline.append({"pid": p.pid, "start": start, "end": time})

        admit(time)  # newcomers join the queue before the just-run process re-enters

        if p.remaining > 0:
            queue.append(p)
        else:
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            completed += 1

    return timeline, procs_sorted


# --------------------------------------------------------------------------
# 7. Multilevel Feedback Queue  (the "creative" showcase algorithm)
#    3 queues by default: quantum 2 -> quantum 4 -> FCFS (no quantum)
# --------------------------------------------------------------------------
def mlfq(processes, quantums=(2, 4, 8)):
    procs_sorted = sorted(_reset(processes), key=lambda p: (p.arrival, p.pid))
    n = len(procs_sorted)
    levels = len(quantums)
    queues = [deque() for _ in range(levels)]
    time = procs_sorted[0].arrival if n else 0
    i = 0
    timeline = []
    completed = 0

    def admit(upto):
        nonlocal i
        while i < n and procs_sorted[i].arrival <= upto:
            queues[0].append(procs_sorted[i])
            i += 1

    admit(time)

    while completed < n:
        level = next((lvl for lvl in range(levels) if queues[lvl]), None)
        if level is None:
            time = procs_sorted[i].arrival
            admit(time)
            continue

        p = queues[level].popleft()
        if p.response == -1:
            p.response = time - p.arrival
        q = quantums[level]
        run = min(q, p.remaining)
        start = time
        time += run
        p.remaining -= run
        timeline.append({"pid": p.pid, "start": start, "end": time, "level": level + 1})

        admit(time)

        if p.remaining > 0:
            next_level = min(level + 1, levels - 1)
            queues[next_level].append(p)
        else:
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            completed += 1

    return timeline, procs_sorted


ALGORITHMS = {
    "FCFS": lambda procs, params: fcfs(procs),
    "SJF (Non-Preemptive)": lambda procs, params: sjf(procs),
    "SRTF (Preemptive SJF)": lambda procs, params: srtf(procs),
    "Priority (Non-Preemptive)": lambda procs, params: priority_np(procs),
    "Priority (Preemptive)": lambda procs, params: priority_p(procs),
    "Round Robin": lambda procs, params: round_robin(procs, quantum=params.get("quantum", 2)),
    "MLFQ (3-Level Feedback Queue)": lambda procs, params: mlfq(
        procs, quantums=params.get("quantums", (2, 4, 8))
    ),
}
