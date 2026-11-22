# 🛤️ SchedulerVerse — CPU Scheduling Simulator
### An MCA-level Operating Systems Mini / Major Project

SchedulerVerse treats CPU scheduling like a **race**: the same workload of
processes is run through several classic scheduling algorithms, and you get
Gantt charts, KPIs, comparison charts, and an **AI-style recommendation
engine** that tells you which algorithm actually won for that workload — and
why — in one interactive Streamlit dashboard.

---

## ✨ Features

| Area | What it does |
|---|---|
| **7 algorithms** | FCFS, SJF (non-preemptive), SRTF (preemptive), Priority (non-preemptive), Priority (preemptive), Round Robin, and a 3-level **Multilevel Feedback Queue (MLFQ)** |
| **3 input modes** | Manual entry (editable table), random workload generator (seeded/reproducible), or CSV upload |
| **Gantt visualizations** | Per-process row Gantt chart + a single-track "CPU strip" that makes context switches obvious |
| **Time scrubber** | Drag a slider to any instant `t` and see exactly which process is running (or if the CPU is idle) |
| **KPIs per algorithm** | Average waiting / turnaround / response time, CPU utilization %, throughput, context switches, makespan |
| **Head-to-head comparison** | Grouped bar charts across every algorithm you selected |
| **🏁 Completion race chart** | A step-line chart showing how fast each algorithm finishes the whole workload |
| **🤖 Recommendation engine** | A transparent, explainable weighted-scoring model (not a black box) that recommends the best algorithm for *this specific* workload, visualized as a radar/fitness chart |
| **Export** | Download the full comparison table as CSV |

---

## 📂 Project Structure

```
cpu_scheduler_project/
├── app.py                      # Streamlit UI (entry point)
├── requirements.txt
├── sample_data/
│   └── processes.csv           # Ready-to-upload sample workload
├── scheduler/
│   ├── process.py              # Process dataclass
│   ├── algorithms.py            # All 7 scheduling algorithms
│   ├── metrics.py               # KPI + per-process table computation
│   └── recommender.py           # Weighted-scoring recommendation engine
├── utils/
│   ├── random_gen.py            # Random workload generator
│   └── charts.py                # All Plotly chart builders
└── tests/
    └── test_algorithms.py       # Sanity tests (no pytest required to run)
```

---

## 🚀 Running it in VS Code

1. **Unzip** this project and open the folder in VS Code.
2. Open a terminal inside VS Code (`` Ctrl+` ``) and create a virtual environment:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

5. Your browser will open automatically at `http://localhost:8501`.

6. (Optional) Sanity-check the algorithms without Streamlit:

   ```bash
   python tests/test_algorithms.py
   ```

---

## 🧠 How to use it

1. **Build a workload** in the sidebar — type your own processes, generate a
   random batch, or upload `sample_data/processes.csv`.
2. **Pick the algorithms** you want to compare (try selecting all 7!).
3. For Round Robin / MLFQ, set the time quantum(s).
4. Click **▶️ Run Simulation**.
5. Explore each algorithm's tab for its Gantt chart + KPIs, then scroll down
   for the head-to-head comparison, the completion race chart, and the
   recommendation engine's verdict.

---

## 📖 Algorithm notes (for your project report / viva)

- **FCFS** — simplest, non-preemptive, can suffer from the *convoy effect*.
- **SJF** — optimal average waiting time among non-preemptive algorithms,
  but needs to know burst times in advance and can starve long jobs.
- **SRTF** — preemptive version of SJF; reacts to new short jobs instantly.
- **Priority (NP / P)** — order driven by an external priority number; can
  starve low-priority processes (classic fix: *aging*, not implemented here
  to keep the demo simple — a good "future enhancement" point).
- **Round Robin** — fair, time-sliced, good response time, but throughput
  depends heavily on the quantum size (too small → too many context
  switches, too large → degenerates to FCFS).
- **MLFQ** — the "creative" showcase algorithm: new processes start in a
  high-priority, short-quantum queue, and processes that use up their
  quantum repeatedly get pushed into longer-quantum queues — this
  approximates how real operating systems (Windows, Linux's older O(1)
  scheduler) prioritize interactive/short tasks over CPU-bound ones,
  without needing to know burst times in advance like SJF/SRTF do.

---

## 🔭 Possible future enhancements (for extending this project)

- Add **aging** to priority scheduling to prevent starvation.
- Add **I/O bursts** (CPU-I/O burst cycles) instead of pure CPU bursts.
- Add a **multi-core** simulation mode (load balancing across N CPUs).
- Persist workloads/results to a small SQLite database for history tracking.
- Add animated (auto-playing) Gantt chart instead of a manual time scrubber.

---

## 🧰 Tech Stack

- **Python 3.9+**
- **Streamlit** — interactive web UI
- **Plotly** — Gantt charts, bar charts, radar chart, race chart
- **Pandas** — tabular data handling

---

### 🎓 Submitted as an MCA Operating Systems mini-project — feel free to
extend, restyle, or rebrand for your own submission.
