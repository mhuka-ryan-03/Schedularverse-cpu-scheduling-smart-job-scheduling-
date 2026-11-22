"""
scheduler.process
------------------
Defines the Process entity used by every scheduling algorithm in this
project. Keeping it as a single dataclass means every algorithm module
can import and mutate the SAME shape of object, which makes the metrics
layer trivial to write.
"""

from dataclasses import dataclass, field


@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0          # lower number = higher priority (like Unix 'nice')

    # ---- filled in while / after a schedule runs -----------------
    remaining: int = field(init=False)
    completion: int = field(default=0, init=False)
    start_time: int = field(default=-1, init=False)
    waiting: int = field(default=0, init=False)
    turnaround: int = field(default=0, init=False)
    response: int = field(default=-1, init=False)

    def __post_init__(self):
        if self.burst <= 0:
            raise ValueError(f"Process {self.pid}: burst time must be > 0")
        if self.arrival < 0:
            raise ValueError(f"Process {self.pid}: arrival time must be >= 0")
        self.remaining = self.burst

    def reset(self):
        """Reset the runtime fields so the same Process can be reused
        across multiple algorithm runs without cross-contamination."""
        self.remaining = self.burst
        self.completion = 0
        self.start_time = -1
        self.waiting = 0
        self.turnaround = 0
        self.response = -1
