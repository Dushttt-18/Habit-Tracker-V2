# app.py
# ─────────────────────────────────────────────────────────────
# Entry point. Orchestrates modules — no business logic here.
# ─────────────────────────────────────────────────────────────

import streamlit as st
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT
from modules import ui, sidebar, dashboard, checklist, heatmap
from modules import data as db

# ── Page config (must be first Streamlit call) ────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────
ui.load_css()

# ── Sidebar (returns selected date) ──────────────────────────
selected_date = sidebar.render()

# ── Load data ─────────────────────────────────────────────────
habits      = db.load_habits()
completions = db.load_completions()

# ── Page header ───────────────────────────────────────────────
st.markdown("# 🌱 Habit Tracker")

# ── Dashboard stats ───────────────────────────────────────────
dashboard.render(habits, completions, selected_date)

st.markdown("<br>", unsafe_allow_html=True)

# ── Daily checklist ───────────────────────────────────────────
checklist.render(habits, completions, selected_date)

# ── Heatmap ───────────────────────────────────────────────────
heatmap.render(habits, completions)

# ── Footer ────────────────────────────────────────────────────
ui.footer()
