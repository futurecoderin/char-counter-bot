"""
Google Sheets Activity Logger for Character Counter Bot.

Setup:
  1. Create a Google Cloud Service Account and download the JSON key.
  2. Place the key at the path specified by GOOGLE_CREDENTIALS_PATH in your .env
     (default: ./google_credentials.json next to bot.py).
  3. Set GOOGLE_SPREADSHEET_ID in your .env.
  4. Share the Google Sheet with the service account email (Editor access).

If credentials are missing, logging is silently skipped and the bot runs normally.
"""

import os
import logging
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Internal state ────────────────────────────────────────────
_lock          = threading.Lock()
_sheet_cache: dict = {}   # tab_name → gspread.Worksheet
_spreadsheet   = None
_initialized   = False
_disabled      = False    # permanently disabled if credentials are missing


def _init():
    """Lazy-initialize the gspread client (thread-safe, retries on transient errors)."""
    global _spreadsheet, _initialized, _disabled

    if _initialized or _disabled:
        return

    with _lock:
        if _initialized or _disabled:
            return
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            script_dir  = os.path.dirname(os.path.abspath(__file__))
            creds_path  = os.getenv(
                "GOOGLE_CREDENTIALS_PATH",
                os.path.join(script_dir, "google_credentials.json")
            )
            spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID", "").strip()

            if not os.path.exists(creds_path):
                logger.warning("Sheets: credentials file not found — logging disabled.")
                _disabled = True
                return

            if not spreadsheet_id:
                logger.warning("Sheets: GOOGLE_SPREADSHEET_ID not set — logging disabled.")
                _disabled = True
                return

            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds  = Credentials.from_service_account_file(creds_path, scopes=scopes)
            client = gspread.authorize(creds)
            _spreadsheet = client.open_by_key(spreadsheet_id)
            _initialized = True
            logger.info("Sheets logger initialized.")

        except Exception as e:
            # Transient failure — will retry on next call
            logger.error(f"Sheets init failed (will retry): {e}")


def _get_worksheet(tab_name: str, headers: list):
    """Return (and cache) a worksheet, creating it with headers if needed."""
    if tab_name in _sheet_cache:
        return _sheet_cache[tab_name]

    with _lock:
        if tab_name in _sheet_cache:
            return _sheet_cache[tab_name]
        try:
            try:
                ws = _spreadsheet.worksheet(tab_name)
            except Exception:
                ws = _spreadsheet.add_worksheet(title=tab_name, rows=5000, cols=len(headers))
                ws.append_row(headers, value_input_option="USER_ENTERED")
            _sheet_cache[tab_name] = ws
            return ws
        except Exception as e:
            logger.error(f"Sheets: could not get/create tab '{tab_name}': {e}")
            return None


def _append_async(tab_name: str, headers: list, row: list):
    """Append a row in a daemon thread — never blocks the bot."""
    def _write():
        _init()
        if _disabled or _spreadsheet is None:
            return
        try:
            ws = _get_worksheet(tab_name, headers)
            if ws:
                ws.append_row(row, value_input_option="USER_ENTERED")
        except Exception as e:
            logger.error(f"Sheets: failed to write row: {e}")

    threading.Thread(target=_write, daemon=True).start()


# ── Character Counter Bot logging ─────────────────────────────

_CHAR_COUNTER_HEADERS = [
    "Timestamp (UTC)", "User ID", "Username", "Full Name", "Language",
    "Action", "Detail",
]


def log_char_counter(user, action: str, detail: str = ""):
    """
    Log a Character Counter Bot event to Google Sheets.

    Parameters
    ----------
    user   : telebot message.from_user object
    action : e.g. "/start or /help", "Text Analyzed", "Forwarded Message", "No Text Sent"
    detail : e.g. "chars=142, words=28, lines=3"
    """
    username  = f"@{user.username}" if getattr(user, "username", None) else "N/A"
    full_name = " ".join(filter(None, [
        getattr(user, "first_name", "") or "",
        getattr(user, "last_name",  "") or "",
    ])) or "N/A"

    row = [
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        str(getattr(user, "id", "")),
        username,
        full_name,
        getattr(user, "language_code", "N/A") or "N/A",
        action,
        str(detail)[:500],
    ]
    _append_async("Char Counter", _CHAR_COUNTER_HEADERS, row)
