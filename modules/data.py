# modules/data.py
# ─────────────────────────────────────────────────────────────
# Data layer — all Google Sheets read/write lives here.
# The rest of the app calls these functions; it never touches
# gspread directly. Swap this file to change the backend.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

from config.settings import (
    SHEET_NAME_HABITS,
    SHEET_NAME_COMPLETIONS,
    DEFAULT_HABITS,
)

# ── Auth scopes ───────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ── Connection (cached for the session) ───────────────────────
@st.cache_resource
def get_client() -> gspread.Client:
    """Authenticate once per Streamlit session."""
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


@st.cache_resource
def get_spreadsheet() -> gspread.Spreadsheet:
    client = get_client()
    return client.open(st.secrets["SPREADSHEET_NAME"])


def _get_or_create_sheet(name: str, headers: list[str]) -> gspread.Worksheet:
    """Return a worksheet, creating it with headers if absent."""
    ss = get_spreadsheet()
    try:
        ws = ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers)
    return ws


# ── Habits CRUD ───────────────────────────────────────────────

def load_habits() -> list[dict]:
    """Return list of habit dicts: {id, name, emoji, created}."""
    ws = _get_or_create_sheet(SHEET_NAME_HABITS, ["id", "name", "emoji", "created"])
    rows = ws.get_all_records()

    if not rows:
        # Seed defaults on first run
        seed = [
            {
                "id": i,
                "name": h["name"],
                "emoji": h["emoji"],
                "created": str(date.today()),
            }
            for i, h in enumerate(DEFAULT_HABITS)
        ]
        for h in seed:
            ws.append_row([h["id"], h["name"], h["emoji"], h["created"]])
        return seed

    return [
        {"id": int(r["id"]), "name": r["name"], "emoji": r["emoji"], "created": r["created"]}
        for r in rows
    ]


def add_habit(name: str, emoji: str) -> None:
    """Append a new habit row."""
    ws = _get_or_create_sheet(SHEET_NAME_HABITS, ["id", "name", "emoji", "created"])
    rows = ws.get_all_records()
    new_id = max((int(r["id"]) for r in rows), default=-1) + 1
    ws.append_row([new_id, name.strip(), emoji, str(date.today())])
    st.cache_data.clear()


def delete_habit(habit_id: int) -> None:
    """Delete a habit row by id."""
    ws = _get_or_create_sheet(SHEET_NAME_HABITS, ["id", "name", "emoji", "created"])
    cell = ws.find(str(habit_id), in_column=1)
    if cell:
        ws.delete_rows(cell.row)
    # Also remove completions for this habit
    _remove_habit_completions(habit_id)
    st.cache_data.clear()


# ── Completions CRUD ──────────────────────────────────────────

@st.cache_data(ttl=30)
def load_completions() -> dict[str, list[int]]:
    """Return {date_str: [habit_id, ...]} dict."""
    ws = _get_or_create_sheet(SHEET_NAME_COMPLETIONS, ["date", "habit_ids"])
    rows = ws.get_all_records()
    result: dict[str, list[int]] = {}
    for r in rows:
        try:
            ids = json.loads(r["habit_ids"]) if r["habit_ids"] else []
            result[r["date"]] = [int(i) for i in ids]
        except (json.JSONDecodeError, KeyError):
            pass
    return result


def save_completions_for_date(date_str: str, habit_ids: list[int]) -> None:
    """Upsert the completions row for a given date."""
    ws = _get_or_create_sheet(SHEET_NAME_COMPLETIONS, ["date", "habit_ids"])
    cell = ws.find(date_str, in_column=1)
    ids_json = json.dumps(sorted(habit_ids))
    if cell:
        ws.update_cell(cell.row, 2, ids_json)
    else:
        ws.append_row([date_str, ids_json])
    st.cache_data.clear()


def _remove_habit_completions(habit_id: int) -> None:
    """Strip a deleted habit_id from all completion rows."""
    ws = _get_or_create_sheet(SHEET_NAME_COMPLETIONS, ["date", "habit_ids"])
    rows = ws.get_all_records()
    for i, r in enumerate(rows, start=2):
        try:
            ids = json.loads(r["habit_ids"]) if r["habit_ids"] else []
            if habit_id in ids:
                ids.remove(habit_id)
                ws.update_cell(i, 2, json.dumps(ids))
        except (json.JSONDecodeError, KeyError):
            pass
