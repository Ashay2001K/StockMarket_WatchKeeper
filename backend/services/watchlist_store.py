"""
Watchlist Storage Service.
Provides persistent storage for custom user watchlists.
Supports hybrid storage:
  - Supabase PostgREST (Primary Production)
  - SQLite (Zero-setup local development fallback)

NOTE: Production cloud deployments (e.g. Render, Fly.io) have ephemeral container
filesystems. Local SQLite data will reset when the instance restarts or scales down.
For production deployments, SUPABASE_URL and SUPABASE_KEY must be provided.
"""

import os
import sqlite3
import logging
from typing import List, Optional, Tuple

from backend.config import settings
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

DEFAULT_WATCHLIST_SYMBOLS = [
    "MCX",
    "POLYCAB",
    "APARINDS",
    "TDPOWERSYS",
    "TRENT",
    "HAL",
    "BEL",
    "DIXON",
    "KAYNES",
    "BSE"
]


def normalize_symbol(symbol: str) -> str:
    """
    Normalizes stock symbol by stripping whitespace, converting to uppercase,
    and removing exchange suffixes (.NS, .BO).
    """
    if not symbol:
        return ""
    return symbol.strip().upper().replace(".NS", "").replace(".BO", "")


class WatchlistStore:
    """
    Unified storage repository for user watchlists.
    """

    def __init__(self):
        self.supabase = SupabaseClient(settings.supabase_url, settings.supabase_key)
        self.is_remote = self.supabase.is_configured
        self.sqlite_db_path = os.path.join(settings.cache_dir, "watchkeeper.db")

        if not self.is_remote:
            # Production storage guardrail check
            env_mode = settings.environment.lower()
            if env_mode not in ("development", "test", "testing", "dev"):
                logger.warning(
                    "WARNING: Running with ephemeral SQLite storage. "
                    "Custom watchlist changes will reset on container restart. "
                    "Configure Supabase for persistent cloud deployment."
                )
            self._init_sqlite()

    def _get_sqlite_conn(self) -> sqlite3.Connection:
        os.makedirs(os.path.dirname(self.sqlite_db_path), exist_ok=True)
        conn = sqlite3.connect(self.sqlite_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self):
        """Initializes SQLite schema for watchlists."""
        try:
            with self._get_sqlite_conn() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS watchlists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        notes TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, symbol)
                    );
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlists(user_id);"
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize SQLite watchlists table: {e}")

    def get_symbols(self, user_id: str = "default_user") -> List[str]:
        """
        Retrieves normalized list of watchlisted symbols for the user.
        If empty, initializes user with default curated momentum symbols.
        """
        uid = getattr(user_id, "default", user_id) if not isinstance(user_id, str) else user_id
        uid = str(uid)
        if self.is_remote:
            symbols = self.supabase.get_user_watchlist(uid)
            if not symbols:
                # Seed defaults
                self.supabase.reset_user_watchlist(DEFAULT_WATCHLIST_SYMBOLS, uid)
                return [normalize_symbol(s) for s in DEFAULT_WATCHLIST_SYMBOLS]
            # Deduplicate while preserving order
            seen = set()
            normalized = []
            for s in symbols:
                ns = normalize_symbol(s)
                if ns and ns not in seen:
                    seen.add(ns)
                    normalized.append(ns)
            return normalized

        # SQLite fallback
        try:
            with self._get_sqlite_conn() as conn:
                cursor = conn.execute(
                    "SELECT symbol FROM watchlists WHERE user_id = ? ORDER BY id ASC",
                    (user_id,)
                )
                rows = cursor.fetchall()
                if not rows:
                    # Seed default symbols
                    for sym in DEFAULT_WATCHLIST_SYMBOLS:
                        conn.execute(
                            "INSERT OR IGNORE INTO watchlists (user_id, symbol, notes) VALUES (?, ?, ?)",
                            (user_id, normalize_symbol(sym), "Curated Momentum Default")
                        )
                    conn.commit()
                    return [normalize_symbol(s) for s in DEFAULT_WATCHLIST_SYMBOLS]

                seen = set()
                result = []
                for row in rows:
                    ns = normalize_symbol(row["symbol"])
                    if ns and ns not in seen:
                        seen.add(ns)
                        result.append(ns)
                return result
        except Exception as e:
            logger.error(f"Error querying SQLite watchlist: {e}")
            return [normalize_symbol(s) for s in DEFAULT_WATCHLIST_SYMBOLS]

    def add_symbol(self, symbol: str, user_id: str = "default_user", notes: str = "") -> Tuple[bool, str]:
        """
        Adds a normalized ticker to the user's watchlist.
        Returns (success: bool, message: str).
        """
        uid = str(getattr(user_id, "default", user_id))
        clean_sym = normalize_symbol(symbol)
        if not clean_sym:
            return False, "Invalid ticker symbol."

        current_symbols = self.get_symbols(uid)
        if clean_sym in current_symbols:
            return False, f"'{clean_sym}' is already in your watchlist."

        if self.is_remote:
            success = self.supabase.add_watchlist_symbol(clean_sym, user_id=uid, notes=notes)
            if success:
                return True, f"'{clean_sym}' added to watchlist."
            return False, f"Failed to persist '{clean_sym}' to remote database."

        # SQLite fallback
        try:
            with self._get_sqlite_conn() as conn:
                conn.execute(
                    "INSERT INTO watchlists (user_id, symbol, notes) VALUES (?, ?, ?)",
                    (uid, clean_sym, notes)
                )
                conn.commit()
                return True, f"'{clean_sym}' added to watchlist."
        except sqlite3.IntegrityError:
            return False, f"'{clean_sym}' is already in your watchlist."
        except Exception as e:
            logger.error(f"Error adding symbol to SQLite watchlist: {e}")
            return False, str(e)

    def remove_symbol(self, symbol: str, user_id: str = "default_user") -> Tuple[bool, str]:
        """
        Removes a ticker from the user's watchlist.
        Returns (success: bool, message: str).
        """
        uid = str(getattr(user_id, "default", user_id))
        clean_sym = normalize_symbol(symbol)
        if not clean_sym:
            return False, "Invalid ticker symbol."

        if self.is_remote:
            success = self.supabase.remove_watchlist_symbol(clean_sym, user_id=uid)
            if success:
                return True, f"'{clean_sym}' removed from watchlist."
            return False, f"Failed to remove '{clean_sym}' from remote database."

        # SQLite fallback
        try:
            with self._get_sqlite_conn() as conn:
                cursor = conn.execute(
                    "DELETE FROM watchlists WHERE user_id = ? AND symbol = ?",
                    (uid, clean_sym)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    return True, f"'{clean_sym}' removed from watchlist."
                return False, f"'{clean_sym}' was not found in your watchlist."
        except Exception as e:
            logger.error(f"Error removing symbol from SQLite watchlist: {e}")
            return False, str(e)

    def reset_watchlist(self, user_id: str = "default_user") -> List[str]:
        """
        Resets user's watchlist back to default curated momentum symbols.
        """
        uid = str(getattr(user_id, "default", user_id))
        clean_defaults = [normalize_symbol(s) for s in DEFAULT_WATCHLIST_SYMBOLS]
        if self.is_remote:
            self.supabase.reset_user_watchlist(clean_defaults, user_id=uid)
            return clean_defaults

        # SQLite fallback
        try:
            with self._get_sqlite_conn() as conn:
                conn.execute("DELETE FROM watchlists WHERE user_id = ?", (uid,))
                for sym in clean_defaults:
                    conn.execute(
                        "INSERT INTO watchlists (user_id, symbol, notes) VALUES (?, ?, ?)",
                        (uid, sym, "Curated Momentum Default")
                    )
                conn.commit()
                return clean_defaults
        except Exception as e:
            logger.error(f"Error resetting SQLite watchlist: {e}")
            return clean_defaults


watchlist_store = WatchlistStore()
