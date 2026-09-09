"use client";

import React from "react";
import { Zap, ShieldAlert, Sparkles, TrendingUp, TrendingDown, Target } from "lucide-react";
import { StockRecord } from "@/lib/api";

interface ScorecardHeroProps {
  stock: StockRecord;
}

export const ScorecardHero: React.FC<ScorecardHeroProps> = ({ stock }) => {
  const isBullish = stock.day_change_pct >= 0;
  
  // Score badge color based on BEM score
  let scoreBadgeStyle = "from-emerald-500/20 to-teal-500/10 border-emerald-500/40 text-emerald-400";
  let scoreGlow = "glow-emerald";
  let emoji = "🔥";
  
  if (stock.bem_score < 50) {
    scoreBadgeStyle = "from-rose-500/20 to-red-500/10 border-rose-500/40 text-rose-400";
    scoreGlow = "glow-rose";
    emoji = "⚠️";
  } else if (stock.bem_score < 70) {
    scoreBadgeStyle = "from-amber-500/20 to-yellow-500/10 border-amber-500/40 text-amber-400";
    scoreGlow = "glow-amber";
    emoji = "👀";
  }

  // Potential badge styling
  let potBadge = "bg-emerald-500/15 border-emerald-500/30 text-emerald-400";
  if (stock.potential_level === "Low") {
    potBadge = "bg-rose-500/15 border-rose-500/30 text-rose-400";
  } else if (stock.potential_level === "Medium") {
    potBadge = "bg-cyan-500/15 border-cyan-500/30 text-cyan-400";
  }

  return (
    <div className="w-full space-y-4">
      {/* Top Ticker & Price Bar */}
      <div className="glass-panel rounded-2xl p-4 flex items-center justify-between shadow-lg">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black tracking-tight text-white">{stock.symbol}</h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              NSE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            {stock.name || "Indian Equity Momentum"}
          </p>
        </div>

        <div className="text-right">
          <div className="text-2xl font-bold font-mono text-slate-100">
            ₹{stock.close_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <div className={`text-xs font-semibold flex items-center justify-end gap-0.5 ${isBullish ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isBullish ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            {isBullish ? '+' : ''}{stock.day_change_pct.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Main Scorecard Badge Hero */}
      <div className={`relative overflow-hidden rounded-3xl p-5 bg-gradient-to-br ${scoreBadgeStyle} border ${scoreGlow} transition-all`}>
        <div className="flex flex-col xs:flex-row items-center justify-between gap-4">
          {/* Big Score Radial/Box */}
          <div className="flex items-center gap-4">
            <div className="relative flex items-center justify-center w-20 h-20 rounded-2xl bg-slate-900/90 border border-slate-700/60 shadow-inner">
              <span className="text-3xl font-black tracking-tighter text-white">
                {Math.round(stock.bem_score)}
              </span>
              <span className="text-[10px] font-bold text-slate-400 absolute bottom-1.5">
                /100
              </span>
            </div>

            <div>
              <div className="text-[11px] uppercase tracking-wider font-bold text-slate-400 flex items-center gap-1">
                <Zap className="w-3 h-3 text-emerald-400" /> BEM 100 Score
              </div>
              <div className="text-xl font-black tracking-tight text-white flex items-center gap-1.5 mt-0.5">
                <span>{emoji}</span> {stock.action.toUpperCase()}
              </div>
              <div className="text-xs text-slate-300/80 mt-1">
                Confidence: <span className="font-semibold text-white">{stock.confidence}</span>
              </div>
            </div>
          </div>

          {/* 10%+ 2-Week Potential Pill */}
          <div className={`px-4 py-2.5 rounded-2xl border ${potBadge} flex flex-col items-end text-right self-stretch xs:self-auto justify-center`}>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1">
              <Target className="w-3 h-3" /> 10%+ 2-Wk Potential
            </span>
            <span className="text-sm font-black text-white mt-0.5">
              {stock.potential_probability_pct}% ({stock.potential_level})
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
