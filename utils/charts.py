"""
utils.charts
-------------
All Plotly figure builders live here, kept separate from app.py so the
Streamlit file stays focused on layout/UX.
"""

import plotly.express as px
import plotly.graph_objects as go

PALETTE = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel


def _color_map(pids):
    return {pid: PALETTE[i % len(PALETTE)] for i, pid in enumerate(sorted(pids))}


def build_gantt_rows(timeline, title="Process Timeline"):
    """One horizontal row per process -- the classic textbook Gantt chart."""
    if not timeline:
        return go.Figure()

    pids = sorted({seg["pid"] for seg in timeline})
    cmap = _color_map(pids)
    fig = go.Figure()

    for seg in timeline:
        level = seg.get("level")
        hover = f"{seg['pid']}<br>Start: {seg['start']}  End: {seg['end']}"
        if level:
            hover += f"<br>Queue level: {level}"
        fig.add_trace(
            go.Bar(
                x=[seg["end"] - seg["start"]],
                y=[seg["pid"]],
                base=[seg["start"]],
                orientation="h",
                marker=dict(color=cmap[seg["pid"]], line=dict(color="#333", width=1)),
                hovertemplate=hover + "<extra></extra>",
                text=f"{seg['end'] - seg['start']}",
                textposition="inside",
                showlegend=False,
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Process",
        barmode="stack",
        height=max(220, 70 + 45 * len(pids)),
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(categoryorder="array", categoryarray=sorted(pids, reverse=True)),
    )
    return fig


def build_cpu_strip(timeline, title="CPU Timeline (single track)"):
    """Everything squeezed onto a single 'CPU' row -- shows context switches at a glance."""
    if not timeline:
        return go.Figure()

    pids = sorted({seg["pid"] for seg in timeline})
    cmap = _color_map(pids)
    fig = go.Figure()
    legend_seen = set()

    for seg in timeline:
        show_legend = seg["pid"] not in legend_seen
        legend_seen.add(seg["pid"])
        fig.add_trace(
            go.Bar(
                x=[seg["end"] - seg["start"]],
                y=["CPU"],
                base=[seg["start"]],
                orientation="h",
                name=seg["pid"],
                marker=dict(color=cmap[seg["pid"]], line=dict(color="#333", width=1)),
                hovertemplate=f"{seg['pid']}<br>Start:{seg['start']} End:{seg['end']}<extra></extra>",
                showlegend=show_legend,
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        barmode="stack",
        height=220,
        legend=dict(orientation="h", yanchor="bottom", y=-0.5),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def build_comparison_bar(results, metric_key, title=None):
    """Grouped bar chart comparing one metric across algorithms."""
    algos = list(results.keys())
    values = [results[a][metric_key] for a in algos]
    fig = go.Figure(
        data=[
            go.Bar(
                x=algos,
                y=values,
                marker=dict(color=px.colors.qualitative.Bold[: len(algos)]),
                text=[round(v, 2) for v in values],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        title=title or metric_key,
        xaxis_title="Algorithm",
        yaxis_title=metric_key,
        height=380,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def build_radar(scores, title="Algorithm Fitness Score (0-100)"):
    """Radar/polar chart -- one axis per algorithm, nice visual summary."""
    algos = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=algos + [algos[0]],
            fill="toself",
            name="Fitness score",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title=title,
        height=420,
        margin=dict(l=40, r=40, t=50, b=20),
    )
    return fig


def build_race_chart(all_results_timelines, title="Completion Race: processes finished over time"):
    """
    all_results_timelines: {algo_name: procs_list}
    Draws a step line per algorithm: x = time, y = cumulative processes completed.
    This is the 'who finishes the workload fastest' visual.
    """
    fig = go.Figure()
    for algo, procs in all_results_timelines.items():
        completions = sorted(p.completion for p in procs)
        x = [0] + completions
        y = list(range(len(completions) + 1))
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=algo,
                line=dict(shape="hv", width=3),
            )
        )
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Processes completed",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig
