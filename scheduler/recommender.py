"""
scheduler.recommender
-----------------------
The "creative" twist of this project: a tiny decision-support engine
that looks at the computed metrics for every algorithm that was run on
the SAME workload, and recommends the best one for that specific
workload -- the way a real OS course would ask "which algorithm suits
this workload and why?"

It is a transparent weighted-scoring model (NOT a black box), so it is
easy to explain in a viva voce / project defense.
"""


WEIGHTS = {
    "waiting": 0.35,       # lower is better
    "turnaround": 0.25,    # lower is better
    "response": 0.15,      # lower is better
    "utilization": 0.15,   # higher is better
    "throughput": 0.10,    # higher is better
}


def recommend_algorithm(results: dict):
    """
    results: {algo_name: metrics_dict} as returned by compute_metrics()

    Returns (best_algo_name, scores_dict, explanation_str)
    """
    if not results:
        return None, {}, "No results to compare."

    waitings = [m["Average Waiting Time"] for m in results.values()]
    tats = [m["Average Turnaround Time"] for m in results.values()]
    resps = [m["Average Response Time"] for m in results.values()]
    utils_ = [m["CPU Utilization (%)"] for m in results.values()]
    thrpts = [m["Throughput (proc/unit time)"] for m in results.values()]

    def norm_low(value, values):
        lo, hi = min(values), max(values)
        if hi == lo:
            return 1.0
        return 1 - (value - lo) / (hi - lo)   # lower raw value -> higher score

    def norm_high(value, values):
        lo, hi = min(values), max(values)
        if hi == lo:
            return 1.0
        return (value - lo) / (hi - lo)       # higher raw value -> higher score

    scores = {}
    for algo, m in results.items():
        s = (
            WEIGHTS["waiting"] * norm_low(m["Average Waiting Time"], waitings)
            + WEIGHTS["turnaround"] * norm_low(m["Average Turnaround Time"], tats)
            + WEIGHTS["response"] * norm_low(m["Average Response Time"], resps)
            + WEIGHTS["utilization"] * norm_high(m["CPU Utilization (%)"], utils_)
            + WEIGHTS["throughput"] * norm_high(m["Throughput (proc/unit time)"], thrpts)
        )
        scores[algo] = round(s * 100, 2)  # scale to a 0-100 "fitness score"

    best = max(scores, key=scores.get)
    explanation = (
        f"'{best}' scored highest ({scores[best]}/100) on a weighted blend of "
        f"waiting time (35%), turnaround time (25%), response time (15%), "
        f"CPU utilization (15%) and throughput (10%) for THIS workload. "
        f"Change the process mix and a different algorithm may win."
    )
    return best, scores, explanation
