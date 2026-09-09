"""
Ticker Search & Auto-Suggest Endpoint.
Fast autocomplete for NSE/BSE tickers on mobile search input.
"""

from typing import List, Dict
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/search", tags=["Search"])

TICKER_DIRECTORY: List[Dict[str, str]] = [
    {"symbol": "MCX", "name": "Multi Commodity Exchange of India", "sector": "Financial Services"},
    {"symbol": "POLYCAB", "name": "Polycab India Limited", "sector": "Capital Goods / Cables"},
    {"symbol": "APARINDS", "name": "Apar Industries Limited", "sector": "Capital Goods / Conductors"},
    {"symbol": "TDPOWERSYS", "name": "TD Power Systems Limited", "sector": "Heavy Electrical Equipment"},
    {"symbol": "TRENT", "name": "Trent Limited", "sector": "Retail / Consumer"},
    {"symbol": "HAL", "name": "Hindustan Aeronautics Limited", "sector": "Aerospace & Defense"},
    {"symbol": "BEL", "name": "Bharat Electronics Limited", "sector": "Aerospace & Defense"},
    {"symbol": "BHEL", "name": "Bharat Heavy Electricals Limited", "sector": "Heavy Electrical"},
    {"symbol": "DIXON", "name": "Dixon Technologies (India) Ltd", "sector": "Electronics Manufacturing"},
    {"symbol": "KAYNES", "name": "Kaynes Technology India Ltd", "sector": "Electronics Manufacturing"},
    {"symbol": "CDSL", "name": "Central Depository Services (India)", "sector": "Capital Markets"},
    {"symbol": "BSE", "name": "BSE Limited", "sector": "Capital Markets"},
    {"symbol": "MAZDOCK", "name": "Mazagon Dock Shipbuilders Ltd", "sector": "Defense / Shipbuilding"},
    {"symbol": "COCHINSHIP", "name": "Cochin Shipyard Limited", "sector": "Defense / Shipbuilding"},
    {"symbol": "RVNL", "name": "Rail Vikas Nigam Limited", "sector": "Railways Infrastructure"},
    {"symbol": "IREDA", "name": "Indian Renewable Energy Dev Agency", "sector": "Green Energy Finance"},
    {"symbol": "ZOMATO", "name": "Zomato Limited", "sector": "Internet / Food Delivery"},
    {"symbol": "SUZLON", "name": "Suzlon Energy Limited", "sector": "Renewable Energy"},
    {"symbol": "TATACHEM", "name": "Tata Chemicals Limited", "sector": "Chemicals"},
    {"symbol": "RELIANCE", "name": "Reliance Industries Limited", "sector": "Conglomerate / Energy"},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "Information Technology"},
    {"symbol": "INFY", "name": "Infosys Limited", "sector": "Information Technology"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Limited", "sector": "Private Banking"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Limited", "sector": "Private Banking"},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Public Sector Banking"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Limited", "sector": "Telecom Services"},
    {"symbol": "ITC", "name": "ITC Limited", "sector": "Consumer Goods / Diversified"},
    {"symbol": "LT", "name": "Larsen & Toubro Limited", "sector": "Infrastructure / EPC"},
    {"symbol": "TITAN", "name": "Titan Company Limited", "sector": "Consumer Discretionary"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors Limited", "sector": "Automobiles / EV"},
]


@router.get("")
async def search_tickers(q: str = Query("", min_length=1)):
    """Auto-suggest search matching symbol prefix or company name."""
    query = q.strip().upper()
    matches = []
    for item in TICKER_DIRECTORY:
        if query in item["symbol"] or query in item["name"].upper():
            matches.append(item)

    # If query is a custom ticker not in directory, append it as a direct candidate
    if not any(item["symbol"] == query for item in matches):
        matches.insert(0, {
            "symbol": query,
            "name": f"{query} (NSE/BSE)",
            "sector": "Equity"
        })

    return {"query": q, "results": matches[:8]}
