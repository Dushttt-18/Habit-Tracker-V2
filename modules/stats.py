# modules/stats.py
# ─────────────────────────────────────────────────────────────
# Pure-Python analytics. No Streamlit imports — unit-testable.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
from datetime import date, timedelta
from config.settings import RATE_WINDOW_DAYS, HEATMAP_DAYS


def current_streak(habit_id: int, completions: dict[str, list[int]]) -> int:
    """Count consecutive days ending today where habit was done."""
    streak = 0
    check = date.today()
    while True:
        key = str(check)
        if key in completions and habit_id in completions[key]:
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak


def longest_streak(habit_id: int, completions: dict[str, list[int]]) -> int:
    """Longest consecutive-day streak ever for this habit."""
    if not completions:
        return 0
    all_dates = sorted(completions.keys())
    best = cur = 0
    prev: date | None = None
    for d_str in all_dates:
        if habit_id in completions.get(d_str, []):
            d = date.fromisoformat(d_str)
            cur = cur + 1 if (prev and (d - prev).days == 1) else 1
            best = max(best, cur)
            prev = d
        else:
            prev = None
    return best


def completion_rate(
    habit_id: int,
    completions: dict[str, list[int]],
    window: int = RATE_WINDOW_DAYS,
) -> float:
    """Fraction of the last `window` days the habit was completed (0–1)."""
    done = sum(
        1
        for i in range(window)
        if habit_id in completions.get(str(date.today() - timedelta(days=i)), [])
    )
    return done / window


def daily_summary(
    habits: list[dict],
    completions: dict[str, list[int]],
    for_date: date,
) -> dict:
    """Return aggregated stats for the dashboard stat cards."""
    done_ids = set(completions.get(str(for_date), []))
    total = len(habits)
    done  = len([h for h in habits if h["id"] in done_ids])
    streaks = [current_streak(h["id"], completions) for h in habits]
    return {
        "total":       total,
        "done":        done,
        "pct":         int(done / total * 100) if total else 0,
        "best_streak": max(streaks) if streaks else 0,
        "all_time":    sum(len(v) for v in completions.values()),
    }


def heatmap_days(
    habit_id: int,
    completions: dict[str, list[int]],
    n: int = HEATMAP_DAYS,
) -> list[dict]:
    """
    Return list of {date, done, label} dicts for the last n days,
    oldest first.
    """
    result = []
    for i in range(n - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        key = str(d)
        done = key in completions and habit_id in completions[key]
        result.append({"date": d, "done": done, "label": d.strftime("%b %d")})
    return result
