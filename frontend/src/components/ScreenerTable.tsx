"use client";

import React, { useState } from "react";
import Link from "next/link";
import { StockRecord } from "@/lib/api";
import { Filter, ChevronRight, AlertTriangle, Sparkles, TrendingUp, TrendingDown, Target } from "lucide-react";

interface ScreenerTableProps {
  stocks: StockRecord[];
  onFilterChange?: (filters: any) => void;
}

export const ScreenerTable: React.FC<ScreenerTableProps> = ({ stocks }) => {
  const [minBem, setMinBem] = useState(0);
  const [maxExhaustion, setMaxExhaustion] = useState(15);
  const [actionFilter, setActionFilter] = useState("all");
  const [noChaseOnly, setNoChaseOnly] = useState(false);

  // Client-side filtering for immediate snappy responsiveness
  const filtered = stocks.filter((s) => {
    if (s.bem_score < minBem) return false;
    if (s.raw_exhaustion_score > maxExhaustion) return false;
    if (actionFilter !== "all" && s.action.toLowerCase() !== actionFilter.toLowerCase()) return false;
    if (noChaseOnly && s.chase_alert_active) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Mobile Filter Bar */}
      <div className="glass-panel rounded-2xl p-3.5 space-y-3">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
          <span className="flex items-center gap-1.5 text-slate-100">
            <Filter className="w-3.5 h-3.5 text-emerald-400" /> Screener Filters
          </span>
          <span className="text-[11px] text-slate-400 font-mono">
            {filtered.length} of {stocks.length} matches
          </span>
        </div>

        {/* Quick Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <button
            onClick={() => { setMinBem(0); setActionFilter("all"); setNoChaseOnly(false); }}
            className={`px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-colors ${
              minBem === 0 && actionFilter === "all" && !noChaseOnly
                ? "bg-emerald-500 text-slate-950 font-bold"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            All Stocks
          </button>
          <button
            onClick={() => { setMinBem(75); setActionFilter("all"); }}
            className={`px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-colors ${
              minBem === 75
                ? "bg-emerald-500 text-slate-950 font-bold"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            BEM ≥ 75
          </button>
          <button
            onClick={() => setNoChaseOnly(!noChaseOnly)}
            className={`px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-colors ${
              noChaseOnly
                ? "bg-amber-500 text-slate-950 font-bold"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            Exclude Chase Risk
          </button>
          <button
            onClick={() => setActionFilter(actionFilter === "Strong Buy" ? "all" : "Strong Buy")}
            className={`px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-colors ${
              actionFilter === "Strong Buy"
                ? "bg-emerald-500 text-slate-950 font-bold"
                : "bg-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            Strong Buy
          </button>
        </div>

        {/* Slider controls */}
        <div className="grid grid-cols-2 gap-3 pt-1 border-t border-slate-800/80 text-[11px]">
          <div>
            <div className="flex justify-between text-slate-400 mb-1">
              <span>Min BEM Score:</span>
              <span className="font-bold text-white font-mono">{minBem}</span>
            </div>
            <input
              type="range"
              min="0"
              max="90"
              step="5"
              value={minBem}
              onChange={(e) => setMinBem(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-slate-400 mb-1">
              <span>Max Exhaustion:</span>
              <span className="font-bold text-white font-mono">{maxExhaustion}</span>
            </div>
            <input
              type="range"
              min="2"
              max="15"
              step="1"
              value={maxExhaustion}
              onChange={(e) => setMaxExhaustion(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>
        </div>
      </div>

      {/* Stock Cards List */}
      <div className="space-y-2.5">
        {filtered.map((stock) => {
          const isBullish = stock.day_change_pct >= 0;
          return (
            <Link
              key={stock.symbol}
              href={`/stock/${stock.symbol}`}
              className="block glass-panel rounded-2xl p-3.5 hover:border-emerald-500/50 active:scale-[0.99] transition-all"
            >
              <div className="flex items-center justify-between">
                {/* Left: Ticker & Sector */}
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center font-bold text-white font-mono shadow-inner">
                    <span className="text-sm font-black text-emerald-400">{Math.round(stock.bem_score)}</span>
                    <span className="text-[8px] text-slate-500 uppercase tracking-tighter">BEM</span>
                  </div>

                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-black text-white">{stock.symbol}</span>
                      {stock.chase_alert_active && (
                        <span className="px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 text-[9px] font-bold border border-rose-500/40 flex items-center gap-0.5">
                          <AlertTriangle className="w-2.5 h-2.5" /> CHASE
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-slate-400 truncate max-w-[140px] xs:max-w-[180px]">
                      {stock.name || stock.sector || "NSE Equity"}
                    </div>
                  </div>
                </div>

                {/* Right: Price, Change, Action */}
                <div className="text-right flex items-center gap-2.5">
                  <div>
                    <div className="text-xs font-bold font-mono text-white">
                      ₹{stock.close_price.toLocaleString("en-IN", { minimumFractionDigits: 1 })}
                    </div>
                    <div className={`text-[10px] font-semibold flex items-center justify-end ${isBullish ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {isBullish ? '+' : ''}{stock.day_change_pct.toFixed(2)}%
                    </div>
                    <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-tight mt-0.5">
                      {stock.action}
                    </div>
                  </div>

                  <ChevronRight className="w-4 h-4 text-slate-500" />
                </div>
              </div>

              {/* Component Mini Badges Footer */}
              <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>Mom: <strong className="text-slate-200">{stock.price_momentum_score.toFixed(0)}</strong>/25</span>
                <span>Vol: <strong className="text-slate-200">{stock.volume_expansion_score.toFixed(0)}</strong>/20</span>
                <span>Del: <strong className="text-slate-200">{stock.delivery_score.toFixed(0)}</strong>/15</span>
                <span>Pot: <strong className="text-emerald-400">{stock.potential_probability_pct}%</strong></span>
              </div>
            </Link>
          );
        })}

        {filtered.length === 0 && (
          <div className="text-center p-8 glass-card rounded-2xl border border-slate-800 text-slate-400 text-sm">
            No stocks matched the selected criteria. Try adjusting the BEM or Exhaustion thresholds.
          </div>
        )}
      </div>
    </div>
  );
};
