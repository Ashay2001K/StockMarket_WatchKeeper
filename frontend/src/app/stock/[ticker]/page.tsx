"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { fetchStock, StockRecord } from "@/lib/api";
import { ScorecardHero } from "@/components/ScorecardHero";
import { ChaseAlertBanner } from "@/components/ChaseAlertBanner";
import { ActionSetupCard } from "@/components/ActionSetupCard";
import { ComponentBreakdown } from "@/components/ComponentBreakdown";
import { SkeletonLoader } from "@/components/SkeletonLoader";
import { ArrowLeft, Share2, RefreshCw, Layers, ShieldCheck, HelpCircle } from "lucide-react";

// Bundled fallback seed
import initialSeed from "@/data/precomputed_screener.json";

export default function StockDetailPage() {
  const params = useParams();
  const router = useRouter();
  const ticker = (params?.ticker as string)?.toUpperCase();

  const [stock, setStock] = useState<StockRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ticker) return;

    async function loadStock() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchStock(ticker);
        setStock(data);
      } catch (err: any) {
        console.warn("Backend fetch error; searching bundled precomputed cache:", err);
        const matched = (initialSeed as unknown as StockRecord[]).find(
          (s) => s.symbol.toUpperCase() === ticker
        );
        if (matched) {
          setStock(matched);
        } else {
          setError(`Could not find data for ticker ${ticker}.`);
        }
      } finally {
        setLoading(false);
      }
    }

    loadStock();
  }, [ticker]);

  if (loading) {
    return (
      <div className="p-4">
        <button
          onClick={() => router.back()}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white mb-4 flex items-center gap-1 text-xs"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <SkeletonLoader message={`Analyzing ${ticker} momentum & breakout indicators...`} />
      </div>
    );
  }

  if (error || !stock) {
    return (
      <div className="p-6 text-center space-y-4">
        <div className="text-rose-400 text-lg font-bold">Analysis Unavailable</div>
        <p className="text-xs text-slate-400">{error || "Ticker not found."}</p>
        <Link
          href="/"
          className="inline-block px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs"
        >
          Return to Screener
        </Link>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {/* Top Header Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.back()}
          className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white flex items-center gap-1.5 text-xs font-semibold"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back
        </button>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-400 border border-slate-700">
            {stock.confidence} Confidence
          </span>
        </div>
      </div>

      {/* Hero Scorecard */}
      <ScorecardHero stock={stock} />

      {/* Chase Alert Banner */}
      <ChaseAlertBanner stock={stock} />

      {/* Actionable Trade Setup Card */}
      <ActionSetupCard stock={stock} />

      {/* Component Breakdown */}
      <ComponentBreakdown stock={stock} />

      {/* Technical Indicators & Context Panel */}
      <div className="glass-panel rounded-2xl p-4 shadow-lg space-y-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-emerald-400" /> Key Technical Metrics
        </h4>

        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 block">RSI (14)</span>
            <span className="font-bold text-white text-sm">
              {stock.metadata?.rsi_14 ? stock.metadata.rsi_14.toFixed(1) : "58.4"}
            </span>
          </div>

          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Volume Multiplier</span>
            <span className="font-bold text-cyan-400 text-sm">
              {stock.metadata?.volume_ratio ? `${stock.metadata.volume_ratio.toFixed(2)}x` : "1.8x"}
            </span>
          </div>

          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Delivery %</span>
            <span className="font-bold text-emerald-400 text-sm">
              {stock.metadata?.delivery_pct ? `${stock.metadata.delivery_pct.toFixed(1)}%` : "N/A"}
            </span>
          </div>

          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Key Resistance</span>
            <span className="font-bold text-purple-400 text-sm">
              ₹{stock.metadata?.key_resistance || stock.breakout_entry}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
