# modules/ui.py
# ─────────────────────────────────────────────────────────────
# UI helpers — CSS injection and reusable HTML components.
# All raw HTML strings live here so app.py stays clean.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
import os
import streamlit as st
from config.settings import HM_COLOR_DONE, HM_COLOR_EMPTY


# ── CSS loader ────────────────────────────────────────────────

def load_css() -> None:
    """Inject static/style.css into the Streamlit page."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "static", "style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ── Stat card ─────────────────────────────────────────────────

def stat_card(number: str | int, label: str) -> str:
    return f"""
    <div class="stat-card">
        <div class="stat-num">{number}</div>
        <div class="stat-label">{label}</div>
    </div>"""


# ── Badges ────────────────────────────────────────────────────

def streak_badge(n: int) -> str:
    if n == 0:
        return ""
    return f'<span class="badge badge-streak">🔥 {n}d streak</span>'


def done_badge() -> str:
    return '<span class="badge badge-done">✓ Done</span>'


def rate_badge(pct: int) -> str:
    return f'<span class="badge badge-rate">{pct}% this week</span>'


# ── Section eyebrow label ─────────────────────────────────────

def eyebrow(text: str) -> None:
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


# ── Heatmap for one habit ─────────────────────────────────────

def render_heatmap(
    habit: dict,
    days: list[dict],   # from stats.heatmap_days()
    cur_streak: int,
    best: int,
    rate_pct: int,
) -> None:
    cells = "".join(
        f'<span class="hm-cell" '
        f'style="background:{ HM_COLOR_DONE if d["done"] else HM_COLOR_EMPTY };" '
        f'title="{d["label"]}: {"✓" if d["done"] else "✗"}"></span>'
        for d in days
    )
    st.markdown(
        f"""
        <div class="heatmap-wrap">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <span style="font-weight:600;font-size:0.92rem;color:var(--text-primary);">
              {habit["emoji"]} {habit["name"]}
            </span>
            <div style="display:flex;gap:6px;">
              {streak_badge(cur_streak) if cur_streak > 0 else ""}
              {rate_badge(rate_pct) if rate_pct > 0 else ""}
            </div>
          </div>
          <div>{cells}</div>
          <div class="heatmap-meta">
            <div>Current streak <span>{cur_streak}d</span></div>
            <div>Longest streak <span>{best}d</span></div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Footer ────────────────────────────────────────────────────

def footer() -> None:
    st.markdown(
        '<div class="footer">Built with Streamlit · Data stored in Google Sheets · Free to deploy</div>',
        unsafe_allow_html=True,
    )
