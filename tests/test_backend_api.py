"""
Integration tests for FastAPI Backend endpoints.
Verifies /health, /stock, /screener, /watchlist, /market-regime, and /search.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["engine"] == "BEM 100 v2.0"
    assert data["memory_safe"] is True


def test_screener_endpoint():
    res = client.get("/api/v1/screener?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert len(data["results"]) > 0
    first = data["results"][0]
    assert "symbol" in first
    assert "bem_score" in first
    assert "action" in first
    assert "potential_probability_pct" in first


def test_screener_with_filters():
    res = client.get("/api/v1/screener?min_bem=75&max_exhaustion=5")
    assert res.status_code == 200
    data = res.json()
    for item in data["results"]:
        assert item["bem_score"] >= 75.0
        assert item["raw_exhaustion_score"] <= 5.0


def test_stock_endpoint_precomputed():
    res = client.get("/api/v1/stock/MCX")
    assert res.status_code == 200
    data = res.json()
    assert data["source"] in ["precomputed_db", "precomputed_cache"]
    stock_data = data["data"]
    assert stock_data["symbol"] == "MCX"
    assert "bem_score" in stock_data
    assert "trade_setup" in stock_data or "preferred_buy_min" in stock_data


def test_watchlist_endpoint():
    res = client.get("/api/v1/watchlist")
    assert res.status_code == 200
    data = res.json()
    assert "watchlist" in data
    assert len(data["watchlist"]) > 0
    first = data["watchlist"][0]
    assert "current_bem" in first
    assert "history_3d" in first
    assert "acceleration_tag" in first


def test_market_regime_endpoint():
    res = client.get("/api/v1/market-regime")
    assert res.status_code == 200
    data = res.json()
    assert "regime" in data
    assert data["regime"] in ["Risk-On", "Risk-Off", "Neutral"]
    assert "india_vix" in data


def test_search_endpoint():
    res = client.get("/api/v1/search?q=poly")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert any(r["symbol"] == "POLYCAB" for r in data["results"])
