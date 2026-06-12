# config/settings.py
# ─────────────────────────────────────────────────────────────
# Central config for the Habit Tracker app.
# Add new settings here — never scatter magic values in modules.
# ─────────────────────────────────────────────────────────────

# ── App metadata ──────────────────────────────────────────────
APP_TITLE       = "Habit Tracker"
APP_ICON        = "🌱"
APP_LAYOUT      = "wide"

# ── Google Sheets ─────────────────────────────────────────────
SHEET_NAME_HABITS      = "habits"       # tab for habit definitions
SHEET_NAME_COMPLETIONS = "completions"  # tab for daily completions

# ── Default starter habits (shown on first run) ───────────────
DEFAULT_HABITS = [
    {"name": "Morning meditation", "emoji": "🧘"},
    {"name": "Exercise 30 min",    "emoji": "💪"},
    {"name": "Read 20 pages",      "emoji": "📖"},
    {"name": "Drink 8 glasses water", "emoji": "💧"},
    {"name": "No social media before noon", "emoji": "📵"},
]

# ── Heatmap ───────────────────────────────────────────────────
HEATMAP_DAYS = 30          # how many days to show in the heatmap

# ── Streak / stats ────────────────────────────────────────────
RATE_WINDOW_DAYS = 7       # window for "completion rate" badge

# ── Colours used in Python (heatmap cells rendered via HTML) ──
HM_COLOR_DONE  = "#22c55e"
HM_COLOR_EMPTY = "#edf2f7"
