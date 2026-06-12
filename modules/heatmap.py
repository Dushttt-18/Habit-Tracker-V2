# modules/heatmap.py
# ─────────────────────────────────────────────────────────────
# 30-day heatmap section — one row per habit.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
import streamlit as st
from modules import stats, ui
from config.settings import HEATMAP_DAYS


def render(habits: list[dict], completions: dict[str, list[int]]) -> None:
    """Render the full heatmap section."""
    st.markdown("---")
    st.markdown("## 📅 Last 30 Days")

    if not habits:
        st.caption("Add habits to see your heatmap.")
        return

    for habit in habits:
        hid      = habit["id"]
        days     = stats.heatmap_days(hid, completions, n=HEATMAP_DAYS)
        cur_s    = stats.current_streak(hid, completions)
        best_s   = stats.longest_streak(hid, completions)
        rate_pct = int(stats.completion_rate(hid, completions) * 100)
        ui.render_heatmap(habit, days, cur_s, best_s, rate_pct)
