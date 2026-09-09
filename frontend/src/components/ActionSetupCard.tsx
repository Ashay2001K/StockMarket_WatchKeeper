"use client";

import React from "react";
import { StockRecord } from "@/lib/api";
import { Crosshair, Shield, TrendingUp, Target, Scale, HelpCircle } from "lucide-react";

interface ActionSetupCardProps {
  stock: StockRecord;
}

export const ActionSetupCard: React.FC<ActionSetupCardProps> = ({ stock }) => {
  return (
    <div className="glass-panel rounded-2xl p-4 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
            <Crosshair className="w-4 h-4 text-emerald-400" />
            Actionable Trade Setup
          </h3>
        </div>
        <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
          {stock.action}
        </span>
      </div>

      {/* Rationale Quote */}
      {stock.metadata?.rationale && (
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 text-xs text-slate-300 italic">
          "{stock.metadata.rationale}"
        </div>
      )}

      {/* Levels Grid */}
      <div className="grid grid-cols-2 gap-2.5">
        {/* Buy Zone */}
        <div className="glass-card rounded-xl p-3 border border-slate-800">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
            <Target className="w-3 h-3 text-cyan-400" /> Preferred Buy Zone
          </div>
          <div className="text-sm font-bold font-mono text-cyan-300 mt-1">
            ₹{stock.preferred_buy_min} – ₹{stock.preferred_buy_max}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Near 20 DMA support</div>
        </div>

        {/* Breakout Entry */}
        <div className="glass-card rounded-xl p-3 border border-slate-800">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-emerald-400" /> Breakout Entry
          </div>
          <div className="text-sm font-bold font-mono text-emerald-400 mt-1">
            ₹{stock.breakout_entry}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Confirmed resistance close</div>
        </div>

        {/* Stop Loss */}
        <div className="glass-card rounded-xl p-3 border border-slate-800">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
            <Shield className="w-3 h-3 text-rose-400" /> ATR / Swing Stop Loss
          </div>
          <div className="text-sm font-bold font-mono text-rose-400 mt-1">
            ₹{stock.stop_loss}
          </div>
          <div className="text-[10px] text-rose-300/80 mt-0.5">
            Risk: -{stock.stop_loss_pct}% (strictly non-arbitrary)
          </div>
        </div>

        {/* Risk / Reward */}
        <div className="glass-card rounded-xl p-3 border border-slate-800">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
            <Scale className="w-3 h-3 text-amber-400" /> Risk / Reward Ratio
          </div>
          <div className="text-sm font-bold font-mono text-amber-300 mt-1">
            1 : {stock.risk_reward_t2}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Target 2 R:R (prefer ≥ 2.0)</div>
        </div>
      </div>

      {/* Target Tiers */}
      <div className="glass-card rounded-xl p-3 border border-slate-800 space-y-2">
        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Multi-Tier Targets (ATR Multiples)
        </div>
        <div className="grid grid-cols-3 gap-2 text-center font-mono">
          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">T1 (+1.5 ATR)</span>
            <span className="text-xs font-bold text-white">₹{stock.target_1}</span>
            <span className="text-[10px] text-emerald-400 block">+{stock.target_1_pct}%</span>
          </div>
          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">T2 (+3.0 ATR)</span>
            <span className="text-xs font-bold text-emerald-300">₹{stock.target_2}</span>
            <span className="text-[10px] text-emerald-400 block">+{stock.target_2_pct}%</span>
          </div>
          <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Stretch (+5 ATR)</span>
            <span className="text-xs font-bold text-purple-300">₹{stock.stretch_target}</span>
            <span className="text-[10px] text-purple-400 block">+{stock.stretch_target_pct}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
