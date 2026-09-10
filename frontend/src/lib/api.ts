/**
 * BEM 100 v2.0 - API Client.
 * Features cold-start handling and automatic retry for free Render/Fly.io backends.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface StockRecord {
  symbol: string;
  name?: string;
  sector?: string;
  date?: string;
  close_price: number;
  day_change_pct: number;
  bem_score: number;
  action: string;
  price_momentum_score: number;
  volume_expansion_score: number;
  delivery_score: number;
  breakout_score: number;
  institutional_score: number;
  exhaustion_adjustment: number;
  raw_exhaustion_score: number;
  chase_alert_active: boolean;
  chase_alert_severity?: string;
  chase_alert_reason?: string;
  chase_strategy?: string;
  potential_level: string;
  potential_probability_pct: number;
  potential_narrative?: string;
  preferred_buy_min: number;
  preferred_buy_max: number;
  breakout_entry: number;
  stop_loss: number;
  stop_loss_pct: number;
  target_1: number;
  target_1_pct: number;
  target_2: number;
  target_2_pct: number;
  stretch_target: number;
  stretch_target_pct: number;
  risk_reward_t1: number;
  risk_reward_t2: number;
  confidence: string;
  metadata?: any;
}

export interface ScreenerResponse {
  count: number;
  total_universe: number;
  results: StockRecord[];
}

export interface WatchlistItem {
  symbol: string;
  close_price: number;
  day_change_pct: number;
  current_bem: number;
  history_3d: number[];
  delta_1d: number;
  acceleration_tag: string;
  status_flag: string;
  action: string;
  chase_alert_active: boolean;
  potential_level: string;
  potential_probability_pct: number;
}

export interface MarketRegimeData {
  regime: "Risk-On" | "Risk-Off" | "Neutral";
  nifty_close: number;
  nifty_above_20_dma: boolean;
  nifty_above_50_dma: boolean;
  nifty_above_200_dma: boolean;
  india_vix: number;
  notes: string[];
}

export async function fetchHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchScreener(params: {
  min_bem?: number;
  max_exhaustion?: number;
  action?: string;
  potential?: string;
  no_chase_only?: boolean;
}): Promise<ScreenerResponse> {
  const query = new URLSearchParams();
  if (params.min_bem !== undefined) query.set("min_bem", params.min_bem.toString());
  if (params.max_exhaustion !== undefined) query.set("max_exhaustion", params.max_exhaustion.toString());
  if (params.action) query.set("action", params.action);
  if (params.potential) query.set("potential", params.potential);
  if (params.no_chase_only) query.set("no_chase_only", "true");

  const url = `${API_BASE}/api/v1/screener?${query.toString()}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load screener data");
  return res.json();
}

export async function fetchStock(ticker: string): Promise<StockRecord> {
  const url = `${API_BASE}/api/v1/stock/${ticker.toUpperCase()}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load analysis for ${ticker}`);
  const json = await res.json();
  return json.data;
}

export interface WatchlistApiResponse {
  count: number;
  symbols: string[];
  watchlist: WatchlistItem[];
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  const url = `${API_BASE}/api/v1/watchlist`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load watchlist");
  const json = await res.json();
  return json.watchlist || [];
}

export async function addToWatchlist(symbol: string, notes: string = ""): Promise<{ item: WatchlistItem; symbol: string }> {
  const url = `${API_BASE}/api/v1/watchlist`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, notes })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Failed to add ${symbol} to watchlist`);
  }
  return data;
}

export async function removeFromWatchlist(symbol: string): Promise<{ symbol: string }> {
  const url = `${API_BASE}/api/v1/watchlist/${encodeURIComponent(symbol)}`;
  const res = await fetch(url, { method: "DELETE" });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Failed to remove ${symbol} from watchlist`);
  }
  return data;
}

export async function resetWatchlist(): Promise<WatchlistItem[]> {
  const url = `${API_BASE}/api/v1/watchlist/reset`;
  const res = await fetch(url, { method: "POST" });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Failed to reset watchlist");
  }
  return data.watchlist || [];
}

export async function fetchMarketRegime(): Promise<MarketRegimeData> {
  const url = `${API_BASE}/api/v1/market-regime`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load market regime");
  return res.json();
}

export async function searchTickers(query: string): Promise<any[]> {
  if (!query) return [];
  const url = `${API_BASE}/api/v1/search?q=${encodeURIComponent(query)}`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const json = await res.json();
  return json.results || [];
}
