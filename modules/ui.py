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
    return (
        '<div class="stat-card">'
        '<div class="stat-num">' + str(number) + '</div>'
        '<div class="stat-label">' + label + '</div>'
        '</div>'
    )


# ── Badges ────────────────────────────────────────────────────

def streak_badge(n: int) -> str:
    if n == 0:
        return ""
    return '<span class="badge badge-streak">🔥 ' + str(n) + 'd streak</span>'


def done_badge() -> str:
    return '<span class="badge badge-done">✓ Done</span>'


def rate_badge(pct: int) -> str:
    if pct == 0:
        return ""
    return '<span class="badge badge-rate">' + str(pct) + '% this week</span>'


# ── Section eyebrow label ─────────────────────────────────────

def eyebrow(text: str) -> None:
    st.markdown('<div class="eyebrow">' + text + '</div>', unsafe_allow_html=True)


# ── Heatmap for one habit ─────────────────────────────────────

def render_heatmap(
    habit: dict,
    days: list[dict],
    cur_streak: int,
    best: int,
    rate_pct: int,
) -> None:
    # Build every piece in plain Python string concatenation.
    # Never embed function calls or ternaries inside f-strings
    # passed to st.markdown — Streamlit can escape them.

    cells_html = ""
    for d in days:
        color = HM_COLOR_DONE if d["done"] else HM_COLOR_EMPTY
        mark  = "✓" if d["done"] else "✗"
        cells_html += (
            '<span class="hm-cell" style="background:' + color + ';" '
            'title="' + d["label"] + ': ' + mark + '"></span>'
        )

    badges_html = ""
    if cur_streak > 0:
        badges_html += '<span class="badge badge-streak">🔥 ' + str(cur_streak) + 'd streak</span> '
    if rate_pct > 0:
        badges_html += '<span class="badge badge-rate">' + str(rate_pct) + '% this week</span>'

    html = (
        '<div class="heatmap-wrap">'
          '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
            '<span style="font-weight:600;font-size:0.92rem;color:var(--text-primary);">'
              + habit["emoji"] + ' ' + habit["name"] +
            '</span>'
            '<div style="display:flex;gap:6px;">' + badges_html + '</div>'
          '</div>'
          '<div>' + cells_html + '</div>'
          '<div class="heatmap-meta">'
            '<div>Current streak <span>' + str(cur_streak) + 'd</span></div>'
            '<div>Longest streak <span>' + str(best) + 'd</span></div>'
          '</div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────

def footer() -> None:
    st.markdown(
        '<div class="footer">Built with Streamlit · Data stored in Google Sheets · Free to deploy</div>',
        unsafe_allow_html=True,
    )
