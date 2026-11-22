"""
CPU Scheduler Simulator -- "SchedulerVerse"
=============================================
An MCA-level Operating Systems mini-project.

Run with:   streamlit run app.py
"""

import io

import pandas as pd
import streamlit as st

from scheduler.process import Process
from scheduler.algorithms import ALGORITHMS
from scheduler.metrics import compute_metrics, process_table
from scheduler.recommender import recommend_algorithm
from utils.random_gen import generate_random_processes
from utils.charts import (
    build_gantt_rows,
    build_cpu_strip,
    build_comparison_bar,
    build_radar,
    build_race_chart,
)

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="SchedulerVerse | CPU Scheduling Simulator",
    page_icon="🛤️",
    layout="wide",
)

st.title("🛤️ SchedulerVerse — CPU Scheduling Simulator")
st.caption(
    "A race track for your processes: every algorithm drives the same workload, "
    "and you watch Gantt charts, KPIs and a recommendation engine decide who wins."
)

ALGO_NAMES = list(ALGORITHMS.keys())

# --------------------------------------------------------------------------
# Sidebar — workload input
# --------------------------------------------------------------------------
st.sidebar.header("1️⃣ Build your workload")
input_mode = st.sidebar.radio("How do you want to supply processes?", ["Manual entry", "Random generator", "Upload CSV"])

processes = []

if input_mode == "Manual entry":
    default_df = pd.DataFrame(
        {
            "PID": ["P1", "P2", "P3", "P4"],
            "Arrival": [0, 1, 2, 3],
            "Burst": [5, 3, 8, 6],
            "Priority": [2, 1, 3, 2],
        }
    )
    st.sidebar.write("Edit the table below (right-click a row to add/delete):")
    edited_df = st.sidebar.data_editor(default_df, num_rows="dynamic", use_container_width=True, key="editor")
    for _, row in edited_df.iterrows():
        try:
            processes.append(
                Process(
                    pid=str(row["PID"]),
                    arrival=int(row["Arrival"]),
                    burst=int(row["Burst"]),
                    priority=int(row["Priority"]),
                )
            )
        except (ValueError, TypeError):
            continue

elif input_mode == "Random generator":
    n = st.sidebar.slider("Number of processes", 2, 15, 6)
    max_arrival = st.sidebar.slider("Max arrival time", 0, 30, 10)
    max_burst = st.sidebar.slider("Max burst time", 1, 30, 10)
    max_priority = st.sidebar.slider("Max priority value", 1, 10, 5)
    seed = st.sidebar.number_input("Random seed (for reproducibility)", min_value=0, value=42, step=1)
    if st.sidebar.button("🎲 Generate workload"):
        st.session_state["random_processes"] = generate_random_processes(
            n=n, max_arrival=max_arrival, max_burst=max_burst, max_priority=max_priority, seed=seed
        )
    processes = st.session_state.get("random_processes", generate_random_processes(
        n=n, max_arrival=max_arrival, max_burst=max_burst, max_priority=max_priority, seed=seed
    ))

else:  # Upload CSV
    st.sidebar.caption("CSV columns required: PID, Arrival, Burst, Priority")
    uploaded = st.sidebar.file_uploader("Upload processes.csv", type=["csv"])
    sample_note = st.sidebar.empty()
    sample_note.caption("No file? Use `sample_data/processes.csv` included in this project.")
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        for _, row in df.iterrows():
            processes.append(
                Process(
                    pid=str(row["PID"]),
                    arrival=int(row["Arrival"]),
                    burst=int(row["Burst"]),
                    priority=int(row.get("Priority", 0)),
                )
            )

st.sidebar.markdown("---")
st.sidebar.header("2️⃣ Choose algorithms to race")
selected_algos = st.sidebar.multiselect(
    "Algorithms", ALGO_NAMES, default=["FCFS", "SJF (Non-Preemptive)", "Round Robin"]
)

params = {}
if "Round Robin" in selected_algos:
    params["quantum"] = st.sidebar.slider("Round Robin quantum", 1, 10, 2)
if "MLFQ (3-Level Feedback Queue)" in selected_algos:
    c1, c2, c3 = st.sidebar.columns(3)
    q1 = c1.number_input("Q1", 1, 10, 2)
    q2 = c2.number_input("Q2", 1, 10, 4)
    q3 = c3.number_input("Q3", 1, 20, 8)
    params["quantums"] = (q1, q2, q3)

run_clicked = st.sidebar.button("▶️ Run Simulation", type="primary", use_container_width=True)

