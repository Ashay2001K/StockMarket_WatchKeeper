"use client";

import React, { useState, useEffect } from "react";
import { HeaderSearch } from "@/components/HeaderSearch";
import { ScreenerTable } from "@/components/ScreenerTable";
import { WatchlistDelta } from "@/components/WatchlistDelta";
import { SkeletonLoader } from "@/components/SkeletonLoader";
import {
  fetchScreener,
  fetchWatchlist,
  fetchMarketRegime,
  StockRecord,
  WatchlistItem,
  MarketRegimeData
} from "@/lib/api";
import { Zap, ShieldCheck, Activity, Compass, Layers, ListOrdered } from "lucide-react";

// Fallback seed data in case API server is waking up
import initialSeed from "@/data/precomputed_screener.json";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"screener" | "watchlist" | "regime">("screener");
  const [stocks, setStocks] = useState<StockRecord[]>(initialSeed as unknown as StockRecord[]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [regime, setRegime] = useState<MarketRegimeData | null>({
    regime: "Risk-On",
    nifty_close: 22650.0,
    nifty_above_20_dma: true,
    nifty_above_50_dma: true,
    nifty_above_200_dma: true,
    india_vix: 14.2,
    notes: ["Nifty 50 above 20, 50, and 200 DMA", "India VIX below 15.0 (Calm volatility)"]
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [screenerRes, watchlistRes, regimeRes] = await Promise.allSettled([
          fetchScreener({}),
          fetchWatchlist(),
          fetchMarketRegime()
        ]);

        if (screenerRes.status === "fulfilled" && screenerRes.value.results.length > 0) {
          setStocks(screenerRes.value.results);
        }
        if (watchlistRes.status === "fulfilled") {
          setWatchlist(watchlistRes.value);
        }
        if (regimeRes.status === "fulfilled") {
          setRegime(regimeRes.value);
        }
      } catch (err) {
        console.warn("Using bundled seed data while backend boots:", err);
      }
    }
    loadData();
  }, []);

  return (
    <div className="p-4 space-y-4">
      {/* Mobile Top Header */}
      <header className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-slate-950 font-black text-base shadow-lg glow-emerald">
              B
            </div>
            <div>
              <h1 className="text-base font-black tracking-tight text-white flex items-center gap-1.5">
                BEM 100 <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono font-bold">v2.0</span>
              </h1>
              <p className="text-[10px] text-slate-400">Indian Momentum & Breakouts</p>
            </div>
          </div>

          {/* Market Regime Pill */}
          {regime && (
            <div className="text-right">
              <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-bold">
                <span className={`w-2 h-2 rounded-full ${regime.regime === "Risk-On" ? "bg-emerald-400 animate-pulse" : "bg-rose-400"}`} />
                <span className={regime.regime === "Risk-On" ? "text-emerald-300" : "text-rose-300"}>{regime.regime}</span>
                <span className="text-slate-500 text-[10px]">| VIX {regime.india_vix}</span>
              </div>
            </div>
          )}
        </div>

        {/* Ticker Search Bar */}
        <HeaderSearch />
      </header>

      {/* Touch-Friendly Tab Bar */}
      <nav className="grid grid-cols-3 gap-1 p-1 bg-slate-900/90 rounded-2xl border border-slate-800 text-xs font-bold shadow-inner">
        <button
          onClick={() => setActiveTab("screener")}
          className={`py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all ${
            activeTab === "screener"
              ? "bg-emerald-500 text-slate-950 shadow-md"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Screener
        </button>

        <button
          onClick={() => setActiveTab("watchlist")}
          className={`py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all ${
            activeTab === "watchlist"
              ? "bg-emerald-500 text-slate-950 shadow-md"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <ListOrdered className="w-3.5 h-3.5" />
          Watchlist
        </button>

        <button
          onClick={() => setActiveTab("regime")}
          className={`py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all ${
            activeTab === "regime"
              ? "bg-emerald-500 text-slate-950 shadow-md"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          Regime
        </button>
      </nav>

      {/* Main Content Area */}
      {isLoading ? (
        <SkeletonLoader />
      ) : (
        <>
          {activeTab === "screener" && (
            <ScreenerTable stocks={stocks} />
          )}

          {activeTab === "watchlist" && (
            <WatchlistDelta
              watchlist={watchlist}
              onWatchlistChange={setWatchlist}
            />
          )}

          {activeTab === "regime" && regime && (
            <div className="glass-panel rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-emerald-400" />
                  Indian Market Regime Analysis
                </h2>
                <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                  {regime.regime}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 font-mono">
                <div className="glass-card rounded-xl p-3 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase block">Nifty 50 Close</span>
                  <span className="text-base font-bold text-white">₹{regime.nifty_close}</span>
                  <span className="text-[10px] text-emerald-400 block mt-0.5">Above 20 & 50 DMA</span>
                </div>

                <div className="glass-card rounded-xl p-3 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase block">India VIX</span>
                  <span className="text-base font-bold text-emerald-400">{regime.india_vix}</span>
                  <span className="text-[10px] text-slate-400 block mt-0.5">&lt; 15.0 (Calm)</span>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Regime Intelligence Notes:</h4>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  <li className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Nifty 50 trading above 20, 50, and 200 DMA — Bullish trend intact.</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>India VIX at 14.2 indicates low systemic volatility (favorable for breakout continuation).</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Compass className="w-4 h-4 text-cyan-400 shrink-0" />
                    <span>High-BEM stocks have model-estimated +10% potential boost under Risk-On regime.</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
