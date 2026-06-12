# modules/data.py
# ─────────────────────────────────────────────────────────────
# Data layer — all Google Sheets read/write lives here.
# The rest of the app calls these functions; it never touches
# gspread directly. Swap this file to change the backend.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import time
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


# ── Retry helper ──────────────────────────────────────────────
def _retry(fn, retries: int = 3, delay: float = 2.0):
    """Call fn(), retrying on APIError up to `retries` times."""
    for attempt in range(retries):
        try:
            return fn()
        except gspread.exceptions.APIError as e:
            if attempt == retries - 1:
                raise
            time.sleep(delay * (attempt + 1))


# ── Connection ────────────────────────────────────────────────
# Use cache_resource only for the credentials object (heavy).
# Re-open the spreadsheet each time so we always get a fresh
# handle — avoids stale worksheet references after add/delete.

@st.cache_resource
def _get_creds() -> Credentials:
    creds_dict = st.secrets["gcp_service_account"]
    return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)


def _get_client() -> gspread.Client:
    return gspread.authorize(_get_creds())


def _get_spreadsheet() -> gspread.Spreadsheet:
    return _get_client().open(st.secrets["SPREADSHEET_NAME"])


def _get_or_create_sheet(name: str, headers: list[str]) -> gspread.Worksheet:
    """Return a worksheet, creating it with headers if absent."""
    ss = _get_spreadsheet()
    try:
        return ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers)
        return ws


# ── Habits CRUD ───────────────────────────────────────────────

@st.cache_data(ttl=60)
def load_habits() -> list[dict]:
    """Return list of habit dicts: {id, name, emoji, created}."""
    ws = _get_or_create_sheet(SHEET_NAME_HABITS, ["id", "name", "emoji", "created"])
    rows = _retry(ws.get_all_records)

    if not rows:
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
            _retry(lambda h=h: ws.append_row([h["id"], h["name"], h["emoji"], h["created"]]))
        return seed

    return [
        {"id": int(r["id"]), "name": r["name"], "emoji": r["emoji"], "created": r["created"]}
        for r in rows
    ]


def add_habit(name: str, emoji: str) -> None:
    """Append a new habit row."""
    ws = _get_or_create_sheet(SHEET_NAME_HABITS, ["id", "name", "emoji", "created"])
    rows = _retry(ws.get_all_records)
    new_id = max((int(r["id"]) for r in rows), default=-1) + 1
    _retry(lambda: ws.append_row([new_id, name.strip(), emoji, str(date.today())]))
    st.cache_data.clear()


def delete_habit(habit_id: int) -> None:
    """Delete a habit row by id."""
    ws = _get_or_create_sheet(SHEET_NAME_HABITS, ["id", "name", "emoji", "created"])
    cell = _retry(lambda: ws.find(str(habit_id), in_column=1))
    if cell:
        _retry(lambda: ws.delete_rows(cell.row))
    _remove_habit_completions(habit_id)
    st.cache_data.clear()


# ── Completions CRUD ──────────────────────────────────────────

@st.cache_data(ttl=30)
def load_completions() -> dict[str, list[int]]:
    """Return {date_str: [habit_id, ...]} dict."""
    ws = _get_or_create_sheet(SHEET_NAME_COMPLETIONS, ["date", "habit_ids"])
    rows = _retry(ws.get_all_records)
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
    cell = _retry(lambda: ws.find(date_str, in_column=1))
    ids_json = json.dumps(sorted(habit_ids))
    if cell:
        _retry(lambda: ws.update_cell(cell.row, 2, ids_json))
    else:
        _retry(lambda: ws.append_row([date_str, ids_json]))
    st.cache_data.clear()


def _remove_habit_completions(habit_id: int) -> None:
    """Strip a deleted habit_id from all completion rows."""
    ws = _get_or_create_sheet(SHEET_NAME_COMPLETIONS, ["date", "habit_ids"])
    rows = _retry(ws.get_all_records)
    for i, r in enumerate(rows, start=2):
        try:
            ids = json.loads(r["habit_ids"]) if r["habit_ids"] else []
            if habit_id in ids:
                ids.remove(habit_id)
                _retry(lambda: ws.update_cell(i, 2, json.dumps(ids)))
        except (json.JSONDecodeError, KeyError):
            pass
