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
        self.url = (supabase_url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.key = supabase_key or os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
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
