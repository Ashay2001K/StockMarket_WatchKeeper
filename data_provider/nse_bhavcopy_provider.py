"""
NSE Bhavcopy Delivery Data Provider.
Downloads official daily public NSE bhavcopy / security delivery reports.
Features realistic browser session spoofing, memory-safe in-memory caching,
and resilient zero-crash fallback handling.
"""

import os
import io
import csv
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import requests

logger = logging.getLogger(__name__)


class NSEBhavcopyProvider:
    """
    Scrapes and caches daily NSE cash delivery percentages.
    Zero paid APIs. Graceful fallback on Cloudflare / network blocks.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive"
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._delivery_cache: Dict[str, float] = {}
        self._cache_date: Optional[str] = None
        self._init_session_cookies()

    def _init_session_cookies(self):
        """Visits NSE homepage to establish session cookies if possible."""
        try:
            self.session.get("https://www.nseindia.com", timeout=self.timeout)
        except Exception as e:
            logger.warning(f"NSE homepage cookie initialization bypassed: {e}")

    def fetch_daily_delivery_bhavcopy(self, date_str: Optional[str] = None) -> Dict[str, float]:
        """
        Downloads the full security bhavdata CSV for the target date.
        Date format: 'DDMMYYYY', e.g., '28032024'. Defaults to latest business day.
        Returns a dictionary: {SYMBOL: delivery_percentage}.
        """
        today = datetime.now()
        target_date = today if date_str is None else datetime.strptime(date_str, "%d%m%Y")
        
        # If weekend, rewind to Friday
        if target_date.weekday() == 5:  # Saturday
            target_date -= timedelta(days=1)
        elif target_date.weekday() == 6:  # Sunday
            target_date -= timedelta(days=2)

        formatted_date = target_date.strftime("%d%m%Y")
        
        # Return memory cache if already populated for this date
        if self._cache_date == formatted_date and self._delivery_cache:
            return self._delivery_cache

        # Public NSE bhavcopy archives URL pattern
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{formatted_date}.csv"

        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and len(response.content) > 1000:
                lines = response.content.decode("utf-8", errors="ignore").splitlines()
                reader = csv.DictReader(lines)
                
                cache: Dict[str, float] = {}
                for row in reader:
                    symbol = row.get("SYMBOL", "").strip().upper()
                    series = row.get("SERIES", "").strip().upper()
                    deliv_pct_str = row.get("DELIV_PER", "").strip()
                    
                    # Only focus on EQ series equities
                    if series == "EQ" and symbol and deliv_pct_str and deliv_pct_str != "-":
                        try:
                            cache[symbol] = float(deliv_pct_str)
                        except ValueError:
                            continue

                if cache:
                    self._delivery_cache = cache
                    self._cache_date = formatted_date
                    logger.info(f"Loaded delivery data for {len(cache)} symbols from NSE bhavcopy.")
                    return self._delivery_cache
            else:
                logger.warning(f"NSE Bhavcopy returned status {response.status_code} for {formatted_date}.")
        except Exception as e:
            logger.warning(f"Failed to download daily NSE delivery bhavcopy: {e}. Falling back gracefully.")

        return self._delivery_cache

    def get_symbol_delivery(self, symbol: str) -> Optional[float]:
        """
        Retrieves the delivery percentage for a specific NSE symbol.
        Returns None if delivery data is unavailable.
        """
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
        if not self._delivery_cache:
            self.fetch_daily_delivery_bhavcopy()
        
        return self._delivery_cache.get(clean_sym, None)
