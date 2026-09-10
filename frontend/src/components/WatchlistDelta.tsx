"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { WatchlistItem, addToWatchlist, removeFromWatchlist, resetWatchlist } from "@/lib/api";
import {
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Plus,
  Trash2,
  Loader2,
  RotateCcw,
  Sparkles,
  Search
} from "lucide-react";

interface WatchlistDeltaProps {
  watchlist: WatchlistItem[];
  onWatchlistChange?: (items: WatchlistItem[]) => void;
}

export const WatchlistDelta: React.FC<WatchlistDeltaProps> = ({
  watchlist: initialWatchlist,
  onWatchlistChange
}) => {
  const [items, setItems] = useState<WatchlistItem[]>(initialWatchlist);
  const [inputTicker, setInputTicker] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const [deletingSymbol, setDeletingSymbol] = useState<string | null>(null);
  const [isResetting, setIsResetting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    setItems(initialWatchlist);
  }, [initialWatchlist]);

  const updateItems = (newItems: WatchlistItem[]) => {
    setItems(newItems);
    if (onWatchlistChange) {
      onWatchlistChange(newItems);
    }
  };

  const handleAddTicker = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanSym = inputTicker.trim().toUpperCase().replace(".NS", "").replace(".BO", "");
    if (!cleanSym) return;

    // Client-side quick check
    if (items.some((it) => it.symbol === cleanSym)) {
      setErrorMessage(`'${cleanSym}' is already in your watchlist.`);
      return;
    }

    setIsAdding(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const res = await addToWatchlist(cleanSym);
      const newItems = [res.item, ...items.filter((it) => it.symbol !== cleanSym)];
      updateItems(newItems);
      setInputTicker("");
      setSuccessMessage(`'${cleanSym}' added with live momentum metrics!`);
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (err: any) {
      setErrorMessage(err.message || `Failed to add ${cleanSym}.`);
    } finally {
      setIsAdding(false);
    }
  };

  const handleRemove = async (symbol: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    setDeletingSymbol(symbol);
    setErrorMessage(null);
    try {
      await removeFromWatchlist(symbol);
      const newItems = items.filter((it) => it.symbol !== symbol);
      updateItems(newItems);
    } catch (err: any) {
      setErrorMessage(err.message || `Failed to remove ${symbol}.`);
    } finally {
      setDeletingSymbol(null);
    }
  };

  const handleReset = async () => {
    setIsResetting(true);
    setErrorMessage(null);
    try {
      const defaultItems = await resetWatchlist();
      updateItems(defaultItems);
      setSuccessMessage("Watchlist restored to top 10 curated momentum stocks.");
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to reset watchlist.");
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Dynamic Add Stock Form */}
      <div className="glass-panel rounded-2xl p-3.5 space-y-2.5">
        <form onSubmit={handleAddTicker} className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={inputTicker}
              onChange={(e) => {
                setInputTicker(e.target.value.toUpperCase());
                if (errorMessage) setErrorMessage(null);
              }}
              disabled={isAdding}
              placeholder="Add stock (e.g. INFY, TCS, RELIANCE)..."
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/80 disabled:opacity-50 uppercase tracking-wider font-mono font-medium"
            />
          </div>
          <button
            type="submit"
            disabled={isAdding || !inputTicker.trim()}
            className="px-3.5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all shadow-md active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
          >
            {isAdding ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Plus className="w-3.5 h-3.5" />
                <span>Add</span>
              </>
            )}
          </button>
        </form>

        {/* In-Flight Async Feedback */}
        {isAdding && (
          <div className="flex items-center gap-2 px-1 text-[11px] text-emerald-400 animate-pulse font-medium">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Fetching live market OHLCV data & computing BEM metrics...</span>
          </div>
        )}

        {/* Error Feedback */}
        {errorMessage && (
          <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between animate-fadeIn">
            <div className="flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-rose-400 hover:text-white text-sm ml-2"
            >
              &times;
            </button>
          </div>
        )}

        {/* Success Feedback */}
        {successMessage && (
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-1.5 animate-fadeIn">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}
      </div>

      {/* Header Info Bar */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Daily Score Acceleration ({items.length})
          </h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px] text-slate-500 font-mono hidden sm:inline">
            T-2 ➔ T-1 ➔ Today
          </span>
          <button
            onClick={handleReset}
            disabled={isResetting}
            title="Reset to Top 10 Curated Momentum Stocks"
            className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-emerald-400 transition-colors font-medium disabled:opacity-50"
          >
            <RotateCcw className={`w-3 h-3 ${isResetting ? "animate-spin" : ""}`} />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Watchlist Cards */}
      {items.length === 0 ? (
        <div className="glass-panel rounded-2xl p-8 text-center space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-slate-900 flex items-center justify-center text-slate-500">
            <Sparkles className="w-6 h-6" />
          </div>
          <h4 className="text-sm font-bold text-white">Your Watchlist is Empty</h4>
          <p className="text-xs text-slate-400 max-w-xs mx-auto">
            Search and add any NSE stock above, or restore the default curated momentum list.
          </p>
          <button
            onClick={handleReset}
            disabled={isResetting}
            className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs inline-flex items-center gap-1.5 transition-all shadow-md"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
            <span>Restore Curated Top 10 Stocks</span>
          </button>
        </div>
      ) : (
        <div className="space-y-2.5">
          {items.map((item) => {
            const isAccelerating = item.delta_1d > 0;
            const isExhausted = item.chase_alert_active;
            const isDeleting = deletingSymbol === item.symbol;

            return (
              <div
                key={item.symbol}
                className="group relative block glass-panel rounded-2xl p-3.5 hover:border-emerald-500/50 active:scale-[0.99] transition-all"
              >
                <Link href={`/stock/${item.symbol}`} className="block">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-black text-white">{item.symbol}</span>
                        <span className="text-xs font-mono text-slate-400">₹{item.close_price}</span>
                        <span
                          className={`text-[11px] font-mono font-bold ${
                            item.day_change_pct >= 0 ? "text-emerald-400" : "text-rose-400"
                          }`}
                        >
                          {item.day_change_pct >= 0 ? "+" : ""}
                          {item.day_change_pct}%
                        </span>
                      </div>

                      {/* 3-day trajectory progression */}
                      <div className="flex items-center gap-1.5 mt-2 font-mono text-xs text-slate-300">
                        <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                          {item.history_3d?.[0] ?? "--"}
                        </span>
                        <ArrowRight className="w-3 h-3 text-slate-600" />
                        <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                          {item.history_3d?.[1] ?? "--"}
                        </span>
                        <ArrowRight className="w-3 h-3 text-slate-600" />
                        <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold">
                          {item.history_3d?.[2] ?? item.current_bem}
                        </span>
                        <span
                          className={`text-[11px] font-bold ml-1 ${
                            isAccelerating ? "text-emerald-400" : "text-slate-400"
                          }`}
                        >
                          ({isAccelerating ? "+" : ""}
                          {item.delta_1d})
                        </span>
                      </div>
                    </div>

                    <div className="text-right flex flex-col items-end gap-1.5">
                      <div className="flex items-center gap-1.5">
                        <div
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full border inline-flex items-center gap-1 ${
                            isExhausted
                              ? "bg-rose-500/10 border-rose-500/40 text-rose-300"
                              : item.status_flag === "Healthy Acceleration"
                              ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-400"
                              : "bg-cyan-500/10 border-cyan-500/40 text-cyan-300"
                          }`}
                        >
                          {isExhausted ? (
                            <AlertTriangle className="w-2.5 h-2.5" />
                          ) : (
                            <CheckCircle2 className="w-2.5 h-2.5" />
                          )}
                          {item.status_flag}
                        </div>

                        {/* Quick Remove Button */}
                        <button
                          onClick={(e) => handleRemove(item.symbol, e)}
                          disabled={isDeleting}
                          title={`Remove ${item.symbol} from watchlist`}
                          className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                        >
                          {isDeleting ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin text-rose-400" />
                          ) : (
                            <Trash2 className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>

                      <div className="text-xs font-bold text-white uppercase tracking-tight">
                        {item.action}
                      </div>
                    </div>
                  </div>
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