# --------------------------------------------------------------------------
# Show input workload
# --------------------------------------------------------------------------
st.subheader("📋 Workload")
if processes:
    df_in = pd.DataFrame(
        [{"PID": p.pid, "Arrival": p.arrival, "Burst": p.burst, "Priority": p.priority} for p in processes]
    )
    st.dataframe(df_in, use_container_width=True, hide_index=True)
else:
    st.info("Add at least one process from the sidebar to get started.")

# --------------------------------------------------------------------------
# Run + display
# --------------------------------------------------------------------------
if run_clicked and processes and selected_algos:
    results_metrics = {}
    results_procs = {}
    results_timelines = {}

    for algo_name in selected_algos:
        fn = ALGORITHMS[algo_name]
        timeline, procs_out = fn(processes, params)
        results_timelines[algo_name] = timeline
        results_procs[algo_name] = procs_out
        results_metrics[algo_name] = compute_metrics(procs_out, timeline)

    st.markdown("---")
    st.subheader("🏁 Per-Algorithm Results")
    tabs = st.tabs(selected_algos)
    for tab, algo_name in zip(tabs, selected_algos):
        with tab:
            timeline = results_timelines[algo_name]
            procs_out = results_procs[algo_name]
            metrics = results_metrics[algo_name]

            colA, colB = st.columns([3, 2])
            with colA:
                st.plotly_chart(build_gantt_rows(timeline, f"{algo_name} — Process Timeline"), use_container_width=True)
                st.plotly_chart(build_cpu_strip(timeline, f"{algo_name} — Single CPU Track"), use_container_width=True)
            with colB:
                st.markdown("**Summary KPIs**")
                for k, v in metrics.items():
                    st.metric(k, v)

            st.markdown("**Per-process breakdown**")
            st.dataframe(process_table(procs_out), use_container_width=True, hide_index=True)

            # Time-scrubber: "what is running at time T?"
            max_t = max(seg["end"] for seg in timeline)
            t = st.slider(f"🔍 Scrub through time ({algo_name})", 0, max_t, 0, key=f"scrub_{algo_name}")
            running = next((seg["pid"] for seg in timeline if seg["start"] <= t < seg["end"]), None)
            if running:
                st.success(f"At time **t = {t}**, process **{running}** is running on the CPU.")
            else:
                st.warning(f"At time **t = {t}**, the CPU is **idle**.")

    # ----------------------------------------------------------------
    # Comparison section (only meaningful with 2+ algorithms)
    # ----------------------------------------------------------------
    st.markdown("---")
    st.subheader("⚖️ Head-to-Head Comparison")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            build_comparison_bar(results_metrics, "Average Waiting Time", "Average Waiting Time (lower = better)"),
            use_container_width=True,
        )
        st.plotly_chart(
            build_comparison_bar(
                results_metrics, "Average Turnaround Time", "Average Turnaround Time (lower = better)"
            ),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            build_comparison_bar(results_metrics, "CPU Utilization (%)", "CPU Utilization % (higher = better)"),
            use_container_width=True,
        )
        st.plotly_chart(
            build_comparison_bar(results_metrics, "Context Switches", "Context Switches (lower = usually better)"),
            use_container_width=True,
        )

    st.plotly_chart(build_race_chart(results_procs), use_container_width=True)

    # ----------------------------------------------------------------
    # Recommendation engine (the creative centrepiece)
    # ----------------------------------------------------------------
    st.markdown("---")
    st.subheader("🤖 Recommendation Engine")
    best, scores, explanation = recommend_algorithm(results_metrics)
    if best:
        st.success(f"🏆 **Recommended algorithm for this workload: {best}**")
        st.write(explanation)
        st.plotly_chart(build_radar(scores), use_container_width=True)

    # ----------------------------------------------------------------
    # Export
    # ----------------------------------------------------------------
    st.markdown("---")
    st.subheader("⬇️ Export results")
    combined = pd.DataFrame(results_metrics).T
    combined.index.name = "Algorithm"
    csv_buf = io.StringIO()
    combined.to_csv(csv_buf)
    st.download_button(
        "Download comparison metrics (CSV)",
        data=csv_buf.getvalue(),
        file_name="scheduling_comparison.csv",
        mime="text/csv",
    )
    st.dataframe(combined, use_container_width=True)

elif run_clicked and not selected_algos:
    st.error("Select at least one algorithm from the sidebar before running.")
elif run_clicked and not processes:
    st.error("Your workload is empty — add some processes first.")
else:
    st.caption("👈 Configure a workload and algorithms in the sidebar, then click **Run Simulation**.")
