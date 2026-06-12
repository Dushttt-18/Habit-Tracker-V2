# modules/checklist.py
from __future__ import annotations
from datetime import date
import streamlit as st
from modules import data as db, stats, ui


def render(
    habits: list[dict],
    completions: dict[str, list[int]],
    selected_date: date,
) -> None:
    date_str = str(selected_date)
    done_ids = set(completions.get(date_str, []))

    ui.eyebrow(selected_date.strftime("%A, %B %d"))

    if not habits:
        st.info("No habits yet — add one in the sidebar to get started.")
        return

    changed = False

    for habit in habits:
        hid     = habit["id"]
        is_done = hid in done_ids
        streak  = stats.current_streak(hid, completions)

        col_cb, col_info, col_badges = st.columns([0.07, 0.65, 0.28])

        with col_cb:
            new_val = st.checkbox("", value=is_done, key="cb_" + str(hid) + "_" + date_str)

        with col_info:
            name_cls = "habit-name done" if is_done else "habit-name"
            # Build with concatenation — no f-string around HTML variables
            html = (
                '<div style="padding-top:5px;">'
                '<span class="' + name_cls + '">'
                + habit["emoji"] + " " + habit["name"] +
                '</span></div>'
            )
            st.markdown(html, unsafe_allow_html=True)

        with col_badges:
            parts = []
            if is_done:
                parts.append('<span class="badge badge-done">✓ Done</span>')
            if streak > 0:
                parts.append('<span class="badge badge-streak">🔥 ' + str(streak) + 'd streak</span>')
            inner = " ".join(parts)
            html = '<div style="padding-top:5px;text-align:right;min-height:28px;">' + inner + '</div>'
            st.markdown(html, unsafe_allow_html=True)

        if new_val != is_done:
            if new_val:
                done_ids.add(hid)
            else:
                done_ids.discard(hid)
            changed = True

    if changed:
        db.save_completions_for_date(date_str, list(done_ids))
        st.rerun()
