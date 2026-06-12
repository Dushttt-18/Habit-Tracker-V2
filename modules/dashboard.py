# modules/dashboard.py
# ─────────────────────────────────────────────────────────────
# Dashboard section: stat cards + daily progress bar.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
from datetime import date
import streamlit as st
from modules import stats, ui


def render(
    habits: list[dict],
    completions: dict[str, list[int]],
    selected_date: date,
) -> None:
    """Render the four stat cards and the progress bar."""
    summary = stats.daily_summary(habits, completions, selected_date)

    # ── Stat cards ────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            ui.stat_card(f"{summary['done']}/{summary['total']}", "Done today"),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            ui.stat_card(f"{summary['pct']}%", "Completion rate"),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            ui.stat_card(summary["best_streak"], "Best streak"),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            ui.stat_card(summary["all_time"], "All-time completions"),
            unsafe_allow_html=True,
        )

    # ── Progress bar ──────────────────────────────────────────
    if summary["total"]:
        st.markdown("<br>", unsafe_allow_html=True)
        ui.eyebrow("Daily Progress")
        st.progress(summary["done"] / summary["total"])
