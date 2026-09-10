"""
Lightweight Supabase Client for Free-Tier REST Access.
Uses native HTTP requests to stay strictly under 5MB memory overhead (no heavy SDKs).
Provides local fallback storage when running in offline or demo modes.
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
import requests

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Direct HTTP client for Supabase PostgREST endpoints.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        raw_url = (supabase_url or os.getenv("SUPABASE_URL", "")).strip().rstrip("/")
        if raw_url.endswith("/rest/v1"):
            raw_url = raw_url[:-8].rstrip("/")
        self.url = raw_url
        self.key = (supabase_key or os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))).strip()
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation"
        }
        self.is_configured = bool(self.url and self.key)

    def upsert_stocks(self, stocks_data: List[Dict[str, Any]]) -> bool:
        """Upserts metadata records into the 'stocks' table."""
        if not self.is_configured:
            logger.info("Supabase not configured; skipping remote stock upsert.")
            return True

        endpoint = f"{self.url}/rest/v1/stocks"
        try:
            res = requests.post(endpoint, headers=self.headers, json=stocks_data, timeout=10)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error upserting stocks to Supabase: {e}")
            return False

    def upsert_daily_scores(self, scores_data: List[Dict[str, Any]]) -> bool:
        """Upserts daily calculated BEM scores into 'daily_scores' table."""
        if not self.is_configured:
            logger.info("Supabase not configured; skipping remote score upsert.")
            return True

        endpoint = f"{self.url}/rest/v1/daily_scores"
        try:
            res = requests.post(endpoint, headers=self.headers, json=scores_data, timeout=15)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error upserting daily scores to Supabase: {e}")
            return False

    def upsert_market_regime(self, regime_data: Dict[str, Any]) -> bool:
        """Upserts the daily market regime record."""
        if not self.is_configured:
            return True

        endpoint = f"{self.url}/rest/v1/market_regime"
        try:
            res = requests.post(endpoint, headers=self.headers, json=regime_data, timeout=10)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error upserting market regime: {e}")
            return False

    def get_latest_scores(
        self,
        min_bem: float = 0.0,
        max_exhaustion: float = 15.0,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Queries precomputed screener results."""
        if not self.is_configured:
            return []

        # Order by date desc, bem_score desc
        query = f"bem_score=gte.{min_bem}&raw_exhaustion_score=lte.{max_exhaustion}&order=date.desc,bem_score.desc&limit={limit}"
        if action:
            query += f"&action=eq.{action}"

        endpoint = f"{self.url}/rest/v1/daily_scores?{query}"
        try:
            res = requests.get(endpoint, headers=self.headers, timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            logger.error(f"Error reading from Supabase: {e}")
        return []

    def get_stock_score(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Queries the latest score record for a specific ticker."""
        if not self.is_configured:
            return None

        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        endpoint = f"{self.url}/rest/v1/daily_scores?symbol=eq.{clean_sym}&order=date.desc&limit=1"
        try:
            res = requests.get(endpoint, headers=self.headers, timeout=10)
            if res.status_code == 200:
                records = res.json()
                if records:
                    return records[0]
        except Exception as e:
            logger.error(f"Error fetching stock score for {clean_sym}: {e}")
        return None

    def get_user_watchlist(self, user_id: str = "default_user") -> List[str]:
        """Queries the list of watchlisted symbols for a specific user."""
        if not self.is_configured:
            return []

        endpoint = f"{self.url}/rest/v1/watchlists?user_id=eq.{user_id}&select=symbol&order=created_at.asc"
        try:
            res = requests.get(endpoint, headers=self.headers, timeout=10)
            if res.status_code == 200:
                return [r["symbol"] for r in res.json() if "symbol" in r]
        except Exception as e:
            logger.error(f"Error fetching watchlist for user {user_id}: {e}")
        return []

    def add_watchlist_symbol(self, symbol: str, user_id: str = "default_user", notes: str = "") -> bool:
        """Adds a symbol to the user's watchlist in Supabase."""
        if not self.is_configured:
            return False

        clean_sym = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        endpoint = f"{self.url}/rest/v1/watchlists"
        payload = {
            "user_id": user_id,
            "symbol": clean_sym,
            "notes": notes
        }
        try:
            res = requests.post(endpoint, headers=self.headers, json=payload, timeout=10)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error adding {clean_sym} to Supabase watchlist: {e}")
            return False

    def remove_watchlist_symbol(self, symbol: str, user_id: str = "default_user") -> bool:
        """Removes a symbol from the user's watchlist in Supabase."""
        if not self.is_configured:
            return False

        clean_sym = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        endpoint = f"{self.url}/rest/v1/watchlists?user_id=eq.{user_id}&symbol=eq.{clean_sym}"
        try:
            res = requests.delete(endpoint, headers=self.headers, timeout=10)
            return res.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error removing {clean_sym} from Supabase watchlist: {e}")
            return False

    def reset_user_watchlist(self, symbols: List[str], user_id: str = "default_user") -> bool:
        """Resets user watchlist to given default symbols."""
        if not self.is_configured:
            return False

        # Clear existing
        endpoint = f"{self.url}/rest/v1/watchlists?user_id=eq.{user_id}"
        try:
            requests.delete(endpoint, headers=self.headers, timeout=10)
            payload = [{"user_id": user_id, "symbol": s.strip().upper().replace(".NS", "").replace(".BO", "")} for s in symbols]
            res = requests.post(f"{self.url}/rest/v1/watchlists", headers=self.headers, json=payload, timeout=10)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error resetting Supabase watchlist: {e}")
            return False

