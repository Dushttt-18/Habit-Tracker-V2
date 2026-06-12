# modules/sidebar.py
# ─────────────────────────────────────────────────────────────
# Sidebar: add habit form, delete habit, date selector.
# Returns any user actions so app.py can call data functions.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
from datetime import date
import streamlit as st
from modules import data as db


def render() -> date:
    """
    Render the sidebar and return the selected date.
    Handles add/delete habit actions internally.
    """
    with st.sidebar:
        st.markdown("## 🌱 Habit Tracker")
        st.markdown(
            f"<div style='color:#a0aec0;font-size:0.82rem;margin-bottom:1.5rem;'>"
            f"{date.today().strftime('%A, %B %d %Y')}</div>",
            unsafe_allow_html=True,
        )

        # ── Date picker ───────────────────────────────────────
        st.markdown("### 📅 View Date")
        selected = st.date_input("", value=date.today(), label_visibility="collapsed")

        st.divider()

        # ── Add habit ─────────────────────────────────────────
        st.markdown("### ➕ Add Habit")
        col_e, col_n = st.columns([1, 3])
        with col_e:
            emoji = st.text_input("", value="✨", max_chars=2, key="new_emoji", placeholder="🌟")
        with col_n:
            name = st.text_input("", placeholder="Habit name…", key="new_name")

        if st.button("Add habit", use_container_width=True, key="btn_add"):
            if name.strip():
                db.add_habit(name.strip(), emoji.strip() or "✨")
                st.success(f'"{name.strip()}" added!')
                st.rerun()
            else:
                st.warning("Enter a habit name.")

        st.divider()

        # ── Delete habit ──────────────────────────────────────
        st.markdown("### 🗑 Remove Habit")
        habits = db.load_habits()
        if habits:
            del_id = st.selectbox(
                "",
                options=[h["id"] for h in habits],
                format_func=lambda i: next(
                    f"{h['emoji']} {h['name']}" for h in habits if h["id"] == i
                ),
                label_visibility="collapsed",
                key="del_choice",
            )
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("Remove habit", use_container_width=True, key="btn_del"):
                db.delete_habit(del_id)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("No habits yet.")

        st.divider()
        st.markdown(
            "<div style='color:#cbd5e0;font-size:0.72rem;text-align:center;'>"
            "Data saved to Google Sheets · Free forever</div>",
            unsafe_allow_html=True,
        )

    return selected
