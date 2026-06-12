# modules/checklist.py
# ─────────────────────────────────────────────────────────────
# Daily checklist: renders habit rows with checkboxes.
# Writes back to Google Sheets only when a value changes.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
from datetime import date
import streamlit as st
from modules import data as db, stats, ui


def render(
    habits: list[dict],
    completions: dict[str, list[int]],
    selected_date: date,
) -> None:
    """Render the interactive checklist for selected_date."""
    date_str  = str(selected_date)
    done_ids  = set(completions.get(date_str, []))
    is_today  = selected_date == date.today()

    ui.eyebrow(selected_date.strftime("%A, %B %d"))

    if not habits:
        st.info("No habits yet — add one in the sidebar to get started.")
        return

    changed = False

    for habit in habits:
        hid      = habit["id"]
        is_done  = hid in done_ids
        streak   = stats.current_streak(hid, completions)
        rate_pct = int(stats.completion_rate(hid, completions) * 100)

        col_cb, col_info, col_badges = st.columns([0.07, 0.65, 0.28])

        with col_cb:
            new_val = st.checkbox(
                "", value=is_done,
                key=f"cb_{hid}_{date_str}",
                disabled=False,
            )

        with col_info:
            name_cls = "habit-name done" if is_done else "habit-name"
            st.markdown(
                f'<div style="padding-top:5px;">'
                f'<span class="{name_cls}">{habit["emoji"]} {habit["name"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col_badges:
            badges = ""
            if is_done:
                badges += ui.done_badge() + " "
            if streak > 0:
                badges += ui.streak_badge(streak)
            st.markdown(
                f'<div style="padding-top:5px;text-align:right;">{badges}</div>',
                unsafe_allow_html=True,
            )

        # Detect toggle
        if new_val != is_done:
            if new_val:
                done_ids.add(hid)
            else:
                done_ids.discard(hid)
            changed = True

    # Persist only if something changed
    if changed:
        db.save_completions_for_date(date_str, list(done_ids))
        st.rerun()
