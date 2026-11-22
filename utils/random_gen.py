import random
from scheduler.process import Process


def generate_random_processes(n=6, max_arrival=10, max_burst=10, max_priority=5, seed=None):
    rng = random.Random(seed)
    processes = []
    for i in range(n):
        processes.append(
            Process(
                pid=f"P{i + 1}",
                arrival=rng.randint(0, max_arrival),
                burst=rng.randint(1, max_burst),
                priority=rng.randint(1, max_priority),
            )
        )
    return processes
